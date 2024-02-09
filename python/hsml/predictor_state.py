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

import humps
from typing import Optional

from hsml import util
from hsml.predictor_state_internal import PredictorStateInternal

class PredictorState:
    """State of a predictor."""

    def __init__(
        self,
        hopsworks_inference_path: str,
        model_server_inference_path: str,
        internal_port: Optional[int],
        revision: Optional[int],
        deployed: Optional[bool],
        status: str,
        serving_status: PredictorStateInternal,
        candidate_status: Optional[PredictorStateInternal],
        **kwargs,
    ):
        self._hopsworks_inference_path = hopsworks_inference_path
        self._model_server_inference_path = model_server_inference_path
        self._internal_port = internal_port
        self._revision = revision
        self._deployed = deployed if deployed is not None else False
        self._status = status
        self._serving_status = serving_status
        self._candidate_status = candidate_status

    def describe(self):
        """Print a description of the deployment state"""
        util.pretty_print(self)

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return PredictorState(*cls.extract_fields_from_json(json_decamelized))

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        hip = util.extract_field_from_json(json_decamelized, "hopsworks_inference_path")
        msip = util.extract_field_from_json(
            json_decamelized, "model_server_inference_path"
        )
        ipt = util.extract_field_from_json(json_decamelized, "internal_port")
        r = util.extract_field_from_json(json_decamelized, "revision")
        d = util.extract_field_from_json(json_decamelized, "deployed")
        s = util.extract_field_from_json(json_decamelized, "status")
        ss = PredictorStateInternal.from_json(json_decamelized.pop("serving_status"))
        cs = PredictorStateInternal.from_json(json_decamelized.pop("candidate_status")) if "candidate_status" in json_decamelized else None
        return hip, msip, ipt, r, d, s, ss, cs

    def to_dict(self):
        json = {
            "serving_status": self._serving_status,
            "hopsworksInferencePath": self._hopsworks_inference_path,
            "modelServerInferencePath": self._model_server_inference_path,
            "status": self._status,
        }

        if self._candidate_status is not None:
            json["candidateStatus"] = self._candidate_status
        if self._internal_port is not None:
            json["internalPort"] = self._internal_port
        if self._revision is not None:
            json["revision"] = self._revision
        if self._deployed is not None:
            json["deployed"] = self._deployed

        return json

    @property
    def hopsworks_inference_path(self):
        """Inference path in the Hopsworks REST API."""
        return self._hopsworks_inference_path

    @property
    def model_server_inference_path(self):
        """Inference path in the model server"""
        return self.model_server_inference_path

    @property
    def internal_port(self):
        """Internal port for the predictor."""
        return self._internal_port

    @property
    def revision(self):
        """Last revision of the predictor."""
        return self._revision

    @property
    def deployed(self):
        """Whether the predictor is deployed or not."""
        return self._deployed

    @property
    def status(self):
        """Overall status of the predictor including the candidate if is available"""
        return self._status

    @property
    def serving_status(self):
        """Status of the main serving"""
        return self._serving_status

    @property
    def candidate_status(self):
        """Status of the candidate serving"""
        return self._candidate_status

    def __repr__(self):
        return f"PredictorState(status: {self.status.capitalize()!r})"
