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

import shutil
import datetime

from typing import Union
import numpy as np
import pandas as pd

from json import JSONEncoder

from hsml.tensorflow.model import Model as TFModel
from hsml.torch.model import Model as TorchModel
from hsml.sklearn.model import Model as SkLearnModel
from hsml.python.model import Model as PyModel
from hsml.model import Model as BaseModel

from six import string_types


class VersionWarning(Warning):
    pass


class MLEncoder(JSONEncoder):
    def default(self, obj):
        try:
            return obj.to_dict()
        except AttributeError:
            return super().default(obj)


class NumpyEncoder(JSONEncoder):
    """Special json encoder for numpy types.
    Note that some numpy types doesn't have native python equivalence,
    hence json.dumps will raise TypeError.
    In this case, you'll need to convert your numpy types into its closest python equivalence.
    """

    def convert(self, obj):
        import pandas as pd
        import numpy as np
        import base64

        def encode_binary(x):
            return base64.encodebytes(x).decode("ascii")

        if isinstance(obj, np.ndarray):
            if obj.dtype == np.object:
                return [self.convert(x)[0] for x in obj.tolist()]
            elif obj.dtype == np.bytes_:
                return np.vectorize(encode_binary)(obj), True
            else:
                return obj.tolist(), True

        if isinstance(obj, (pd.Timestamp, datetime.date)):
            return obj.isoformat(), True
        if isinstance(obj, bytes) or isinstance(obj, bytearray):
            return encode_binary(obj), True
        if isinstance(obj, np.generic):
            return obj.item(), True
        if isinstance(obj, np.datetime64):
            return np.datetime_as_string(obj), True
        return obj, False

    def default(self, obj):  # pylint: disable=E0202
        res, converted = self.convert(obj)
        if converted:
            return res
        else:
            return super().default(obj)


def _is_numpy_scalar(x):
    return np.isscalar(x) or x is None


def _is_ndarray(x):
    return isinstance(x, np.ndarray) or (
        isinstance(x, dict) and all([isinstance(ary, np.ndarray) for ary in x.values()])
    )


def set_model_class(model):
    if "framework" not in model:
        return BaseModel(**model)
    if model["framework"] == "TENSORFLOW":
        return TFModel(**model)
    if model["framework"] == "TORCH":
        return TorchModel(**model)
    if model["framework"] == "SKLEARN":
        return SkLearnModel(**model)
    elif model["framework"] == "PYTHON":
        return PyModel(**model)


def _handle_tensor_input(input_tensor: Union[np.ndarray, dict]):
    if isinstance(input_tensor, dict):
        result = {}
        for name in input_tensor.keys():
            result[name] = input_tensor[name].tolist()
        return {"data": result}
    else:
        return {"data": input_tensor.tolist()}


def input_example_to_json(input_example):
    if _is_ndarray(input_example):
        return _handle_tensor_input(input_example)
    else:
        return _handle_dataframe_input(input_example)


def _handle_dataframe_input(input_ex):
    if isinstance(input_ex, pd.DataFrame):
        result = input_ex.to_dict(orient="split")
        del result["index"]
        return result
    elif isinstance(input_ex, pd.Series):
        return input_ex.to_dict()
    else:
        raise TypeError(
            "{} is not a supported input example type".format(type(input_ex))
        )


def zip(zip_file_path, dir_to_zip_path):
    return shutil.make_archive(zip_file_path + "/archive", "zip", dir_to_zip_path)


def unzip(zip_file_path, extract_dir=None):
    return shutil.unpack_archive(zip_file_path, extract_dir=extract_dir)


def validate_metrics(metrics):
    if not isinstance(metrics, dict):
        raise TypeError(
            "provided metrics is of instance {}, expected a dict".format(type(metrics))
        )

    for metric in metrics:
        if not isinstance(metric, string_types):
            raise TypeError(
                "provided metrics key is of instance {}, expected a string".format(
                    type(metric)
                )
            )
        validate_metric_value(metrics[metric])


def validate_metric_value(opt_val):
    try:
        int(opt_val)
        return opt_val
    except Exception:
        pass
    try:
        float(opt_val)
        return opt_val
    except Exception:
        pass
    raise TypeError(
        "Metric value is of type {}, expecting a number".format(type(opt_val))
    )
