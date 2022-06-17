#
#   Copyright 2022 Logical Clocks AB
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

import time
import uuid
import os

from tqdm.auto import tqdm

from hsml import util

from hsml.constants import DEPLOYMENT, PREDICTOR, PREDICTOR_STATE
from hsml.core import serving_api, dataset_api

from hsml.client.exceptions import ModelServingException, RestAPIError


class ServingEngine:
    def __init__(self):
        self._serving_api = serving_api.ServingApi()
        self._dataset_api = dataset_api.DatasetApi()

    def _poll_deployment_status(
        self, deployment_instance, status: str, await_status: int, update_progress=None
    ):
        if await_status > 0:
            sleep_seconds = 5
            for _ in range(int(await_status / sleep_seconds)):
                time.sleep(sleep_seconds)
                state = deployment_instance.get_state()
                # num available instances
                num_instances = state.available_predictor_instances
                if state.available_transformer_instances is not None:
                    num_instances += state.available_transformer_instances
                if status == PREDICTOR_STATE.STATUS_STOPPED:
                    num_instances = (  # if stopping, return num stopped instances
                        deployment_instance.requested_instances - num_instances
                    )
                # update progress bar
                if update_progress is not None:
                    update_progress(num_instances)
                if state.status.upper() == status:
                    return state  # deployment reached desired status
            raise ModelServingException(
                "Deployment has not reached the desired status within the expected awaiting time. Check the current status by using `.get_state()`, "
                + "explore the server logs using `.get_logs()` or set a higher value for await_"
                + status.lower()
            )

    def start(self, deployment_instance, await_status: int) -> bool:
        (done, status) = self._check_status(
            deployment_instance, PREDICTOR_STATE.STATUS_RUNNING
        )
        if not done:
            pbar = tqdm(total=deployment_instance.requested_instances)
            pbar.set_description("Starting deployment")

            def update_progress(num_instances=0):
                pbar.update(num_instances - pbar.n)

            try:
                update_progress()
                self._serving_api.post(
                    deployment_instance, DEPLOYMENT.ACTION_START
                )  # start deployment

                state = self._poll_deployment_status(  # wait for status
                    deployment_instance,
                    PREDICTOR_STATE.STATUS_RUNNING,
                    await_status,
                    update_progress,
                )
                if state is not None:
                    status = state.status.upper()
                    if status == PREDICTOR_STATE.STATUS_RUNNING:
                        pbar.set_description("Deployment is running")
            except RestAPIError as re:
                self.stop(deployment_instance, await_status=0)
                raise re

        if status == PREDICTOR_STATE.STATUS_RUNNING:
            print("Start making predictions by using `.predict()`")

    def stop(self, deployment_instance, await_status: int) -> bool:
        (done, _) = self._check_status(
            deployment_instance, PREDICTOR_STATE.STATUS_STOPPED
        )
        if not done:
            pbar = tqdm(total=deployment_instance.requested_instances)
            pbar.set_description("Stopping deployment")

            def update_progress(num_instances=0):
                pbar.update(num_instances - pbar.n)
                if num_instances == deployment_instance.requested_instances:
                    pbar.set_description("Waiting for the instances to terminate")

            update_progress()
            self._serving_api.post(
                deployment_instance, DEPLOYMENT.ACTION_STOP
            )  # stop deployment

            state = self._poll_deployment_status(  # wait for status
                deployment_instance,
                PREDICTOR_STATE.STATUS_STOPPED,
                await_status,
                update_progress,
            )
            if (
                state is not None
                and state.status.upper() == PREDICTOR_STATE.STATUS_STOPPED
            ):
                pbar.set_description("Deployment is stopped")

    def predict(self, deployment_instance, data: dict):
        serving_tool = deployment_instance.predictor.serving_tool
        through_hopsworks = (
            serving_tool != PREDICTOR.SERVING_TOOL_KSERVE
        )  # if not KServe, send request to Hopsworks
        try:
            return self._serving_api.send_inference_request(
                deployment_instance, data, through_hopsworks
            )
        except RestAPIError as re:
            if (
                re.response.status_code == RestAPIError.STATUS_CODE_NOT_FOUND
                or re.error_code
                == ModelServingException.ERROR_CODE_DEPLOYMENT_NOT_RUNNING
            ):
                raise ModelServingException(
                    "Deployment not created or running. If it is already created, start it by using `.start()` or check its status with .get_state()"
                )

            re.args = (
                re.args[0] + "\n\n Check the model server logs by using `.get_logs()`",
            )
            raise re

    def _check_status(self, deployment_instance, desired_status):
        state = deployment_instance.get_state()
        if state is None:
            return (True, None)

        status = state.status.upper()

        # desired status: running
        if desired_status == PREDICTOR_STATE.STATUS_RUNNING:
            if (
                status == PREDICTOR_STATE.STATUS_STARTING
                or status == PREDICTOR_STATE.STATUS_RUNNING
            ):
                print("Deployment is already " + status.lower())
                return (True, status)
            if status == PREDICTOR_STATE.STATUS_UPDATING:
                print("Deployment is already running and updating")
                return (True, status)
            if status == PREDICTOR_STATE.STATUS_STOPPING:
                raise ModelServingException(
                    "Deployment is stopping, please wait until it completely stops"
                )

        # desired status: stopped
        if desired_status == PREDICTOR_STATE.STATUS_STOPPED:
            if (
                status == PREDICTOR_STATE.STATUS_STOPPED
                or status == PREDICTOR_STATE.STATUS_STOPPING
            ):
                print("Deployment is already " + status.lower())
                return (True, status)

        return (False, status)

    def download_artifact(self, deployment_instance):
        if deployment_instance.id is None:
            raise ModelServingException(
                "Deployment is not created yet. To create the deployment use `.save()`"
            )
        if deployment_instance.artifact_version is None:
            # model artifacts are not created in non-k8s installations
            raise ModelServingException(
                "Model artifacts not supported in non-k8s installations. \
                 Download the model files by using `model.download()`"
            )

        from_artifact_zip_path = deployment_instance.artifact_path
        to_artifacts_path = os.path.join(
            os.getcwd(),
            str(uuid.uuid4()),
            deployment_instance.model_name,
            str(deployment_instance.model_version),
            "Artifacts",
        )
        to_artifact_version_path = (
            to_artifacts_path + "/" + str(deployment_instance.artifact_version)
        )
        to_artifact_zip_path = to_artifact_version_path + ".zip"

        os.makedirs(to_artifacts_path)

        try:
            self._dataset_api.download(from_artifact_zip_path, to_artifact_zip_path)
            util.decompress(to_artifact_zip_path, extract_dir=to_artifacts_path)
            os.remove(to_artifact_zip_path)
        except BaseException as be:
            raise be
        finally:
            if os.path.exists(to_artifact_zip_path):
                os.remove(to_artifact_zip_path)

        return to_artifact_version_path

    def save(self, deployment_instance, await_update: int):
        if deployment_instance.id is None:
            # if new deployment
            self._serving_api.put(deployment_instance)
            print("Deployment created, explore it at " + deployment_instance.get_url())
            print("Before making predictions, start the deployment by using `.start()`")
            return

        # if existing deployment
        state = deployment_instance.get_state()
        if state is None:
            return

        status = state.status.upper()
        if status == PREDICTOR_STATE.STATUS_STARTING:
            # if starting, it cannot be updated yet
            raise ModelServingException(
                "Deployment is starting, please wait until it is running before applying changes. \n"
                + "Check the current status by using `.get_state()` or explore the server logs using `.get_logs()`"
            )
        if status == PREDICTOR_STATE.STATUS_RUNNING:
            # if running, it's fine
            self._serving_api.put(deployment_instance)
            print("Deployment updated, applying changes to running instances...")
            state = self._poll_deployment_status(  # wait for status
                deployment_instance, PREDICTOR_STATE.STATUS_RUNNING, await_update
            )
            if state is not None:
                if state.status.upper() == PREDICTOR_STATE.STATUS_RUNNING:
                    print("Running instances updated successfully")
            return
        if status == PREDICTOR_STATE.STATUS_UPDATING:
            # if updating, it cannot be updated yet
            raise ModelServingException(
                "Deployment is updating, please wait until it is running before applying changes. \n"
                + "Check the current status by using `.get_state()` or explore the server logs using `.get_logs()`"
            )
            return
        if status == PREDICTOR_STATE.STATUS_STOPPING:
            # if stopping, it cannot be updated yet
            raise ModelServingException(
                "Deployment is stopping, please wait until it is stopped before applying changes"
            )
            return
        if status == PREDICTOR_STATE.STATUS_STOPPED:
            # if stopped, it's fine
            self._serving_api.put(deployment_instance)
            print("Deployment updated, explore it at " + deployment_instance.get_url())
            return

        raise ValueError("Unknown deployment status: " + status)

    def delete(self, deployment_instance, force=False):
        state = deployment_instance.get_state()
        if state is None:
            return

        status = state.status.upper()
        if not force and status != PREDICTOR_STATE.STATUS_STOPPED:
            raise ModelServingException(
                "Deployment not stopped, please stop it first by using `.stop()` or check its status with .get_state()"
            )

        self._serving_api.delete(deployment_instance)
        print("Deployment deleted successfully")

    def get_state(self, deployment_instance):
        try:
            state = self._serving_api.get_state(deployment_instance)
        except RestAPIError as re:
            if re.error_code == ModelServingException.ERROR_CODE_SERVING_NOT_FOUND:
                raise ModelServingException("Deployment not found")
            raise re
        deployment_instance._predictor._set_state(state)
        return state

    def get_logs(self, deployment_instance, component, tail):
        state = self.get_state(deployment_instance)
        if state is None:
            return

        status = state.status.upper()
        if status == PREDICTOR_STATE.STATUS_STOPPING:
            print(
                "Deployment is stopping, explore historical logs at "
                + deployment_instance.get_url()
            )
            return
        if status == PREDICTOR_STATE.STATUS_STOPPED:
            print(
                "Deployment not running, explore historical logs at "
                + deployment_instance.get_url()
            )
            return
        if status == PREDICTOR_STATE.STATUS_STARTING:
            print("Deployment is starting, server logs might not be ready yet")

        print(
            "Explore all the logs and filters in the Kibana logs at "
            + deployment_instance.get_url(),
            end="\n\n",
        )

        return self._serving_api.get_logs(deployment_instance, component, tail)
