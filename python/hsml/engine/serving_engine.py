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


class ServingEngine:
    def __init__(self):
        self._serving_api = serving_api.ServingApi()
        self._dataset_api = dataset_api.DatasetApi()

    def _poll_deployment_status(
        self, deployment_instance, status: str, await_status: int, update_progress
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
                update_progress(num_instances)
                if state.status.upper() == status:
                    return state  # deployment reached desired status
            print(
                "Deployment has not reached the desired status within the expected awaiting time, set a higher value for await_"
                + status.lower()
                + " to wait longer."
            )

    def start(self, deployment_instance, await_status: int):
        if self._check_status(deployment_instance, PREDICTOR_STATE.STATUS_RUNNING):
            return

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
            if (
                state is not None
                and state.status.upper() == PREDICTOR_STATE.STATUS_RUNNING
            ):
                pbar.set_description("Deployment is running")
        except BaseException as be:
            self.stop(deployment_instance, await_status=0)
            raise be

    def stop(self, deployment_instance, await_status: int):
        if self._check_status(deployment_instance, PREDICTOR_STATE.STATUS_STOPPED):
            return

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
        if state is not None and state.status.upper() == PREDICTOR_STATE.STATUS_STOPPED:
            pbar.set_description("Deployment is stopped")

    def predict(self, deployment_instance, data: dict):
        serving_tool = deployment_instance.predictor.serving_tool
        through_hopsworks = (
            serving_tool != PREDICTOR.SERVING_TOOL_KSERVE
        )  # if not KServe, send request to Hopsworks
        return self._serving_api.send_inference_request(
            deployment_instance, data, through_hopsworks
        )

    def _check_status(self, deployment_instance, desired_status):
        status = deployment_instance.get_state().status.upper()

        # desired status: running
        if desired_status == PREDICTOR_STATE.STATUS_RUNNING:
            if (
                status == PREDICTOR_STATE.STATUS_STARTING
                or status == PREDICTOR_STATE.STATUS_RUNNING
            ):
                print("Deployment is already " + status.lower())
                return True
            if status == PREDICTOR_STATE.STATUS_UPDATING:
                print("Deployment is already running and updating")
                return True
            if status == PREDICTOR_STATE.STATUS_STOPPING:
                print("Deployment is stopping, please wait until it completely stops")
                return True

        # desired status: stopped
        if desired_status == PREDICTOR_STATE.STATUS_STOPPED:
            if (
                status == PREDICTOR_STATE.STATUS_STOPPED
                or status == PREDICTOR_STATE.STATUS_STOPPING
            ):
                print("Deployment is already " + status.lower())
                return True

        return False

    def download_artifact(self, deployment_instance):
        if deployment_instance.artifact_version is None:
            # model artifacts are not created in non-k8s installations
            print(
                "Model artifacts not supported in non-k8s installations. \
                 Download the model files using `model.download()`"
            )
            return

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
