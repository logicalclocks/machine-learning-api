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
from typing import Optional

from hsml import util
from hsml.constants import KAFKA_TOPIC_CONFIG


class KafkaTopicConfig:
    """Configuration for a Kafka topic."""

    def __init__(
        self,
        topic_name: str,
        topic_num_replicas: Optional[int] = None,
        topic_num_partitions: Optional[int] = None,
    ):
        self._topic_name = topic_name
        self._topic_num_replicas = topic_num_replicas or KAFKA_TOPIC_CONFIG.NUM_REPLICAS
        self._topic_num_partitions = (
            topic_num_partitions or KAFKA_TOPIC_CONFIG.NUM_PARTITIONS
        )

    def describe(self):
        util.pretty_print(self)

    @classmethod
    def from_response_json(cls, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        return cls.from_json(json_decamelized)

    @classmethod
    def from_json(cls, json_decamelized):
        return KafkaTopicConfig(*cls.extract_fields_from_json(json_decamelized))

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        name = json_decamelized.pop("name")  # required
        tnr = (
            json_decamelized.pop("num_of_replicas")
            if "num_of_replicas" in json_decamelized
            else None
        )
        tnp = (
            json_decamelized.pop("num_of_partitions")
            if "num_of_partitions" in json_decamelized
            else None
        )
        return name, tnr, tnp

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(*self.extract_fields_from_json(json_decamelized))
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        return {
            "kafkaTopicDTO": {
                "name": self._topic_name,
                "numOfReplicas": self._topic_num_replicas,
                "numOfPartitions": self._topic_num_partitions,
            }
        }

    @property
    def topic_name(self):
        """Name of the Kafka topic."""
        return self._topic_name

    @topic_name.setter
    def topic_name(self, topic_name: str):
        self._topic_name = topic_name

    @property
    def topic_num_replicas(self):
        """Number of replicas of the Kafka topic."""
        return self._topic_num_replicas

    @topic_num_replicas.setter
    def topic_num_replicas(self, topic_num_replicas: int):
        self._topic_num_replicas = topic_num_replicas

    @property
    def topic_num_partitions(self):
        """Number of partitions of the Kafka topic."""
        return self._topic_num_partitions

    @topic_num_partitions.setter
    def topic_num_partitions(self, topic_num_partitions: int):
        self._topic_num_partitions = topic_num_partitions
