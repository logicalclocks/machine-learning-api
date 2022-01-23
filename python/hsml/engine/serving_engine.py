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

from tqdm.auto import tqdm

from hsml.core import serving_api
from hsml.constants import DEPLOYMENT, PREDICTOR, PREDICTOR_STATE


class ServingEngine:
    def __init__(self):
        self._serving_api = serving_api.ServingApi()

    def _poll_deployment_status(
        self, deployment_instance, status: str, await_status: int, update_progress
    ):
        if await_status > 0:
            sleep_seconds = 1
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
                update_progress(num_instances)
                if state.status.upper() == status:
                    return state  # deployment reached desired status
            print(
                "Deployment has not reached the desired status within the expected awaiting time, set a higher value for await_"
                + status.lower()
                + " to wait longer."
            )

    def start(self, deployment_instance, await_status: int):
        pbar = tqdm(total=4)
        pbar.set_description("Starting deployment")

        def update_progress(num_instances=0):
            # print("current step: " + str(num_instances))
            # print("pbar.n: " + str(pbar.n))
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
                pbar.set_description("Deployment is ready")
        except BaseException as be:
            self.stop(deployment_instance, await_status=0)
            raise be

    def stop(self, deployment_instance, await_status: int):
        pbar = tqdm(total=4)
        pbar.set_description("Stopping deployment")

        def update_progress(num_instances=0):
            # print("current step: " + str(num_instances))
            # print("pbar.n: " + str(pbar.n))
            pbar.update(num_instances - pbar.n)

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
        serving_tool = deployment_instance.predictor.predictor_config.serving_tool
        through_hopsworks = (
            serving_tool != PREDICTOR.SERVING_TOOL_KFSERVING
        )  # if not KFServing, send request to Hopsworks
        return self._serving_api.send_inference_request(
            deployment_instance, data, through_hopsworks
        )
