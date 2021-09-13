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

from hsml import client, model


class ModelsApi:
    def __init__(self):
        pass

    def put(self, model_instance, query_params):
        """Save model metadata to the model registry.

        :param model_instance: metadata object of feature group to be saved
        :type model_instance: Model
        :return: updated metadata object of the model
        :rtype: Model
        """
        _client = client.get_instance()
        path_params = [
            "project",
            _client._project_id,
            "models",
            model_instance.name + "_" + str(model_instance.version),
        ]
        headers = {"content-type": "application/json"}
        return model_instance.update_from_response_json(
            _client._send_request(
                "PUT",
                path_params,
                headers=headers,
                query_params=query_params,
                data=model_instance.json(),
            )
        )

    def get(self, name, version):
        """Get the metadata of a model with a certain name and version.

        :param name: name of the model
        :type name: str
        :param version: version of the model
        :type version: int
        :return: model metadata object
        :rtype: Model
        """
        _client = client.get_instance()
        path_params = [
            "project",
            _client._project_id,
            "models",
            name + "_" + str(version),
        ]
        query_params = {"expand": "trainingdatasets"}
        model_json = _client._send_request("GET", path_params, query_params)
        return model.Model.from_response_json(model_json)

    def get_models(self, name, metric=None, direction=None):
        """Get the metadata of a model with a certain name and version.

        :param name: name of the model
        :type name: str
        :param version: version of the model
        :type version: int
        :return: model metadata object
        :rtype: Model
        """

        _client = client.get_instance()
        path_params = ["project", _client._project_id, "models"]

        query_params = {"expand": "trainingdatasets", "filter_by": "name_eq:" + name}
        if metric is not None and direction is not None:
            if direction.lower() == "max":
                direction = "desc"
            elif direction.lower() == "min":
                direction = "asc"

            query_params["sort_by"] = metric + ":" + direction
            query_params["limit"] = "1"

        model_json = _client._send_request("GET", path_params, query_params)
        return model.Model.from_response_json(model_json)

    def delete(self, model_instance):
        """Delete the model and metadata.

        :param model_instance: metadata object of model to delete
        :type model_instance: Model
        """
        _client = client.get_instance()
        path_params = ["project", _client._project_id, "models", model_instance.id]
        _client._send_request("DELETE", path_params)
