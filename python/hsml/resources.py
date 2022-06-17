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
from typing import Optional, Union
from abc import abstractclassmethod, abstractmethod

from hsml import util

from hsml.constants import RESOURCES


class Resources:
    """Resource configuration for a predictor or transformer.

    # Arguments
        cores: Number of CPUs. The default value is `1` CPUs.
        memory: Memory resources. The default value is `1024Mb`.
        gpus: Number of GPUs. The default value is `0` GPUs.
    # Returns
        `Resources`. Resource configuration for a predictor or transformer.
    """

    def __init__(
        self,
        cores: Optional[int] = None,
        memory: Optional[int] = None,
        gpus: Optional[int] = None,
    ):
        self._cores = cores if cores is not None else RESOURCES.CORES
        self._memory = memory if memory is not None else RESOURCES.MEMORY
        self._gpus = gpus if gpus is not None else RESOURCES.GPUS

    def describe(self):
        """Print a description of the resource configuration"""
        util.pretty_print(self)

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls.from_json(json_decamelized)

    @abstractclassmethod
    def from_json(cls, json_decamelized):
        return Resources(*cls.extract_fields_from_json(json_decamelized))

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        cores = util.extract_field_from_json(json_decamelized, "cores")
        memory = util.extract_field_from_json(json_decamelized, "memory")
        gpus = util.extract_field_from_json(json_decamelized, "gpus")

        return cores, memory, gpus

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    @abstractmethod
    def to_dict(self):
        return {"cores": self._cores, "memory": self._memory, "gpus": self._gpus}

    @property
    def cores(self):
        """Number of CPUs to be allocated per instance"""
        return self._cores

    @cores.setter
    def cores(self, cores: int):
        self._cores = cores

    @property
    def memory(self):
        """Memory resources to be allocated per instance"""
        return self._memory

    @memory.setter
    def memory(self, memory: int):
        self._memory = memory

    @property
    def gpus(self):
        """Number of GPUs to be allocated per instance"""
        return self._gpus

    @gpus.setter
    def gpus(self, gpus: int):
        self._gpus = gpus

    def __repr__(self):
        return f"Resources(cores: {self._cores!r}, memory: {self._memory!r}, gpus: {self._gpus!r})"


class ComponentResources:
    """Resource configuration for a predictor or transformer.

    # Arguments
        num_instances: Number of instances. The default value is 1 instance.
        requests: Minimum resources to allocate for a deployment
        limits: Maximum resources to allocate for a deployment
    # Returns
        `ComponentResource`. Resource configuration for a predictor or transformer.
    """

    def __init__(
        self,
        num_instances: Optional[int] = None,
        requests: Optional[Union[Resources, dict]] = None,
        limits: Optional[Union[Resources, dict]] = None,
    ):
        self._num_instances = (
            num_instances if num_instances is not None else RESOURCES.NUM_INSTANCES
        )
        self._requests = util.get_obj_from_json(requests, Resources) or Resources()
        self._limits = util.get_obj_from_json(limits, Resources) or Resources()

    def describe(self):
        """Print a description of the resource configuration"""
        util.pretty_print(self)

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls.from_json(json_decamelized)

    @abstractclassmethod
    def from_json(cls, json_decamelized):
        pass

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        num_instances = util.extract_field_from_json(
            json_decamelized, [cls.NUM_INSTANCES_KEY, "num_instances"]
        )

        if cls.RESOURCES_CONFIG_KEY in json_decamelized:
            resources = json_decamelized.pop(cls.RESOURCES_CONFIG_KEY)
            requests = util.get_obj_from_json(resources["requests"], Resources)
            limits = util.get_obj_from_json(resources["limits"], Resources)
        else:
            requests = util.extract_field_from_json(
                json_decamelized, "requests", as_instance_of=Resources
            )
            limits = util.extract_field_from_json(
                json_decamelized, "limits", as_instance_of=Resources
            )

        return num_instances, requests, limits

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    @abstractmethod
    def to_dict(self):
        pass

    @property
    def num_instances(self):
        """Number of instances"""
        return self._num_instances

    @num_instances.setter
    def num_instances(self, num_instances: int):
        self._num_instances = num_instances

    @property
    def requests(self):
        """Minimum resources to allocate"""
        return self._requests

    @requests.setter
    def requests(self, requests: Resources):
        self._resources = requests

    @property
    def limits(self):
        """Maximum resources to allocate"""
        return self._limits

    @limits.setter
    def limits(self, limits: Resources):
        self._limits = limits

    def __repr__(self):
        return f"ComponentResources(num_instances: {self._num_instances!r}, requests: {self._requests is not None!r}, limits: {self._limits is not None!r})"


class PredictorResources(ComponentResources):

    RESOURCES_CONFIG_KEY = "predictor_resources"
    NUM_INSTANCES_KEY = "requested_instances"

    def __init__(
        self,
        num_instances: Optional[int] = None,
        requests: Optional[Union[Resources, dict]] = None,
        limits: Optional[Union[Resources, dict]] = None,
    ):
        super().__init__(num_instances, requests, limits)

    @classmethod
    def from_json(cls, json_decamelized):
        return PredictorResources(*cls.extract_fields_from_json(json_decamelized))

    def to_dict(self):
        return {
            humps.camelize(self.NUM_INSTANCES_KEY): self._num_instances,
            humps.camelize(self.RESOURCES_CONFIG_KEY): {
                "requests": self._requests.to_dict()
                if self._requests is not None
                else None,
                "limits": self._limits.to_dict() if self._limits is not None else None,
            },
        }


class TransformerResources(ComponentResources):

    RESOURCES_CONFIG_KEY = "transformer_resources"
    NUM_INSTANCES_KEY = "requested_transformer_instances"

    def __init__(
        self,
        num_instances: Optional[int] = None,
        requests: Optional[Union[Resources, dict]] = None,
        limits: Optional[Union[Resources, dict]] = None,
    ):
        super().__init__(num_instances, requests, limits)

    @classmethod
    def from_json(cls, json_decamelized):
        return TransformerResources(*cls.extract_fields_from_json(json_decamelized))

    def to_dict(self):
        return {
            humps.camelize(self.NUM_INSTANCES_KEY): self._num_instances,
            humps.camelize(self.RESOURCES_CONFIG_KEY): {
                "requests": self._requests.to_dict()
                if self._requests is not None
                else None,
                "limits": self._limits.to_dict() if self._limits is not None else None,
            },
        }
