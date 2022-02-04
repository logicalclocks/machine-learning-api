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
from typing import Optional

from hsml import util

from hsml.constants import INFERENCE_BATCHER


class InferenceBatcherConfig:
    """Configuration for an inference batcher."""

    def __init__(self, enabled: Optional[bool] = None):
        self._enabled = enabled if enabled is not None else INFERENCE_BATCHER.ENABLED

    def describe(self):
        util.pretty_print(self)

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls.from_json(json_decamelized)

    @classmethod
    def from_json(cls, json_decamelized):
        return InferenceBatcherConfig(cls.extract_fields_from_json(json_decamelized))

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        return util.extract_field_from_json(
            json_decamelized, "batching_enabled"
        ) or util.extract_field_from_json(json_decamelized, "enabled")

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(self.extract_fields_from_json(json_decamelized))
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        return {"batchingEnabled": self._enabled}

    @property
    def enabled(self):
        """Whether the inference batcher is enabled or not."""
        return self._enabled

    @enabled.setter
    def enabled(self, enabled: bool):
        self._enabled = enabled
