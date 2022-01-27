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
from typing import List, Optional

from hsml import util


class PredictorState:
    """State of a Predictor."""

    def __init__(
        self,
        available_predictor_instances: int,
        available_transformer_instances: Optional[int],
        internal_ips: List[str],
        internal_path: str,
        internal_port: Optional[int],
        external_ip: Optional[str],
        external_port: Optional[int],
        revision: Optional[int],
        deployed: Optional[bool],
        conditions: Optional[List[str]],
        status: str,
    ):
        self._available_predictor_instances = available_predictor_instances
        self._available_transformer_instances = available_transformer_instances
        self._internal_ips = internal_ips
        self._internal_path = internal_path
        self._internal_port = internal_port
        self._external_ip = external_ip
        self._external_port = external_port
        self._revision = revision
        self._deployed = deployed or False
        self._conditions = conditions
        self._status = status

    def describe(self):
        util.pretty_print(self)

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return PredictorState(*cls.extract_fields_from_json(json_decamelized))

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        ai = (
            json_decamelized.pop("available_instances")
            if "available_instances" in json_decamelized
            else None
        )
        ati = (
            json_decamelized.pop("available_transformer_instances")
            if "available_transformer_instances" in json_decamelized
            else None
        )
        ii = (
            json_decamelized.pop("internal_ips")
            if "internal_ips" in json_decamelized
            else None
        )
        iph = (
            json_decamelized.pop("internal_path")
            if "internal_path" in json_decamelized
            else None
        )
        ipt = (
            json_decamelized.pop("internal_port")
            if "internal_port" in json_decamelized
            else None
        )
        ei = (
            json_decamelized.pop("external_ip")
            if "external_ip" in json_decamelized
            else None
        )
        ep = (
            json_decamelized.pop("external_port")
            if "external_port" in json_decamelized
            else None
        )
        r = json_decamelized.pop("revision") if "revision" in json_decamelized else None
        d = json_decamelized.pop("deployed") if "deployed" in json_decamelized else None
        c = (
            json_decamelized.pop("conditions")
            if "conditions" in json_decamelized
            else None
        )
        s = json_decamelized.pop("status") if "status" in json_decamelized else None

        return ai, ati, ii, iph, ipt, ei, ep, r, d, c, s

    def to_dict(self):
        json = {
            "availableInstances": self._available_predictor_instances,
            "internalIPs": self._internal_ips,
            "internalPath": self._internal_path,
            "status": self._status,
        }

        if self._available_transformer_instances is not None:
            json[
                "availableTransformerInstances"
            ] = self._available_transformer_instances
        if self._internal_port is not None:
            json["internalPort"] = self._internal_port
        if self._external_ip is not None:
            json["externalIP"] = self._external_ip
        if self._external_port is not None:
            json["externalPort"] = self.external_port
        if self._revision is not None:
            json["revision"] = self._revision
        if self._deployed is not None:
            json["deployed"] = self._deployed
        if self._conditions is not None:
            json["conditions"] = self._conditions

        return json

    @property
    def available_predictor_instances(self):
        """Available instances of the predictor."""
        return self._available_predictor_instances

    @property
    def available_transformer_instances(self):
        """Available instances of the transformer."""
        return self._available_transformer_instances

    @property
    def internal_ips(self):
        """Internal IPs of the predictor."""
        return self._internal_ips

    @property
    def internal_path(self):
        """Internal path to the predictor."""
        return self._internal_path

    @property
    def internal_port(self):
        """Internal port of the predictor."""
        return self._internal_port

    @property
    def external_ip(self):
        """External IP of the predictor."""
        return self._external_ip

    @property
    def external_port(self):
        """External port of the predictor."""
        return self._external_port

    @property
    def revision(self):
        """Revision of the predictor."""
        return self._revision

    @property
    def deployed(self):
        """Whether the predictor is deployed."""
        return self._deployed

    @property
    def conditions(self):
        """Conditions of the predictor."""
        return self._conditions

    @property
    def status(self):
        """Status of the predictor."""
        return self._status
