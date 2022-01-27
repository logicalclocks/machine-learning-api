#
#   Copyright 2022 Logical Clocks AB
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

import json
import humps
from typing import Union, Optional

from hsml import util
from hsml import deployment

from hsml.predictor_config import PredictorConfig
from hsml.transformer_config import TransformerConfig
from hsml.predictor_state import PredictorState


class Predictor:
    """Metadata object representing a predictor in Model Serving."""

    def __init__(
        self,
        name: str,
        model_name: str,
        model_path: str,
        model_version: int,
        artifact_version: Union[int, str],
        predictor_config: Union[PredictorConfig, dict],
        transformer_config: Optional[Union[TransformerConfig, dict]] = None,
        id: Optional[int] = None,
        created_at: Optional[str] = None,
        creator: Optional[str] = None,
    ):
        self._name = name
        self._model_name = model_name
        self._model_path = model_path
        self._model_version = model_version
        self._artifact_version = artifact_version
        self._predictor_config = predictor_config
        self._transformer_config = transformer_config
        self._id = id
        self._created_at = created_at
        self._creator = creator

        # check for dict params
        predictor_config = util.get_obj_from_json(predictor_config, PredictorConfig)
        transformer_config = util.get_obj_from_json(
            transformer_config, TransformerConfig
        )

    def deploy(self):
        """Deploy this predictor of a pre-trained model"""

        _deployment = deployment.Deployment(predictor=self, name=self._name)
        _deployment.save()

        return _deployment

    def set_state(self, state: PredictorState):
        """Set the state of the predictor"""

        self._state = state

    def describe(self):
        util.pretty_print(self)

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        if isinstance(json_decamelized, list):
            if len(json_decamelized) == 0:
                return []
            return [cls.from_json(predictor) for predictor in json_decamelized]
        else:
            return cls.from_json(json_decamelized)

    @classmethod
    def from_json(cls, json_decamelized):
        predictor = Predictor(*cls.extract_fields_from_json(json_decamelized))
        predictor.set_state(PredictorState.from_response_json(json_decamelized))
        return predictor

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        name = json_decamelized.pop("name")
        mn = util.extract_field_from_json(json_decamelized, "model_name", default=name)
        mp = json_decamelized.pop("model_path")
        mv = json_decamelized.pop("model_version")
        av = json_decamelized.pop("artifact_version")
        pc = PredictorConfig.from_json(json_decamelized)
        tc = TransformerConfig.from_json(json_decamelized)
        id = json_decamelized.pop("id")
        ca = json_decamelized.pop("created")
        c = json_decamelized.pop("creator")
        return name, mn, mp, mv, av, pc, tc, id, ca, c

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(*self.extract_fields_from_json(json_decamelized))
        self.set_state(PredictorState.from_response_json(json_decamelized))
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        json = {
            "id": self._id,
            "name": self._name,
            "modelName": self._model_name,
            "modelPath": self._model_path,
            "modelVersion": self._model_version,
            "artifactVersion": self._artifact_version,
            "created": self._created_at,
            "creator": self._creator,
            **self._predictor_config.to_dict(),
        }
        if self._transformer_config is not None:
            return {**json, **self._transformer_config.to_dict()}
        return json

    @property
    def id(self):
        """Id of the predictor."""
        return self._id

    @property
    def name(self):
        """Name of the predictor."""
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def model_name(self):
        """Name of the model deployed by the predictor."""
        return self._model_name

    @model_name.setter
    def model_name(self, model_name: str):
        self._model_name = model_name

    @property
    def model_path(self):
        """Model path deployed by the predictor."""
        return self._model_path

    @model_path.setter
    def model_path(self, model_path: str):
        self._model_path = model_path

    @property
    def model_version(self):
        """Model version deployed by the predictor."""
        return self._model_version

    @model_version.setter
    def model_version(self, model_version: int):
        self._model_version = model_version

    @property
    def artifact_version(self):
        """Artifact version deployed by the predictor."""
        return self._artifact_version

    @artifact_version.setter
    def artifact_version(self, artifact_version: Union[int, str]):
        self._artifact_version = artifact_version

    @property
    def predictor_config(self):
        """Configuration of the predictor."""
        return self._predictor_config

    @predictor_config.setter
    def predictor_config(self, predictor_config: PredictorConfig):
        self._predictor_config = predictor_config

    @property
    def transformer_config(self):
        """Transformer configuration attached to the predictor."""
        return self._transformer_config

    @transformer_config.setter
    def transformer_config(self, transformer_config: TransformerConfig):
        self._transformer_config = transformer_config

    @property
    def created_at(self):
        """Created at date of the predictor."""
        return self._created_at

    @property
    def creator(self):
        """Creator of the predictor."""
        return self._creator

    @property
    def requested_instances(self):
        """Total number of requested instances in the predictor."""
        num_instances = self._predictor_config._resources_config.num_instances
        if self._transformer_config is not None:
            num_instances += self._transformer_config.resources_config.num_instances
        return num_instances
