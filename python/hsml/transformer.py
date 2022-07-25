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
from typing import Optional, Union

from hsml import util
from hsml import client

from hsml.deployable_component import DeployableComponent
from hsml.resources import TransformerResources


class Transformer(DeployableComponent):
    """Metadata object representing a transformer to be used in a predictor."""

    def __init__(
        self,
        script_file: str,
        resources: Optional[Union[TransformerResources, dict]] = None,  # base
    ):
        resources = (
            self._validate_resources(
                util.get_obj_from_json(resources, TransformerResources)
            )
            or self._get_default_resources()
        )

        super().__init__(script_file, resources)

    def describe(self):
        """Print a description of the transformer"""
        util.pretty_print(self)

    @classmethod
    def _validate_resources(cls, resources):
        if resources is not None:
            # ensure scale-to-zero for kserve deployments on app hopsworks
            if resources.num_instances != 0 and client.is_saas_connection():
                raise ValueError(
                    "Number of instances must be 0 for KServe deployments to enable scale-to-zero capabilities"
                )
        return resources

    @classmethod
    def _get_default_resources(cls):
        # enable scale-to-zero in app hopsworks
        resources = TransformerResources()
        if client.is_saas_connection():
            resources.num_instances = 0
        return resources

    @classmethod
    def from_json(cls, json_decamelized):
        sf, rc = cls.extract_fields_from_json(json_decamelized)
        return Transformer(sf, rc) if sf is not None else None

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        sf = util.extract_field_from_json(
            json_decamelized, ["transformer", "script_file"]
        )
        rc = TransformerResources.from_json(json_decamelized)
        return sf, rc

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(*self.extract_fields_from_json(json_decamelized))
        return self

    def to_dict(self):
        return {"transformer": self._script_file, **self._resources.to_dict()}

    def __repr__(self):
        return f"Transformer({self._script_file!r})"
