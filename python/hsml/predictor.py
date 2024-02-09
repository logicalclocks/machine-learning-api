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
from typing import Union, Optional, Dict

from hsml import util
from hsml import deployment
from hsml import client

from hsml.constants import ARTIFACT_VERSION, PREDICTOR, MODEL
from hsml.predictor_state import PredictorState
from hsml.resources import PredictorResources
from hsml.inference_logger import InferenceLogger
from hsml.predictor_specification import PredictorSpecification


class Predictor:
    """Metadata object representing a predictor in Model Serving."""

    def __init__(
        self,
        name: str,
        specification: Union[Dict, PredictorSpecification],
        candidate_specification: Optional[Union[Dict, PredictorSpecification]] = None,
        serving_tool: Optional[str] = None,
        inference_logger: Optional[Union[InferenceLogger, dict]] = None,  # base
        id: Optional[int] = None,
        description: Optional[str] = None,
        created_at: Optional[str] = None,
        creator: Optional[str] = None,
        candidate_traffic_percentage: Optional[int] = None,
        **kwargs,
    ):
        serving_tool = (
            self._validate_serving_tool(serving_tool)
            or self._get_default_serving_tool()
        )

        main_serving_spec = util.get_obj_from_json(
            specification, PredictorSpecification
        )
        main_serving_spec.resources = self._validate_resources(
            main_serving_spec.resources, serving_tool
        ) or self._get_default_resources(serving_tool)
        self._specification = main_serving_spec
        self._candidate_specification = None
        if candidate_specification is not None:
            candidate_spec = util.get_obj_from_json(
                candidate_specification, PredictorSpecification
            )
            candidate_spec.resources = self._validate_resources(
                candidate_spec.resources, serving_tool
            ) or self._get_default_resources(serving_tool)
            self._candidate_specification = candidate_spec

        self._name = name
        self._serving_tool = serving_tool
        self._id = id
        self._description = description
        self._created_at = created_at
        self._creator = creator
        self._inference_logger = util.get_obj_from_json(
            inference_logger, InferenceLogger
        )
        self._candidate_traffic_percentage = candidate_traffic_percentage

    def deploy(self):
        """Create a deployment for this predictor and persists it in the Model Serving.

        !!! example
            ```python

            import hopsworks

            project = hopsworks.login()

            # get Hopsworks Model Registry handle
            mr = project.get_model_registry()

            # retrieve the trained model you want to deploy
            my_model = mr.get_model("my_model", version=1)

            # get Hopsworks Model Serving handle
            ms = project.get_model_serving()

            my_predictor = ms.create_predictor(my_model)
            my_deployment = my_predictor.deploy()

            print(my_deployment.get_state())
            ```

        # Returns
            `Deployment`. The deployment metadata object of a new or existing deployment.
        """

        _deployment = deployment.Deployment(
            predictor=self, name=self._name, description=self._description
        )
        _deployment.save()

        return _deployment

    def describe(self):
        """Print a description of the predictor"""
        util.pretty_print(self)

    def _set_state(self, state: PredictorState):
        """Set the state of the predictor"""
        self._state = state

    @classmethod
    def _validate_resources(cls, resources, serving_tool):
        if resources is not None:
            # ensure scale-to-zero for kserve deployments when required
            if (
                serving_tool == PREDICTOR.SERVING_TOOL_KSERVE
                and resources.num_instances != 0
                and client.get_serving_num_instances_limits()[0] == 0
            ):
                raise ValueError(
                    "Scale-to-zero is required for KServe deployments in this cluster. Please, set the number of instances to 0."
                )
        return resources

    @classmethod
    def _validate_serving_tool(cls, serving_tool):
        if serving_tool is not None:
            if client.is_saas_connection():
                # only kserve supported in saasy hopsworks
                if serving_tool != PREDICTOR.SERVING_TOOL_KSERVE:
                    raise ValueError(
                        "KServe deployments are the only supported in Serverless Hopsworks"
                    )
                return serving_tool
            # if not saas, check valid serving_tool
            serving_tools = list(util.get_members(PREDICTOR, prefix="SERVING_TOOL"))
            if serving_tool not in serving_tools:
                raise ValueError(
                    "Serving tool '{}' is not valid. Possible values are '{}'".format(
                        serving_tool, ", ".join(serving_tools)
                    )
                )
        return serving_tool

    @classmethod
    def _get_default_resources(cls, serving_tool):
        # enable scale-to-zero by default in kserve deployments
        num_instances = 0 if serving_tool == PREDICTOR.SERVING_TOOL_KSERVE else 1
        return PredictorResources(num_instances)

    @classmethod
    def _get_default_serving_tool(cls):
        # set kserve as default if it is available
        return (
            PREDICTOR.SERVING_TOOL_KSERVE
            if client.is_kserve_installed()
            else PREDICTOR.SERVING_TOOL_DEFAULT
        )

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
        predictor = Predictor(**cls.extract_fields_from_json(json_decamelized))
        predictor._set_state(PredictorState.from_response_json(json_decamelized))
        return predictor

    @classmethod
    def extract_fields_from_json(cls, json_decamelized):
        kwargs = {}
        kwargs["name"] = json_decamelized.pop("name")
        kwargs["description"] = util.extract_field_from_json(
            json_decamelized, "description"
        )
        kwargs["serving_tool"] = json_decamelized.pop("serving_tool")
        kwargs["inference_logger"] = InferenceLogger.from_json(json_decamelized)
        kwargs["id"] = json_decamelized.pop("id")
        kwargs["created_at"] = json_decamelized.pop("created")
        kwargs["creator"] = json_decamelized.pop("creator")
        kwargs["specification"] = PredictorSpecification.from_json(
            json_decamelized.pop("specification")
        )
        kwargs["candidate_specification"] = (
            PredictorSpecification.from_json(
                json_decamelized.pop("candidate_specification")
            )
            if "candidate_specification" in json_decamelized
            else None
        )
        kwargs["candidate_traffic_percentage"] = util.extract_field_from_json(
            json_decamelized, "candidate_traffic_percentage"
        )
        return kwargs

    def update_from_response_json(self, json_dict):
        json_decamelized = humps.decamelize(json_dict)
        self.__init__(**self.extract_fields_from_json(json_decamelized))
        self._set_state(PredictorState.from_response_json(json_decamelized))
        return self

    def json(self):
        return json.dumps(self, cls=util.MLEncoder)

    def to_dict(self):
        json = {
            "id": self._id,
            "name": self._name,
            "description": self._description,
            "created": self._created_at,
            "creator": self._creator,
            "specification": self._specification.to_dict(),
            "servingTool": self._serving_tool,
        }
        if self._candidate_specification is not None:
            json = {**json, **self._candidate_specification.to_dict()}
        if self._candidate_traffic_percentage is not None:
            json = {**json, **self._candidate_traffic_percentage}
        if self._inference_logger is not None:
            json = {**json, **self._inference_logger.to_dict()}
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
    def description(self):
        """Description of the predictor."""
        return self._description

    @description.setter
    def description(self, description: str):
        self._description = description

    @property
    def serving_tool(self):
        """Serving tool used to run the model server."""
        return self._serving_tool

    @serving_tool.setter
    def serving_tool(self, serving_tool: str):
        self._serving_tool = serving_tool

    @property
    def inference_logger(self):
        """Configuration of the inference logger attached to this predictor."""
        return self._inference_logger

    @inference_logger.setter
    def inference_logger(self, inference_logger: InferenceLogger):
        self._inference_logger = inference_logger

    @property
    def created_at(self):
        """Created at date of the predictor."""
        return self._created_at

    @property
    def creator(self):
        """Creator of the predictor."""
        return self._creator

    @property
    def specification(self):
        """The specification of the main predictor"""
        return self._specification

    @specification.setter
    def specification(self, specification: PredictorSpecification):
        self._specification = specification

    @property
    def candidate_specification(self):
        """The specification for the candidate predictor"""
        return self._candidate_specification

    @candidate_specification.setter
    def candidate_specification(self, candidate_specification: PredictorSpecification):
        self._candidate_specification = candidate_specification

    @property
    def candidate_traffic_percentage(self):
        """The traffic percentage for the candidate predictor"""
        return self._candidate_traffic_percentage

    @candidate_traffic_percentage.setter
    def candidate_traffic_percentage(self, candidate_traffic_percentage: int):
        self._candidate_traffic_percentage = candidate_traffic_percentage

    def __repr__(self):
        desc = (
            f", description: {self._description!r}"
            if self._description is not None
            else ""
        )
        return f"Predictor(name: {self._name!r}" + desc + ")"
