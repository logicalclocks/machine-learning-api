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

from typing import Union, Optional

from hsml import util
from hsml import predictor as predictor_mod

from hsml.core import serving_api
from hsml.engine import serving_engine
from hsml.resources import Resources
from hsml.inference_logger import InferenceLogger
from hsml.inference_batcher import InferenceBatcher
from hsml.transformer import Transformer

from hsml.client.exceptions import ModelServingException


class Deployment:
    """Metadata object representing a deployment in Model Serving."""

    def __init__(self, predictor, name: Optional[str] = None):
        self._predictor = predictor
        self._name = name

        if self._predictor is None:
            raise ModelServingException("A predictor is required")
        elif not isinstance(self._predictor, predictor_mod.Predictor):
            raise ValueError(
                "The predictor provided is not an instance of the Predictor class"
            )

        if self._name is None:
            self._name = self._predictor.name
        else:
            self._name = self._predictor.name = name

        self._serving_api = serving_api.ServingApi()
        self._serving_engine = serving_engine.ServingEngine()

    def save(self):
        """Persist this deployment including the predictor and metadata to Model Serving."""

        self._serving_api.put(self, query_params={})

    def start(self, await_running: Optional[int] = 60):
        """Start the deployment

        # Arguments
            await_running: Awaiting time (seconds) for the deployment to start.
                           If the deployment has not started within this timespan, the call to this method returns while
                           it deploys in the background.
        """

        self._serving_engine.start(self, await_status=await_running)

    def stop(self, await_stopped: Optional[int] = 60):
        """Stop the deployment

        # Arguments
            await_stopped: Awaiting time (seconds) for the deployment to stop.
                           If the deployment has not stopped within this timespan, the call to this method returns while
                           it stopping in the background.
        """

        self._serving_engine.stop(self, await_status=await_stopped)

    def delete(self):
        """Delete the deployment"""

        self._serving_api.delete(self)

    def get_state(self):
        """Get the current state of the deployment

        # Returns
            `PredictorState`. The state of the deployment.
        """

        state = self._serving_api.get_state(self)
        self.predictor._set_state(state)
        return state

    def predict(self, data: dict):
        """Send inference requests to the deployment

        # Arguments
            data: Payload of the inference request.

        # Returns
            `dict`. Inference response.
        """

        return self._serving_engine.predict(self, data)

    def describe(self):
        """Print a description of the deployment"""

        util.pretty_print(self)

    @classmethod
    def from_response_json(cls, json_dict):
        predictors = predictor_mod.Predictor.from_response_json(json_dict)
        if isinstance(predictors, list):
            return [
                cls.from_predictor(predictor_instance)
                for predictor_instance in predictors
            ]
        else:
            return cls.from_predictor(predictors)

    @classmethod
    def from_predictor(cls, predictor_instance):
        return Deployment(predictor=predictor_instance, name=predictor_instance._name)

    def update_from_response_json(self, json_dict):
        self._predictor.update_from_response_json(json_dict)
        self.__init__(predictor=self._predictor, name=self._predictor._name)
        return self

    def json(self):
        return self._predictor.json()

    def to_dict(self):
        return self._predictor.to_dict()

    # Deployment

    @property
    def id(self):
        """Id of the deployment."""
        return self._predictor.id

    @property
    def name(self):
        """Name of the deployment."""
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def predictor(self):
        """Predictor used in the deployment."""
        return self._predictor

    @predictor.setter
    def predictor(self, predictor):
        self._predictor = predictor

    @property
    def requested_instances(self):
        """Total number of requested instances in the deployment."""
        return self._predictor.requested_instances

    # Single predictor

    @property
    def model_name(self):
        """Name of the model deployed by the predictor"""
        return self._predictor._model_name

    @model_name.setter
    def model_name(self, model_name: str):
        self._predictor._model_name = model_name

    @property
    def model_path(self):
        """Model path deployed by the predictor."""
        return self._predictor._model_path

    @model_path.setter
    def model_path(self, model_path: str):
        self._predictor._model_path = model_path

    @property
    def model_version(self):
        """Model version deployed by the predictor."""
        return self._predictor._model_version

    @model_version.setter
    def model_version(self, model_version: int):
        self._predictor._model_version = model_version

    @property
    def artifact_version(self):
        """Artifact version deployed by the predictor."""
        return self._predictor._artifact_version

    @artifact_version.setter
    def artifact_version(self, artifact_version: Union[int, str]):
        self._predictor._artifact_version = artifact_version

    @property
    def model_server(self):
        """Model server ran by the predictor."""
        return self._predictor._model_server

    @model_server.setter
    def model_server(self, model_server: str):
        self._predictor._model_server = model_server

    @property
    def serving_tool(self):
        """Serving tool used to run the model server."""
        return self._predictor._serving_tool

    @serving_tool.setter
    def serving_tool(self, serving_tool: str):
        self._predictor._serving_tool = serving_tool

    @property
    def script_file(self):
        """Script file used by the predictor."""
        return self._predictor._script_file

    @script_file.setter
    def script_file(self, script_file: str):
        self._predictor._script_file = script_file

    @property
    def resources(self):
        """Resource configuration for the predictor."""
        return self._predictor._resources

    @resources.setter
    def resources(self, resources: Resources):
        self._predictor._resources = resources

    @property
    def inference_logger(self):
        """Configuration of the inference logger attached to this predictor."""
        return self._predictor._inference_logger

    @inference_logger.setter
    def inference_logger(self, inference_logger: InferenceLogger):
        self._predictor._inference_logger = inference_logger

    @property
    def inference_batcher(self):
        """Configuration of the inference batcher attached to this predictor."""
        return self._predictor._inference_batcher

    @inference_batcher.setter
    def inference_batcher(self, inference_batcher: InferenceBatcher):
        self._predictor._inference_batcher = inference_batcher

    @property
    def transformer(self):
        """Transformer configured in the predictor."""
        return self._predictor._transformer

    @transformer.setter
    def transformer(self, transformer: Transformer):
        self._predictor._transformer = transformer

    @property
    def created_at(self):
        """Created at date of the predictor."""
        return self._predictor._created_at

    @property
    def creator(self):
        """Creator of the predictor."""
        return self._predictor._creator

    def __repr__(self):
        return f"Deployment({self._name!r}, {self.model_name!r}, {self.model_version!r}, {self.serving_tool!r})"
