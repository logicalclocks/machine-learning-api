#
#   Copyright 2021 Logical Clocks AB
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

import warnings
import humps

from hsml import util
from hsml.core import models_api
from hsml.tensorflow import signature as tensorflow_signature  # noqa: F401
from hsml.python import signature as python_signature  # noqa: F401
from hsml.sklearn import signature as sklearn_signature  # noqa: F401
from hsml.torch import signature as torch_signature  # noqa: F401


class ModelRegistry:
    DEFAULT_VERSION = 1

    def __init__(self, project_name, project_id):
        self._project_name = project_name
        self._project_id = project_id

        self._models_api = models_api.ModelsApi()

        self._tensorflow = tensorflow_signature
        self._python = python_signature
        self._sklearn = sklearn_signature
        self._torch = torch_signature

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls(**json_decamelized)

    def get_model(self, name: str, version: int = None):
        """Get a model entity from the model registry.
        Getting a model from the Model Registry means getting its metadata handle
        so you can subsequently download the model directory.
        # Arguments
            name: Name of the model to get.
            version: Version of the model to retrieve, defaults to `None` and will
                return the `version=1`.
        # Returns
            `Model`: The model metadata object.
        # Raises
            `RestAPIError`: If unable to retrieve model from the model registry.
        """

        if version is None:
            warnings.warn(
                "No version provided for getting model `{}`, defaulting to `{}`.".format(
                    name, self.DEFAULT_VERSION
                ),
                util.VersionWarning,
            )
            version = self.DEFAULT_VERSION
        return self._models_api.get(name, version)

    def get_models(self, name: str):
        """Get all model entities from the model registry for a specified name.
        Getting all models from the Model Registry for a given name returns a model entity for each version registered under
        the specified model name.
        # Arguments
            name: Name of the model to get.
        # Returns
            `List[Model]`: A list of all the model versions
        # Raises
            `RestAPIError`: If unable to retrieve model versions from the model registry.
        """

        return self._models_api.get_models(name)

    def get_best_model(self, name: str, metric=None, direction=None):
        """Get the best performing model entity from the model registry.
        Getting the best performing model from the Model Registry means specifying in addition to the name, also a metric
        name corresponding to one of the keys in the training_metrics dict of the model and a direction. For example to
        get the model version with the highest accuracy, specify metric='accuracy' and direction='max'.
        # Arguments
            name: Name of the model to get.
            metric: Name of the key in the training metrics field to compare.
            direction: 'max' to get the model entity with the highest value of the set metric, or 'min' for the lowest.
        # Returns
            `Model`: The model metadata object.
        # Raises
            `RestAPIError`: If unable to retrieve model from the model registry.
        """

        model = self._models_api.get_models(name, metric=metric, direction=direction)
        if type(model) is list and len(model) > 0:
            return model[0]
        else:
            return None

    @property
    def project_name(self):
        """Name of the project in which the model registry is located."""
        return self._project_name

    @property
    def project_id(self):
        """Id of the project in which the model registry is located."""
        return self._project_id

    @property
    def tensorflow(self):
        """tensorflow module for the model registry."""
        return self._tensorflow

    @property
    def python(self):
        """python module for the model registry."""
        return self._python

    @property
    def sklearn(self):
        """sklearn module for the model registry."""
        return self._sklearn

    @property
    def torch(self):
        """torch module for the model registry."""
        return self._torch
