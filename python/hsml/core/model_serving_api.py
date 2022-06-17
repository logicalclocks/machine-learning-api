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
from hsml.core import dataset_api, serving_api
from hsml.constants import INFERENCE_ENDPOINTS
from hsml.inference_endpoint import get_endpoint_by_type
from hsml.client.exceptions import ModelRegistryException


class ModelServingApi:
    def __init__(self):
        self._dataset_api = dataset_api.DatasetApi()
        self._serving_api = serving_api.ServingApi()

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

    def set_istio_client_if_available(self):
        """Set istio client if available"""

        # check kserve installed
        if self._serving_api.is_kserve_installed():
            # check existing istio client
            try:
                if client.get_istio_instance() is not None:
                    return  # istio client already set
            except Exception:
                pass

            # setup istio client
            inference_endpoints = self._serving_api.get_inference_endpoints()
            if client.get_client_type() == "internal":
                endpoint = get_endpoint_by_type(
                    inference_endpoints, INFERENCE_ENDPOINTS.ENDPOINT_TYPE_NODE
                )
                if endpoint is not None:
                    client.set_istio_client(
                        endpoint.get_any_host(),
                        endpoint.get_port(INFERENCE_ENDPOINTS.PORT_NAME_HTTP).number,
                    )
                else:
                    raise ValueError(
                        "Istio ingress endpoint of type '"
                        + INFERENCE_ENDPOINTS.ENDPOINT_TYPE_NODE
                        + "' not found"
                    )
            else:
                endpoint = get_endpoint_by_type(
                    inference_endpoints, INFERENCE_ENDPOINTS.ENDPOINT_TYPE_LOAD_BALANCER
                )
                if endpoint is not None:
                    _client = client.get_instance()
                    client.set_istio_client(
                        endpoint.get_any_host(),
                        endpoint.get_port(INFERENCE_ENDPOINTS.PORT_NAME_HTTP).number,
                        _client._project_name,
                        _client._auth._token,  # reuse hopsworks client token
                    )
                else:
                    raise ValueError(
                        "Istio ingress endpoint of type '"
                        + INFERENCE_ENDPOINTS.ENDPOINT_TYPE_LOAD_BALANCER
                        + "' not found"
                    )
