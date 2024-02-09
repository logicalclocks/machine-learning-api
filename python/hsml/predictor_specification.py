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

from hsml.constants import ARTIFACT_VERSION, PREDICTOR, MODEL
from hsml.transformer import Transformer
from hsml.predictor_state import PredictorState
from hsml.deployable_component import DeployableComponent
from hsml.resources import PredictorResources
from hsml.inference_logger import InferenceLogger
from hsml.inference_batcher import InferenceBatcher


class PredictorSpecification(DeployableComponent):
    """Metadata object representing a predictor in Model Serving."""

    def __init__(
        self,
        model_name: str,
        model_path: str,
        model_version: int,
        model_framework: str,  # MODEL.FRAMEWORK
        artifact_version: Union[int, str],
        model_server: str,
        script_file: Optional[str] = None,
        resources: Optional[Union[PredictorResources, dict]] = None,  # base
        inference_batcher: Optional[Union[InferenceBatcher, dict]] = None,  # base
        transformer: Optional[Union[Transformer, dict]] = None,
        id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(
            script_file,
            resources,
            inference_batcher,
        )

        self._model_name = model_name
        self._model_path = model_path
        self._model_version = model_version
        self._model_framework = model_framework
        self._artifact_version = artifact_version
        self._model_server = model_server
        self._id = id
        self._transformer = util.get_obj_from_json(transformer, Transformer)
        self._validate_script_file(self._model_framework, self._script_file)

    def deploy(self):
        """Create a deployment for this predictor and persists it in the Model Serving.

        !!! example
            ```python

            import hopsworks

            project = hopsworks.login()

            # get Hopsworks Model Registry handle
            mr = project.get_model_registry()

            # retrieve the trained model you want to deploy
            my_model = mr.get_model("my_model", version=1)

            # get Hopsworks Model Serving handle
            ms = project.get_model_serving()

            my_predictor = ms.create_predictor(my_model)
            my_deployment = my_predictor.deploy()

            print(my_deployment.get_state())
            ```

        # Returns
            `Deployment`. The deployment metadata object of a new or existing deployment.
        """

        _deployment = deployment.Deployment(
            predictor=self, name=self._name, description=self._description
        )
        _deployment.save()

        return _deployment

    def describe(self):
        """Print a description of the predictor"""
        util.pretty_print(self)

    def _set_state(self, state: PredictorState):
        """Set the state of the predictor"""
        self._state = state

    @classmethod
    def _validate_script_file(cls, model_framework, script_file):
        if model_framework == MODEL.FRAMEWORK_PYTHON and script_file is None:
            raise ValueError(
                "Predictor scripts are required in deployments for custom Python models"
            )

    @classmethod
    def _infer_model_server(cls, model_framework):
        return (
            PREDICTOR.MODEL_SERVER_TF_SERVING
            if model_framework == MODEL.FRAMEWORK_TENSORFLOW
            else PREDICTOR.MODEL_SERVER_PYTHON
        )

    @classmethod
    def for_model(cls, model, **kwargs):
        kwargs["model_name"] = model.name
        kwargs["model_path"] = model.model_path
        kwargs["model_version"] = model.version

        # get predictor for specific model, includes model type-related validations
        return util.get_predictor_for_model(model, **kwargs)

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls.from_json(json_decamelized)

    @classmethod
    def from_json(cls, json_decamelized):
        return PredictorSpecification(**cls.extract_fields_from_json(json_decamelized))

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        kwargs = {}
        kwargs["model_name"] = json_decamelized.pop("model_name")
        kwargs["model_path"] = json_decamelized.pop("model_path")
        kwargs["model_version"] = json_decamelized.pop("model_version")
        kwargs["model_framework"] = (
            json_decamelized.pop("model_framework")
            if "model_framework" in json_decamelized
            else MODEL.FRAMEWORK_SKLEARN  # backward compatibility
        )
        kwargs["artifact_version"] = util.extract_field_from_json(
            json_decamelized, "artifact_version"
        )
        kwargs["model_server"] = json_decamelized.pop("model_server")
        kwargs["script_file"] = util.extract_field_from_json(
            json_decamelized, "predictor"
        )
        kwargs["resources"] = PredictorResources.from_json(json_decamelized)
        kwargs["inference_batcher"] = InferenceBatcher.from_json(json_decamelized)
        kwargs["transformer"] = Transformer.from_json(json_decamelized)
        kwargs["id"] = json_decamelized.pop("id")
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
            "modelName": self._model_name,
            "modelPath": self._model_path,
            "modelVersion": self._model_version,
            "modelFramework": self._model_framework,
            "artifactVersion": self._artifact_version,
            "modelServer": self._model_server,
            "predictor": self._script_file,
        }
        if self._resources is not None:
            json = {**json, **self._resources.to_dict()}
        if self._inference_batcher is not None:
            json = {**json, **self._inference_batcher.to_dict()}
        if self._transformer is not None:
            json = {**json, **self._transformer.to_dict()}
        return json

    @property
    def id(self):
        """Id of the predictor."""
        return self._id

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
    def model_framework(self):
        """Model framework of the model to be deployed by the predictor."""
        return self._model_framework

    @model_framework.setter
    def model_framework(self, model_framework: str):
        self._model_framework = model_framework
        self._model_server = self._infer_model_server(model_framework)

    @property
    def artifact_version(self):
        """Artifact version deployed by the predictor."""
        return self._artifact_version

    @artifact_version.setter
    def artifact_version(self, artifact_version: Union[int, str]):
        self._artifact_version = artifact_version

    @property
    def artifact_path(self):
        """Path of the model artifact deployed by the predictor. Resolves to /Projects/{project_name}/Models/{name}/{version}/Artifacts/{artifact_version}/{name}_{version}_{artifact_version}.zip"""
        artifact_name = "{}_{}_{}.zip".format(
            self._model_name, str(self._model_version), str(self._artifact_version)
        )
        return "{}/{}/Artifacts/{}/{}".format(
            self._model_path,
            str(self._model_version),
            str(self._artifact_version),
            artifact_name,
        )

    @property
    def model_server(self):
        """Model server used by the predictor."""
        return self._model_server

    @property
    def script_file(self):
        """Script file used to load and run the model."""
        return self._predictor._script_file

    @script_file.setter
    def script_file(self, script_file: str):
        self._script_file = script_file
        self._artifact_version = ARTIFACT_VERSION.CREATE

    @property
    def transformer(self):
        """Transformer configuration attached to the predictor."""
        return self._transformer

    @transformer.setter
    def transformer(self, transformer: Transformer):
        self._transformer = transformer

    @property
    def requested_instances(self):
        """Total number of requested instances in the predictor."""
        num_instances = self._resources.num_instances
        if self._transformer is not None:
            num_instances += self._transformer.resources.num_instances
        return num_instances

    def __repr__(self):
        return str(vars(self))

