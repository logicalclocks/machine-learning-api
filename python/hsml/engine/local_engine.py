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

from hsml.core import dataset_api


class LocalEngine:
    def __init__(self):
        self._dataset_api = dataset_api.DatasetApi()

    def mkdir(self, model_instance):
        self._dataset_api.mkdir(model_instance.version_path)

    def delete(self, model_instance):
        self._dataset_api.rm(model_instance.version_path)
