from hsml import client
from hsml.model_registry import ModelRegistry
from hsml.core import dataset_api


class ModelRegistryApi:
    def __init__(self):
        self._dataset_api = dataset_api.DatasetApi()

    def get(self, name=None):
        """Get model registry for specific project.
        :param name: project of the model registry
        :type name: str
        :return: the model registry metadata
        :rtype: ModelRegistry
        """
        _client = client.get_instance()

        if name is not None and not self._dataset_api.path_exists("{}::Models".format(name)):
            raise ModelRegistryException(
                "No model registry shared with project {} from project {}".format(
                    _client._project_name, name
                )
            )

        return ModelRegistry(_client._project_name, _client._project_id, shared_registry_project=name)
