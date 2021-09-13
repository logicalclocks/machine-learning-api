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

from typing import Union, Optional, TypeVar
import json
import numpy
import pandas

from hsml.utils.model_signature_spec import ModelSignatureSpec


class Signature:
    """Metadata object representing a model signature for a model."""

    def __init__(
        self,
        inputs: Optional[
            Union[
                pandas.DataFrame,
                pandas.Series,
                TypeVar("pyspark.sql.dataframe.DataFrame"),  # noqa: F821
                TypeVar("hsfs.training_dataset.TrainingDataset"),  # noqa: F821
                numpy.ndarray,
            ]
        ] = None,
        predictions: Optional[
            Union[
                pandas.DataFrame,
                pandas.Series,
                TypeVar("pyspark.sql.dataframe.DataFrame"),  # noqa: F821
                numpy.ndarray,
            ]
        ] = None,
    ):

        if inputs is not None:
            self.inputs = self._convert_to_signature(inputs)

        if predictions is not None:
            self.predictions = self._convert_to_signature(predictions)

    def _convert_to_signature(self, data):
        return ModelSignatureSpec(data)

    def json(self):
        return json.dumps(
            self, default=lambda o: getattr(o, "__dict__", o), sort_keys=True, indent=2
        )
