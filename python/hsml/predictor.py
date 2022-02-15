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

import json
import humps
from typing import Union, Optional

from hsml import util
from hsml import deployment

from hsml.constants import PREDICTOR
from hsml.transformer import Transformer
from hsml.predictor_state import PredictorState
from hsml.serving_component import ServingComponent
from hsml.resources import PredictorResources
from hsml.inference_logger import InferenceLogger
from hsml.inference_batcher import InferenceBatcher


class Predictor(ServingComponent):
    """Metadata object representing a predictor in Model Serving."""

    def __init__(
        self,
        name: str,
        model_name: str,
        model_path: str,
        model_version: int,
        artifact_version: Union[int, str],
        model_server: str,
        serving_tool: Optional[str] = None,
        script_file: Optional[str] = None,
        resources: Optional[Union[PredictorResources, dict]] = None,  # base
        inference_logger: Optional[Union[InferenceLogger, dict]] = None,  # base
        inference_batcher: Optional[Union[InferenceBatcher, dict]] = None,  # base
        transformer: Optional[Union[Transformer, dict]] = None,
        id: Optional[int] = None,
        created_at: Optional[str] = None,
        creator: Optional[str] = None,
    ):
        super().__init__(
            script_file,
            util.get_obj_from_json(resources, PredictorResources)
            or PredictorResources(),
            inference_batcher,
        )

        self._name = name
        self._model_name = model_name
        self._model_path = model_path
        self._model_version = model_version
        self._artifact_version = artifact_version
        self._id = id
        self._created_at = created_at
        self._creator = creator

        self._model_server = self._validate_model_server(model_server)
        self._serving_tool = (
            self._validate_serving_tool(serving_tool)
            or PREDICTOR.SERVING_TOOL_KFSERVING
        )
        self._inference_logger = (
            util.get_obj_from_json(inference_logger, InferenceLogger)
            or InferenceLogger()
        )
        self._transformer = util.get_obj_from_json(transformer, Transformer)

    def deploy(self):
        """Deploy this predictor of a pre-trained model"""

        _deployment = deployment.Deployment(predictor=self, name=self._name)
        _deployment.save()

        return _deployment

    def describe(self):
        util.pretty_print(self)

    def _set_state(self, state: PredictorState):
        """Set the state of the predictor"""

        self._state = state

    def _validate_model_server(self, model_server):
        model_servers = util.get_members(PREDICTOR, prefix="MODEL_SERVER")
        if model_server not in model_servers:
            raise ValueError(
                "Model server {} is not valid. Possible values are {}".format(
                    model_server, ", ".join(model_servers)
                )
            )
        return model_server

    def _validate_serving_tool(self, serving_tool):
        if serving_tool is not None:
            serving_tools = util.get_members(PREDICTOR, prefix="SERVING_TOOL")
            if serving_tool not in serving_tools:
                raise ValueError(
                    "Serving tool {} is not valid. Possible values are {}".format(
                        serving_tool, ", ".join(serving_tools)
                    )
                )
        return serving_tool

    @classmethod
    def for_model(cls, model, **kwargs):
        kwargs["model_name"] = model.name
        kwargs["model_path"] = model.model_path
        kwargs["model_version"] = model.version

        return util.get_predictor_for_model(model, **kwargs)

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        if isinstance(json_decamelized, list):
            if len(json_decamelized) == 0:
                return []
            return [cls.from_json(predictor) for predictor in json_decamelized]
        else:
            return cls.from_json(json_decamelized)

    @classmethod
    def from_json(cls, json_decamelized):
        predictor = Predictor(**cls.extract_fields_from_json(json_decamelized))
        predictor._set_state(PredictorState.from_response_json(json_decamelized))
        return predictor

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        kwargs = {}
        kwargs["name"] = json_decamelized.pop("name")
        kwargs["model_name"] = util.extract_field_from_json(
            json_decamelized, "model_name", default=kwargs["name"]
        )
        kwargs["model_path"] = json_decamelized.pop("model_path")
        kwargs["model_version"] = json_decamelized.pop("model_version")
        kwargs["artifact_version"] = json_decamelized.pop("artifact_version")
        kwargs["model_server"] = json_decamelized.pop("model_server")
        kwargs["serving_tool"] = json_decamelized.pop("serving_tool")
        kwargs["script_file"] = util.extract_field_from_json(
            json_decamelized, "predictor"
        )
        kwargs["resources"] = PredictorResources.from_json(json_decamelized)
        kwargs["inference_logger"] = InferenceLogger.from_json(json_decamelized)
        kwargs["inference_batcher"] = InferenceBatcher.from_json(json_decamelized)
        kwargs["transformer"] = Transformer.from_json(json_decamelized)
        kwargs["id"] = json_decamelized.pop("id")
        kwargs["created_at"] = json_decamelized.pop("created")
        kwargs["creator"] = json_decamelized.pop("creator")
        return kwargs

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(**self.extract_fields_from_json(json_decamelized))
        self._set_state(PredictorState.from_response_json(json_decamelized))
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        json = {
            "id": self._id,
            "name": self._name,
            "modelName": self._model_name,
            "modelPath": self._model_path,
            "modelVersion": self._model_version,
            "artifactVersion": self._artifact_version,
            "created": self._created_at,
            "creator": self._creator,
            "modelServer": self._model_server,
            "servingTool": self._serving_tool,
            "predictor": self._script_file,
            **self._resources.to_dict(),
            **self._inference_logger.to_dict(),
            **self._inference_batcher.to_dict(),
        }
        if self._transformer is not None:
            return {**json, **self._transformer.to_dict()}
        return json

    @property
    def id(self):
        """Id of the predictor."""
        return self._id

    @property
    def name(self):
        """Name of the predictor."""
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def model_name(self):
        """Name of the model deployed by the predictor."""
        return self._model_name

    @model_name.setter
    def model_name(self, model_name: str):
        self._model_name = model_name

    @property
    def model_path(self):
        """Model path deployed by the predictor."""
        return self._model_path

    @model_path.setter
    def model_path(self, model_path: str):
        self._model_path = model_path

    @property
    def model_version(self):
        """Model version deployed by the predictor."""
        return self._model_version

    @model_version.setter
    def model_version(self, model_version: int):
        self._model_version = model_version

    @property
    def artifact_version(self):
        """Artifact version deployed by the predictor."""
        return self._artifact_version

    @artifact_version.setter
    def artifact_version(self, artifact_version: Union[int, str]):
        self._artifact_version = artifact_version

    @property
    def model_server(self):
        """Model server used by the predictor."""
        return self._model_server

    @model_server.setter
    def model_server(self, model_server: str):
        self._model_server = model_server

    @property
    def serving_tool(self):
        """Serving tool used to run the model server."""
        return self._serving_tool

    @serving_tool.setter
    def serving_tool(self, serving_tool: str):
        self._serving_tool = serving_tool

    @property
    def inference_logger(self):
        """Configuration of the inference logger attached to this predictor."""
        return self._inference_logger

    @inference_logger.setter
    def inference_logger(self, inference_logger: InferenceLogger):
        self._inference_logger = inference_logger

    @property
    def transformer(self):
        """Transformer configuration attached to the predictor."""
        return self._transformer

    @transformer.setter
    def transformer(self, transformer: Transformer):
        self._transformer = transformer

    @property
    def created_at(self):
        """Created at date of the predictor."""
        return self._created_at

    @property
    def creator(self):
        """Creator of the predictor."""
        return self._creator

    @property
    def requested_instances(self):
        """Total number of requested instances in the predictor."""
        num_instances = self._resources.num_instances
        if self._transformer is not None:
            num_instances += self._transformer.resources.num_instances
        return num_instances
