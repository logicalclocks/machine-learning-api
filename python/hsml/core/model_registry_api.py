from hsml import client
from hsml.model_registry import ModelRegistry


class ModelRegistryApi:
    def __init__(self):
        pass

    def get(self, name=None):
        """Get model registry for specific project.
        :param name: project of the model registry
        :type name: str
        :return: the model registry metadata
        :rtype: ModelRegistry
        """
        _client = client.get_instance()

        if name is not None:
            project_info = _client._send_request("GET", ["project", "getProjectInfo", name])

        return ModelRegistry(_client._project_name, _client._project_id, shared_registry_project=name)
