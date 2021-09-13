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

from hsml import util

from hsml.core import models_api, dataset_api

from hsml.engine import models_engine


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
        signature=None,
        training_dataset=None,
        input_example=None,
        framework=None,
        model_registry_id=None,
        href=None,
        expand=None,
        items=None,
        count=None,
        type=None,
    ):

        if id is None:
            self._id = name + "_" + str(version)
        else:
            self._id = id

        if project_name is not None:
            self._path = (
                "/Projects/" + project_name + "/Models/" + name + "/" + str(version)
            )

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
        self._signature = signature
        self._training_dataset = training_dataset
        self._model_registry_id = model_registry_id

        self._models_api = models_api.ModelsApi()
        self._dataset_api = dataset_api.DatasetApi()
        self._models_engine = models_engine.Engine()

    def save(self, model_path, await_registration=480):
        """Persist the model metadata object to the model registry."""
        return self._models_engine.save(
            self, model_path, await_registration=await_registration
        )

    def download(self):
        """Download the model files to a local folder."""
        return self._models_engine.download(self)

    def delete(self):
        """Delete the model

        !!! danger "Potentially dangerous operation"
            This operation drops all metadata associated with **this version** of the
            model **and** in addition to the model artifacts.

        # Raises
            `RestAPIError`.
        """
        self._models_api.delete(self)

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
            "signature": self._signature,
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
        if self._environment is not None and isinstance(self._environment, list):
            self._environment = self._models_engine.read_environment(self)
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
        return self._program

    @program.setter
    def program(self, program):
        self._program = program

    @property
    def user(self):
        """user_full_name of the model."""
        return self._user_full_name

    @user.setter
    def user_full_name(self, user_full_name):
        self._user_full_name = user_full_name

    @property
    def input_example(self):
        """input_example of the model."""
        if self._input_example is not None and isinstance(self._input_example, str):
            self._input_example = self._models_engine.read_input_example(self)
        return self._input_example

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
    def signature(self):
        """signature of the model."""
        if self._signature is not None and isinstance(self._signature, str):
            self._signature = self._models_engine.read_signature(self)
        return self._signature

    @signature.setter
    def signature(self, signature):
        self._signature = signature

    @property
    def training_dataset(self):
        """training_dataset of the model."""
        if self._training_dataset is not None and isinstance(
            self._training_dataset, str
        ):
            td_split = self._training_dataset.split(":")
            td_dict = {
                "project": td_split[0],
                "name": td_split[1],
                "version": td_split[2],
            }
            return td_dict
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
    def experiment_project_name(self):
        """experiment_project_name of the model."""
        return self._experiment_project_name

    @experiment_project_name.setter
    def experiment_project_name(self, experiment_project_name):
        self._experiment_project_name = experiment_project_name

    @property
    def path(self):
        """path of the model."""
        return self._path

    @path.setter
    def path(self, path):
        self._path = path

    def add_tag(self, name: str, value):
        """Attach a tag to a feature group.
        A tag consists of a <name,value> pair. Tag names are unique identifiers across the whole cluster.
        The value of a tag can be any valid json - primitives, arrays or json objects.
        # Arguments
            name: Name of the tag to be added.
            value: Value of the tag to be added.
        # Raises
            `RestAPIError` in case the backend fails to add the tag.
        """

        self._models_engine.add_tag(self, name, value)

    def delete_tag(self, name: str):
        """Delete a tag attached to a feature group.
        # Arguments
            name: Name of the tag to be removed.
        # Raises
            `RestAPIError` in case the backend fails to delete the tag.
        """
        self._models_engine.delete_tag(self, name)

    def get_tag(self, name: str):
        """Get the tags of a feature group.
        # Arguments
            name: Name of the tag to get.
        # Returns
            tag value
        # Raises
            `RestAPIError` in case the backend fails to retrieve the tag.
        """
        return self._models_engine.get_tag(self, name)

    def get_tags(self):
        """Retrieves all tags attached to a feature group.
        # Returns
            `Dict[str, obj]` of tags.
        # Raises
            `RestAPIError` in case the backend fails to retrieve the tags.
        """
        return self._models_engine.get_tags(self)
