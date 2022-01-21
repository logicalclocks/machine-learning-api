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

from typing import Optional

from hsml import util
from hsml import predictor

from hsml.core import serving_api
from hsml.engine import serving_engine

from hsml.client.exceptions import ModelServingException


class Deployment:
    """Metadata object representing a deployment in Model Serving."""

    def __init__(self, predictor, name: Optional[str] = None):
        self._predictor = predictor
        self._name = name

        if self._predictor is None:
            raise ModelServingException("A predictor is required")

        if self._name is None:
            self._name = self._predictor.name
        else:
            self._name = self._predictor.name = name

        self._serving_api = serving_api.ServingApi()
        self._serving_engine = serving_engine.ServingEngine()

    def save(self):
        """Persist this deployment including the predictor and metadata to model serving."""

        self._serving_api.put(self, query_params={})

    def start(self, await_running: Optional[int] = 60):
        """Start this deployment"""

        return self._serving_engine.start(self, await_status=await_running)

    def stop(self, await_stopped: Optional[int] = 60):
        """Stop this deployment"""

        return self._serving_engine.stop(self, await_status=await_stopped)

    def delete(self):
        """Delete this deployment"""

        self._serving_api.delete(self)

    def get_state(self):
        """Get the current state of the deployment"""

        state = self._serving_api.get_state(self)
        self.predictor.set_state(state)
        return state

    def predict(self, data: dict):
        """Send inference requests to this deployment"""

        return self._serving_engine.predict(self, data)

    def describe(self):
        """Print a description of this deployment"""

        util.pretty_print(self)

    @classmethod
    def from_response_json(cls, json_dict):
        predictors = predictor.Predictor.from_response_json(json_dict)
        if isinstance(predictors, list):
            return [
                cls.from_predictor(predictor_instance)
                for predictor_instance in predictors
            ]
        else:
            return cls.from_predictor(predictors)

    @classmethod
    def from_predictor(cls, predictor_instance):
        return Deployment(predictor=predictor_instance, name=predictor_instance._name)

    def update_from_response_json(self, json_dict):
        self._predictor.update_from_response_json(json_dict)
        self.__init__(predictor=self._predictor, name=self._predictor._name)
        return self

    def json(self):
        return self._predictor.json()

    def to_dict(self):
        return self._predictor.to_dict()

    @property
    def id(self):
        """Id of the deployment."""
        return self._predictor.id

    @property
    def name(self):
        """Name of the deployment."""
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def predictor(self):
        """Predictor contained in the deployment."""
        return self._predictor

    @predictor.setter
    def predictor(self, predictor):
        self._predictor = predictor

    @property
    def requested_instances(self):
        """Total number of requested instances in the deployment."""
        return self._predictor.requested_instances
