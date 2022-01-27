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
import inspect
import humps

import numpy as np
import pandas as pd
import os

from json import JSONEncoder, dumps

from hsml.constants import PREDICTOR

from hsml.tensorflow.model import Model as TFModel
from hsml.torch.model import Model as TorchModel
from hsml.sklearn.model import Model as SkLearnModel
from hsml.python.model import Model as PyModel
from hsml.model import Model as BaseModel

from hsml.predictor_config import PredictorConfig as BasePredictorConfig
from hsml.tensorflow.predictor_config import PredictorConfig as TFPredictorConfig
from hsml.torch.predictor_config import PredictorConfig as TorchPredictorConfig
from hsml.sklearn.predictor_config import PredictorConfig as SkLearnPredictorConfig
from hsml.python.predictor_config import PredictorConfig as PyPredictorConfig

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


def set_model_class(model):
    _ = model.pop("type")
    _ = model.pop("href")

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


def _handle_tensor_input(input_tensor):
    return input_tensor.tolist()


def input_example_to_json(input_example):
    if isinstance(input_example, np.ndarray):
        if input_example.size > 0:
            return _handle_tensor_input(input_example)
        else:
            raise ValueError(
                "input_example of type {} can not be empty".format(type(input_example))
            )
    else:
        return _handle_dataframe_input(input_example)


def _handle_dataframe_input(input_ex):
    if isinstance(input_ex, pd.DataFrame):
        if not input_ex.empty:
            return input_ex.iloc[0].tolist()
        else:
            raise ValueError(
                "input_example of type {} can not be empty".format(type(input_ex))
            )
    elif isinstance(input_ex, pd.Series):
        if not input_ex.empty:
            return input_ex.iloc[0]
        else:
            raise ValueError(
                "input_example of type {} can not be empty".format(type(input_ex))
            )
    elif isinstance(input_ex, list):
        if len(input_ex) > 0:
            return input_ex
        else:
            raise ValueError(
                "input_example of type {} can not be empty".format(type(input_ex))
            )
    else:
        raise TypeError(
            "{} is not a supported input example type".format(type(input_ex))
        )


def compress(archive_file_path, archive_name, dir_to_archive_path):
    return shutil.make_archive(
        os.path.join(archive_file_path, archive_name), "gztar", dir_to_archive_path
    )


def decompress(archive_file_path, extract_dir=None):
    return shutil.unpack_archive(archive_file_path, extract_dir=extract_dir)


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


def get_predictor_config_for_model(model: BaseModel):
    if not isinstance(model, BaseModel):
        raise ValueError(
            "model is of type {}, but an instance of {} class is expected".format(
                type(model), BaseModel
            )
        )

    if type(model) == TFModel:
        return TFPredictorConfig()
    if type(model) == TorchModel:
        return TorchPredictorConfig()
    if type(model) == SkLearnModel:
        return SkLearnPredictorConfig()
    if type(model) == PyModel:
        return PyPredictorConfig()
    if type(model) == BaseModel:
        return BasePredictorConfig(model_server=PREDICTOR.MODEL_SERVER_PYTHON)


def pretty_print(obj):
    json_decamelized = humps.decamelize(obj.to_dict())
    print(dumps(json_decamelized, indent=4, sort_keys=True))


def get_obj_from_json(obj, cls):
    if obj is not None:
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, dict):
            return cls.from_json(obj)
        raise ValueError(
            "Object of type {} cannot be converted to class {}".format(type(obj), cls)
        )
    return obj


def get_members(cls, prefix=None):
    for m in inspect.getmembers(cls, lambda m: not (inspect.isroutine(m))):
        n = m[0]  # name
        if (prefix is not None and n.startswith(prefix)) or (
            prefix is None and not (n.startswith("__") and n.endswith("__"))
        ):
            yield m[1]  # value
