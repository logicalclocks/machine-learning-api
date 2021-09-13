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

from hsml.utils.tensor import Tensor
from typing import Union, Optional
import numpy


class TensorSignature:
    """Metadata object representing a tensor signature for a model."""

    def __init__(self, numpy_obj: Optional[Union[numpy.ndarray]] = None):

        self.tensor = self._convert_tensor_to_signature(numpy_obj)

    def _convert_tensor_to_signature(self, tensor_obj):
        return Tensor(shape=tensor_obj.shape, data_type=str(tensor_obj.dtype))
