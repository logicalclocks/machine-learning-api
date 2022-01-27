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
from typing import Optional

from hsml import util

from hsml.component_config import ComponentConfig
from hsml.resources_config import TransformerResourcesConfig
from hsml.inference_logger_config import InferenceLoggerConfig
from hsml.inference_batcher_config import InferenceBatcherConfig


class TransformerConfig(ComponentConfig):
    """Configuration object attached to a Transformer."""

    def __init__(
        self,
        script_file: str,
        resources_config: Optional[TransformerResourcesConfig] = None,
        inference_logger: Optional[InferenceLoggerConfig] = None,
        inference_batcher: Optional[InferenceBatcherConfig] = None,
    ):
        resources_config = resources_config or TransformerResourcesConfig()

        super().__init__(
            script_file, resources_config, inference_logger, inference_batcher
        )

    def describe(self):
        util.pretty_print(self)

    @classmethod
    def from_json(cls, json_decamelized):
        return (
            TransformerConfig(*cls.extract_fields_from_json(json_decamelized))
            if "transformer" in json_decamelized
            else None
        )

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        sf = json_decamelized.pop("transformer")
        rc = TransformerResourcesConfig.from_json(json_decamelized)
        il = InferenceLoggerConfig.from_json(json_decamelized)
        ib = InferenceBatcherConfig.from_json(json_decamelized)
        return sf, rc, il, ib

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(*self.extract_fields_from_json(json_decamelized))
        return self

    def to_dict(self):
        return {"transformer": self._script_file, **self._resources_config.to_dict()}
