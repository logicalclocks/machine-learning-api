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

from hsml.utils.columnar_signature import ColumnarSignature
from hsml.utils.tensor_signature import TensorSignature
import numpy

class ModelSignatureSpec:
    """Metadata object representing a model signature for a model."""

    def __init__(
            self,
            data=None
    ):

        if isinstance(data, numpy.ndarray):
            self.tensor_signature = self._convert_tensor_to_signature(data)
        else:
            self.columnar_signature = self._convert_columnar_to_signature(data)

    def _convert_columnar_to_signature(self, data):
        return ColumnarSignature(data)

    def _convert_tensor_to_signature(self, data):
        return TensorSignature(data)

    def to_dict(self):
        sig_dict = {}
        if hasattr(self, "columnarSignature"):
            sig_dict["columnarSignature"] = self.columnar_signature
        if hasattr(self, "tensorSignature"):
            sig_dict["tensorSignature"] = self.tensor_signature
        return sig_dict
