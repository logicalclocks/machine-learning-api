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

from hsml.constants import DEFAULT, ARTIFACT_VERSION
from hsml.core import serving_api
from hsml.model import Model
from hsml.predictor import Predictor
from hsml.deployment import Deployment
from hsml.resources import PredictorResources
from hsml.inference_logger import InferenceLogger
from hsml.inference_batcher import InferenceBatcher
from hsml.transformer import Transformer


class ModelServing:
    DEFAULT_VERSION = 1

    def __init__(self, project_name: str, project_id: int):
        self._project_name = project_name
        self._project_id = project_id

        self._serving_api = serving_api.ServingApi()

    def get_deployment_by_id(self, id: int):
        """Get a deployment by id from Model Serving.
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
        """Get a deployment by name from Model Serving.
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
            `List[Deployment]`: A list of deployments.
        # Raises
            `RestAPIError`: If unable to retrieve deployments from model serving.
        """

        return self._serving_api.get_all()

    def create_predictor(
        self,
        model: Model,
        name: Optional[str] = None,
        artifact_version: Optional[str] = ARTIFACT_VERSION.CREATE,
        model_server: Optional[str] = None,
        serving_tool: Optional[str] = None,
        script_file: Optional[str] = None,
        resources: Optional[Union[PredictorResources, dict]] = DEFAULT,
        inference_logger: Optional[Union[InferenceLogger, dict, str]] = DEFAULT,
        inference_batcher: Optional[Union[InferenceBatcher, dict]] = None,
        transformer: Optional[Union[Transformer, dict]] = None,
    ):
        """Create a Predictor metadata object.

        !!! note "Lazy"
            This method is lazy and does not persist any metadata or deploy any model on its own.
            To create a deployment using this predictor, call the `deploy()` method.

        # Arguments
            model: Model to be deployed.
            name: Name of the predictor.
            artifact_version: Version number of the model artifact to deploy, `CREATE` to create a new model artifact
            or `MODEL-ONLY` to reuse the shared artifact containing only the model files.
            model_server: Model server ran by the predictor.
            serving_tool: Serving tool used to deploy the model server.
            script_file: Path to a custom predictor script implementing the Predict class.
            resources: Resources to be allocated for the predictor.
            inference_logger: Inference logger configuration.
            inference_batcher: Inference batcher configuration.
            transformer: Transformer to be deployed together with the predictor.

        # Returns
            `Predictor`. The predictor metadata object.
        """

        if name is None:
            name = model.name

        return Predictor.for_model(
            model,
            name=name,
            artifact_version=artifact_version,
            model_server=model_server,
            serving_tool=serving_tool,
            script_file=script_file,
            resources=resources,
            inference_logger=inference_logger,
            inference_batcher=inference_batcher,
            transformer=transformer,
        )

    def create_transformer(
        self,
        script_file: Optional[str] = None,
        resources: Optional[Union[PredictorResources, dict]] = DEFAULT,
    ):
        """Create a Transformer metadata object.

        !!! note "Lazy"
            This method is lazy and does not persist any metadata or deploy any transformer. To create a deployment using this transformer, set it in the `predictor.transformer` property.

        # Arguments
            script_file: Path to a custom predictor script implementing the Transformer class.
            resources: Resources to be allocated for the transformer.

        # Returns
            `Transformer`. The model metadata object.
        """

        return Transformer(script_file=script_file, resources=resources)

    def create_deployment(self, predictor: Predictor, name: Optional[str] = None):
        """Create a Deployment metadata object.

        !!! note "Lazy"
            This method is lazy and does not persist any metadata or deploy any model. To create a deployment, call the `save()` method.

        # Arguments
            predictor: predictor to be used in the deployment
            name: name of the deployment

        # Returns
            `Deployment`. The model metadata object.
        """

        return Deployment(predictor=predictor, name=name)

    @property
    def project_name(self):
        """Name of the project in which Model Serving is located."""
        return self._project_name

    @property
    def project_id(self):
        """Id of the project in which Model Serving is located."""
        return self._project_id

    def __repr__(self):
        return f"ModelServing({self._project_name!r})"
