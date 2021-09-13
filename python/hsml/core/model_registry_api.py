from hsml import client
from hsml.model_registry import ModelRegistry


class ModelRegistryApi:
    def __init__(self):
        pass

    def get(self):
        """Get model registry store with specific id or name.

        :return: the model registry metadata
        :rtype: ModelRegistry
        """
        _client = client.get_instance()
        return ModelRegistry(_client._project_name, _client._project_id)
