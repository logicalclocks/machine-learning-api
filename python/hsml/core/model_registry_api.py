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
        shared_project_name = name
        shared_project_id = None

        if name is not None:
            project_info = _client._send_request("GET", ["project", "getProjectInfo", name])
            shared_project_id = self._project_id = str(project_info["projectId"])

        return ModelRegistry(_client._project_name, _client._project_id, shared_project_name=shared_project_name, shared_project_id=shared_project_id)
