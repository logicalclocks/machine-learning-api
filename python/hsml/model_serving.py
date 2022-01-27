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

from typing import Union, Optional

from hsml.core import serving_api
from hsml.model import Model
from hsml.predictor import Predictor
from hsml.predictor_config import PredictorConfig
from hsml.deployment import Deployment
from hsml.transformer_config import TransformerConfig


class ModelServing:
    DEFAULT_VERSION = 1

    def __init__(self, project_name: str, project_id: int):
        self._project_name = project_name
        self._project_id = project_id

        self._serving_api = serving_api.ServingApi()

    def get_deployment_by_id(self, id: int):
        """Get a deployment entity from model serving.
        Getting a deployment from Model Serving means getting its metadata handle
        so you can subsequently operate on it (e.g., start or stop).

        # Arguments
            id: Id of the deployment to get.
        # Returns
            `Deployment`: The deployment metadata object.
        # Raises
            `RestAPIError`: If unable to retrieve deployment from model serving.
        """

        return self._serving_api.get_by_id(id)

    def get_deployment(self, name: str):
        """Get a deployment entity from model serving by name.
        Getting a deployment from Model Serving means getting its metadata handle
        so you can subsequently operate on it (e.g., start or stop).

        # Arguments
            name: Name of the deployment to get.
        # Returns
            `Deployment`: The deployment metadata object.
        # Raises
            `RestAPIError`: If unable to retrieve deployment from model serving.
        """

        return self._serving_api.get(name)

    def get_deployments(self):
        """Get all deployments from model serving.

        # Returns
            `List[Deployment]`: A list of deployment metadata objects.
        # Raises
            `RestAPIError`: If unable to retrieve deployments from model serving.
        """

        return self._serving_api.get_all()

    def create_predictor(
        self,
        model: Model,
        name: Optional[str] = None,
        artifact_version: Union[int, str] = "CREATE",
        predictor_config: PredictorConfig = None,
        transformer_config: TransformerConfig = None,
    ):
        """Deploy the model"""

        if name is None:
            name = model.name
        if predictor_config is None:
            predictor_config = PredictorConfig.for_model(self)

        return Predictor(
            name,
            model.name,
            model.model_path,
            model.version,
            artifact_version,
            predictor_config,
            transformer_config=transformer_config,
        )

    def create_deployment(self, predictor: Predictor, name: Optional[str] = None):
        """Deploy the model"""

        return Deployment(predictor=predictor, name=name)

    @property
    def project_name(self):
        """Name of the project in which model serving is located."""
        return self._project_name

    @property
    def project_id(self):
        """Id of the project in which model serving is located."""
        return self._project_id
