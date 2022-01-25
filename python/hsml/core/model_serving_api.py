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
#

from hsml import client
from hsml.model_serving import ModelServing
from hsml.core import dataset_api
from hsml.client.exceptions import ModelRegistryException


class ModelServingApi:
    def __init__(self):
        self._dataset_api = dataset_api.DatasetApi()

    def get(self):
        """Get model serving for specific project.
        :param project: project of the model registry
        :type project: str
        :return: the model serving metadata
        :rtype: ModelServing
        """
        _client = client.get_instance()

        # Validate that there is a Models dataset in the connected project
        if not self._dataset_api.path_exists("Models"):
            raise ModelRegistryException(
                "No Models dataset exists in project {}, Please enable the Serving service or create the dataset manually.".format(
                    _client._project_name
                )
            )

        return ModelServing(_client._project_name, _client._project_id)
