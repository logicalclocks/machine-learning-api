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
            sleep_seconds = 3
            for _ in range(int(await_status / sleep_seconds)):
                time.sleep(sleep_seconds)
                state = deployment_instance.get_state()
                num_instances = state.available_predictor_instances
                if state.available_transformer_instances is not None:
                    num_instances += state.available_transformer_instances
                update_progress(num_instances)
                if state.status.upper() == status:
                    return state  # deployment reached desired status
            print(
                "Deployment has not reached the desired status within the expected awaiting time, set a higher value for await_"
                + status.lower()
                + " to wait longer."
            )

    def start(self, deployment_instance, await_status: int):
        pbar = tqdm(
            [
                {
                    "status": PREDICTOR_STATE.STATUS_STOPPED,
                    "desc": "Deployment is stopped",
                },
                {
                    "status": PREDICTOR_STATE.STATUS_STARTING,
                    "desc": "Starting deployment",
                },
                {
                    "status": PREDICTOR_STATE.STATUS_RUNNING,
                    "desc": "Deployment is running",
                },
            ]
        )

        def update_progress(num_instances=None):
            if num_instances is not None:
                pbar.set_description("%s" % step["desc"])
            else:
                pbar.set_description(
                    "%s (%d/%d)"
                    % (
                        step["desc"],
                        num_instances,
                        deployment_instance.requested_instances,
                    )
                )

        for step in pbar:
            try:
                update_progress()
                if step["status"] == PREDICTOR_STATE.STATUS_STOPPED:
                    self._serving_api.post(deployment_instance, DEPLOYMENT.ACTION_START)
                if step["status"] == PREDICTOR_STATE.STATUS_STARTING:
                    state = self._poll_deployment_status(
                        deployment_instance,
                        PREDICTOR_STATE.STATUS_RUNNING,
                        await_status,
                        update_progress,
                    )
                    if (
                        state is not None
                        and state.status.upper() != PREDICTOR_STATE.STATUS_RUNNING
                    ):
                        return
                if step["status"] == PREDICTOR_STATE.STATUS_RUNNING:
                    pass
            except BaseException as be:
                self.stop(deployment_instance, await_status=0)
                raise be

    def stop(self, deployment_instance, await_status: int):
        pbar = tqdm(
            [
                {
                    "status": PREDICTOR_STATE.STATUS_RUNNING,
                    "desc": "Deployment is running",
                },
                {
                    "status": PREDICTOR_STATE.STATUS_STOPPING,
                    "desc": "Stopping deployment",
                },
                {
                    "status": PREDICTOR_STATE.STATUS_STOPPED,
                    "desc": "Deployment is stopped",
                },
            ]
        )

        def update_progress(num_instances=None):
            if num_instances is not None:
                pbar.set_description("%s" % step["desc"])
            else:
                pbar.set_description(
                    "%s (%d/%d)"
                    % (
                        step["desc"],
                        num_instances,
                        deployment_instance.requested_instances,
                    )
                )

        for step in pbar:
            pbar.set_description("%s" % step["desc"])
            if step["status"] == PREDICTOR_STATE.STATUS_RUNNING:
                self._serving_api.post(deployment_instance, DEPLOYMENT.ACTION_STOP)
            if step["status"] == PREDICTOR_STATE.STATUS_STOPPING:
                state = self._poll_deployment_status(
                    deployment_instance,
                    PREDICTOR_STATE.STATUS_STOPPED,
                    await_status,
                    update_progress,
                )
                if (
                    state is not None
                    and state.status.upper() != PREDICTOR_STATE.STATUS_STOPPED
                ):
                    return
            if step["status"] == PREDICTOR_STATE.STATUS_STOPPED:
                pass

    def predict(self, deployment_instance, data: dict):
        serving_tool = deployment_instance.predictor.predictor_config.serving_tool
        through_hopsworks = (
            serving_tool != PREDICTOR.SERVING_TOOL_KFSERVING
        )  # if not KFServing, send request to Hopsworks
        return self._serving_api.send_inference_request(
            deployment_instance, data, through_hopsworks
        )
