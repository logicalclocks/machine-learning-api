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

from hsml import client
from hsml.model_registry import ModelRegistry
from hsml.core import dataset_api
from hsml.client.exceptions import ModelRegistryException


class ModelRegistryApi:
    def __init__(self):
        self._dataset_api = dataset_api.DatasetApi()

    def get(self, project=None):
        """Get model registry for specific project.
        :param project: project of the model registry
        :type project: str
        :return: the model registry metadata
        :rtype: ModelRegistry
        """
        _client = client.get_instance()

        if project is not None and not self._dataset_api.path_exists(
            "{}::Models".format(project)
        ):
            raise ModelRegistryException(
                "No model registry shared with current project {}, from project {}".format(
                    _client._project_name, project
                )
            )

        return ModelRegistry(
            _client._project_name, _client._project_id, shared_registry_project=project
        )
