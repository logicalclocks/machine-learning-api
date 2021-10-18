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

from hsml.model import Model
import humps


class Model(Model):
    """Metadata object representing a tensorflow model in the Model Registry."""

    def __init__(
        self,
        id,
        name,
        version=None,
        created=None,
        environment=None,
        description=None,
        experiment_id=None,
        project_name=None,
        experiment_project_name=None,
        metrics=None,
        program=None,
        user_full_name=None,
        signature=None,
        training_dataset=None,
        input_example=None,
        framework=None,
    ):
        super().__init__(
            id,
            name,
            version=version,
            created=created,
            environment=environment,
            description=description,
            experiment_id=experiment_id,
            project_name=project_name,
            experiment_project_name=experiment_project_name,
            metrics=metrics,
            program=program,
            user_full_name=user_full_name,
            signature=signature,
            training_dataset=training_dataset,
            input_example=input_example,
            framework="TENSORFLOW",
        )

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        _ = json_decamelized.pop("type")
        self.__init__(**json_decamelized)
        return self
