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

from hsml.constants import PREDICTOR
from hsml.predictor_config import PredictorConfig
from hsml.resources_config import PredictorResourcesConfig
from hsml.inference_logger_config import InferenceLoggerConfig
from hsml.inference_batcher_config import InferenceBatcherConfig


class PredictorConfig(PredictorConfig):
    """Configuration for a predictor running a tensorflow model."""

    def __init__(
        self,
        serving_tool: Optional[str] = PREDICTOR.SERVING_TOOL_KFSERVING,
        script_file: Optional[str] = None,
        resources_config: Optional[Union[PredictorResourcesConfig, dict]] = None,
        inference_logger: Optional[Union[InferenceLoggerConfig, dict]] = None,
        inference_batcher: Optional[Union[InferenceBatcherConfig, dict]] = None,
    ):
        super().__init__(
            model_server=PREDICTOR.MODEL_SERVER_TF_SERVING,
            serving_tool=serving_tool,
            script_file=script_file,
            resources_config=resources_config,
            inference_logger=inference_logger,
            inference_batcher=inference_batcher,
        )
