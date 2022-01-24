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

import humps
from typing import Union, Optional

from hsml import util

from hsml.constants import PREDICTOR
from hsml.component_config import ComponentConfig
from hsml.resources_config import ResourcesConfig
from hsml.inference_logger_config import InferenceLoggerConfig
from hsml.inference_batcher_config import InferenceBatcherConfig


class PredictorConfig(ComponentConfig):
    """Configuration object attached to a Predictor."""

    REQUESTED_INSTANCES_KEY: str = "requested_instances"

    def __init__(
        self,
        model_server: str,
        serving_tool: Optional[str] = None,
        script_file: Optional[str] = None,
        resources_config: Optional[Union[ResourcesConfig, dict]] = None,
        inference_logger: Optional[Union[InferenceLoggerConfig, dict]] = None,
        inference_batcher: Optional[Union[InferenceBatcherConfig, dict]] = None,
    ):
        super().__init__(
            script_file, resources_config, inference_logger, inference_batcher
        )

        self._model_server = model_server
        self._serving_tool = (
            serving_tool if serving_tool is not None else PREDICTOR.SERVING_TOOL
        )

    def describe(self):
        util.pretty_print(self)

    @classmethod
    def for_model(cls, model):
        return util.get_predictor_config_for_model(model)

    @classmethod
    def from_json(cls, json_decamelized):
        return PredictorConfig(*cls.extract_fields_from_json(json_decamelized))

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        ms = json_decamelized.pop("model_server")
        st = json_decamelized.pop("serving_tool")
        sf = (
            json_decamelized.pop("predictor")
            if "predictor" in json_decamelized
            else None
        )
        rc = (
            ResourcesConfig.from_json(json_decamelized, cls.REQUESTED_INSTANCES_KEY)
            if cls.REQUESTED_INSTANCES_KEY in json_decamelized
            else None
        )
        il = InferenceLoggerConfig.from_json(json_decamelized)
        ib = InferenceBatcherConfig.from_json(json_decamelized)
        return ms, st, sf, rc, il, ib

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(*self.extract_fields_from_json(json_decamelized))
        return self

    def to_dict(self):
        return {
            "modelServer": self._model_server,
            "servingTool": self._serving_tool,
            "predictor": self._script_file,
            **self._resources_config.to_dict("requestedInstances"),
            **self._inference_logger.to_dict(),
            **self._inference_batcher.to_dict(),
        }

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
