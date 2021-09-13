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

from typing import Optional, Union, TypeVar
import pandas
import numpy
from hsml.utils.signature import Signature
from hsml.sklearn.model import Model


def create_model(
    name: str,
    version: Optional[int] = None,
    metrics: Optional[dict] = None,
    description: Optional[str] = None,
    input_example: Optional[Union[pandas.core.frame.DataFrame, numpy.ndarray]] = None,
    signature: Optional[Signature] = None,
    training_dataset: Optional[
        TypeVar("hsfs.training_dataset.TrainingDataset")  # noqa: F821
    ] = None,
):
    """Create a model metadata object.

    !!! note "Lazy"
        This method is lazy and does not persist any metadata or uploads model artifacts in the
        model registry on its own. To save the model object and the model artifacts, call the `save()` method with a
        local file path to the directory containing the model artifacts.

    # Arguments
        name: Name of the model to create.
        version: Optionally version of the model to create, defaults to `None` and
            will create the model with incremented version from the last
            version in the model registry.
        description: Optionally a string describing the model, defaults to empty string
            `""`.
        input_example: Optionally an input example that represents inputs for the model, defaults to `None`.
        signature: Optionally a signature for the model for inputs and/or predictions.
        training_dataset: Optionally a training dataset used to train the model.

    # Returns
        `Model`. The model metadata object.
    """
    return Model(
        id=None,
        name=name,
        version=version,
        description=description,
        metrics=metrics,
        input_example=input_example,
        signature=signature,
        training_dataset=training_dataset,
    )
