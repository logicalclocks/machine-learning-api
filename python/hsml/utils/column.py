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

class Column:
    """Metadata object representing a model signature for a model."""

    def __init__(
            self,
            name: None,
            data_type: None
    ):

        self.name = name
        self.data_type = data_type

    def to_dict(self):
        return {
            "name": self.name,
            "dataType": self.data_type
        }