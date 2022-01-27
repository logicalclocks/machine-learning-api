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

import json
import humps
from typing import Union, Optional

from hsml import util

from hsml.engine import model_engine
from hsml.predictor import Predictor
from hsml.predictor_config import PredictorConfig
from hsml.transformer_config import TransformerConfig


class Model:
    """Metadata object representing a model in the Model Registry."""

    def __init__(
        self,
        id,
        name,
        version=None,
        created=None,
        environment=None,
        description=None,
        experiment_id=None,
        project_name=None,
        experiment_project_name=None,
        metrics=None,
        program=None,
        user_full_name=None,
        model_schema=None,
        training_dataset=None,
        input_example=None,
        framework=None,
        model_registry_id=None,
        tags=None,
    ):

        self._id = id
        self._name = name
        self._version = version

        if description is None:
            self._description = "A collection of models for " + name
        else:
            self._description = description

        self._created = created
        self._environment = environment
        self._experiment_id = experiment_id
        self._project_name = project_name
        self._experiment_project_name = experiment_project_name
        self._training_metrics = metrics
        self._program = program
        self._user_full_name = user_full_name
        self._input_example = input_example
        self._framework = framework
        self._model_schema = model_schema
        self._training_dataset = training_dataset

        # This is needed for update_from_response_json function to not overwrite name of the shared registry this model originates from
        if not hasattr(self, "_shared_registry_project_name"):
            self._shared_registry_project_name = None

        self._model_registry_id = model_registry_id

        self._model_engine = model_engine.ModelEngine()

    def save(self, model_path, await_registration=480):
        """Persist this model including model files and metadata to the model registry."""
        return self._model_engine.save(
            self, model_path, await_registration=await_registration
        )

    def download(self):
        """Download the model files to a local folder."""
        return self._model_engine.download(self)

    def delete(self):
        """Delete the model

        !!! danger "Potentially dangerous operation"
            This operation drops all metadata associated with **this version** of the
            model **and** deletes the model files.

        # Raises
            `RestAPIError`.
        """
        self._model_engine.delete(self)

    def deploy(
        self,
        name: Optional[str] = None,
        artifact_version: Optional[str] = "CREATE",
        predictor_config: Optional[Union[PredictorConfig, dict]] = None,
        transformer_config: Optional[Union[TransformerConfig, dict]] = None,
    ):
        """Deploy the model"""

        if name is None:
            name = self._name
        if predictor_config is None:
            predictor_config = PredictorConfig.for_model(self)

        return Predictor(
            name,
            self._name,
            self.model_path,
            self._version,
            artifact_version,
            predictor_config,
            transformer_config=transformer_config,
        ).deploy()

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        if "count" in json_decamelized:
            if json_decamelized["count"] == 0:
                return []
            return [util.set_model_class(model) for model in json_decamelized["items"]]
        else:
            return util.set_model_class(json_decamelized)

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        _ = json_decamelized.pop("type")
        self.__init__(**json_decamelized)
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        return {
            "id": self._name + "_" + str(self._version),
            "experimentId": self._experiment_id,
            "projectName": self._project_name,
            "experimentProjectName": self._experiment_project_name,
            "name": self._name,
            "modelSchema": self._model_schema,
            "version": self._version,
            "description": self._description,
            "inputExample": self._input_example,
            "framework": self._framework,
            "metrics": self._training_metrics,
            "trainingDataset": self._training_dataset,
            "environment": self._environment,
            "program": self._program,
        }

    @property
    def id(self):
        """Id of the model."""
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def name(self):
        """Name of the model."""
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def version(self):
        """Version of the model."""
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

    @property
    def description(self):
        """Description of the model."""
        return self._description

    @description.setter
    def description(self, description):
        self._description = description

    @property
    def created(self):
        """Creation date of the model."""
        return self._created

    @created.setter
    def created(self, created):
        self._created = created

    @property
    def environment(self):
        """Input example of the model."""
        if self._environment is not None:
            return self._model_engine.read_file(self, "environment.yml")
        return self._environment

    @environment.setter
    def environment(self, environment):
        self._environment = environment

    @property
    def experiment_id(self):
        """Experiment Id of the model."""
        return self._experiment_id

    @experiment_id.setter
    def experiment_id(self, experiment_id):
        self._experiment_id = experiment_id

    @property
    def training_metrics(self):
        """Training metrics of the model."""
        return self._training_metrics

    @training_metrics.setter
    def training_metrics(self, training_metrics):
        self._training_metrics = training_metrics

    @property
    def program(self):
        """Executable used to export the model."""
        if self._program is not None:
            return self._model_engine.read_file(self, self._program)

    @program.setter
    def program(self, program):
        self._program = program

    @property
    def user(self):
        """user of the model."""
        return self._user_full_name

    @user.setter
    def user(self, user_full_name):
        self._user_full_name = user_full_name

    @property
    def input_example(self):
        """input_example of the model."""
        return self._model_engine.read_json(self, "input_example.json")

    @input_example.setter
    def input_example(self, input_example):
        self._input_example = input_example

    @property
    def framework(self):
        """framework of the model."""
        return self._framework

    @framework.setter
    def framework(self, framework):
        self._framework = framework

    @property
    def model_schema(self):
        """model schema of the model."""
        return self._model_engine.read_json(self, "model_schema.json")

    @model_schema.setter
    def model_schema(self, model_schema):
        self._model_schema = model_schema

    @property
    def training_dataset(self):
        """training_dataset of the model."""
        return self._training_dataset

    @training_dataset.setter
    def training_dataset(self, training_dataset):
        self._training_dataset = training_dataset

    @property
    def project_name(self):
        """project_name of the model."""
        return self._project_name

    @project_name.setter
    def project_name(self, project_name):
        self._project_name = project_name

    @property
    def model_registry_id(self):
        """model_registry_id of the model."""
        return self._model_registry_id

    @model_registry_id.setter
    def model_registry_id(self, model_registry_id):
        self._model_registry_id = model_registry_id

    @property
    def experiment_project_name(self):
        """experiment_project_name of the model."""
        return self._experiment_project_name

    @experiment_project_name.setter
    def experiment_project_name(self, experiment_project_name):
        self._experiment_project_name = experiment_project_name

    @property
    def model_path(self):
        """path of the model with version folder omitted. Resolves to /Projects/{project_name}/Models/{name}"""
        return "/Projects/{}/Models/{}".format(self.project_name, self.name)

    @property
    def version_path(self):
        """path of the model including version folder. Resolves to /Projects/{project_name}/Models/{name}/{version}"""
        return "{}/{}".format(self.model_path, str(self.version))

    @property
    def shared_registry_project_name(self):
        """shared_registry_project_name of the model."""
        return self._shared_registry_project_name

    @shared_registry_project_name.setter
    def shared_registry_project_name(self, shared_registry_project_name):
        self._shared_registry_project_name = shared_registry_project_name

    def set_tag(self, name: str, value: Union[str, dict]):
        """Attach a tag to a model.

        A tag consists of a <name,value> pair. Tag names are unique identifiers across the whole cluster.
        The value of a tag can be any valid json - primitives, arrays or json objects.

        # Arguments
            name: Name of the tag to be added.
            value: Value of the tag to be added.
        # Raises
            `RestAPIError` in case the backend fails to add the tag.
        """

        self._model_engine.set_tag(self, name, value)

    def delete_tag(self, name: str):
        """Delete a tag attached to a model.

        # Arguments
            name: Name of the tag to be removed.
        # Raises
            `RestAPIError` in case the backend fails to delete the tag.
        """
        self._model_engine.delete_tag(self, name)

    def get_tag(self, name: str):
        """Get the tags of a model.

        # Arguments
            name: Name of the tag to get.
        # Returns
            tag value
        # Raises
            `RestAPIError` in case the backend fails to retrieve the tag.
        """
        return self._model_engine.get_tag(self, name)

    def get_tags(self):
        """Retrieves all tags attached to a model.

        # Returns
            `Dict[str, obj]` of tags.
        # Raises
            `RestAPIError` in case the backend fails to retrieve the tags.
        """
        return self._model_engine.get_tags(self)
