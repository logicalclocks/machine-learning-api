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

from hsml.utils.column import Column
import pandas
import importlib

try:
    import hsfs
except ImportError:
    pass

try:
    import pyspark
except ImportError:
    pass


class ColumnarSignature:
    """Metadata object representing a columnar signature for a model."""

    def __init__(self, columnar_obj=None):
        if isinstance(columnar_obj, list):
            self.columns = self._convert_list_to_signature(columnar_obj)
        elif isinstance(columnar_obj, pandas.DataFrame):
            self.columns = self._convert_pandas_df_to_signature(columnar_obj)
        elif isinstance(columnar_obj, pandas.Series):
            self.columns = self._convert_pandas_series_to_signature(columnar_obj)
        elif importlib.util.find_spec("pyspark") is not None and isinstance(
            columnar_obj, pyspark.sql.dataframe.DataFrame
        ):
            self.columns = self._convert_spark_to_signature(columnar_obj)
        elif importlib.util.find_spec("hsfs") is not None and isinstance(
            columnar_obj, hsfs.training_dataset.TrainingDataset
        ):
            self.columns = self._convert_td_to_signature(columnar_obj)
        else:
            raise TypeError(
                "{} is not supported in a signature.".format(type(columnar_obj))
            )

    def _convert_list_to_signature(self, columnar_obj):
        columns = []
        for entry in columnar_obj:
            columns.append(Column(name=entry["name"], data_type=entry["type"]))
        return columns

    def _convert_pandas_df_to_signature(self, columnar_obj):
        pandas_columns = columnar_obj.columns
        pandas_data_types = columnar_obj.dtypes
        columns = []
        for name in pandas_columns:
            columns.append(Column(name=name, data_type=str(pandas_data_types[name])))
        return columns

    def _convert_pandas_series_to_signature(self, columnar_obj):
        columns = []
        columns.append(Column(name="series", data_type=str(columnar_obj.dtypes)))
        return columns

    def _convert_spark_to_signature(self, spark_df):
        columns = []
        types = spark_df.dtypes
        for dtype in types:
            name, dtype = dtype
            columns.append(Column(name=name, data_type=str(dtype)))
        return columns

    def _convert_td_to_signature(self, td):
        columns = []
        features = td.schema
        for feature in features:
            columns.append(Column(name=feature.name, data_type=feature.type))
        return columns

    def to_dict(self):
        return {"columns": self.columns}
