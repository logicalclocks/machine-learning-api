#
#   Copyright 2024 Hopsworks AB
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

import pytest
import copy

from hsml import resources
from hsml.constants import RESOURCES

SERVING_RESOURCE_LIMITS = {"cores": 2, "memory": 516, "gpus": 2}


class TestResources:

    # Resources

    def test_from_response_json_cpus(self, backend_fixtures):
        # Arrange
        json = backend_fixtures["resources"]["get_only_cores"]["response"]

        # Act
        r = resources.Resources.from_response_json(json)

        # Assert
        assert r.cores == json["cores"]
        assert r.memory is None
        assert r.gpus is None

    def test_from_response_json_memory(self, backend_fixtures):
        # Arrange
        json = backend_fixtures["resources"]["get_only_memory"]["response"]

        # Act
        r = resources.Resources.from_response_json(json)

        # Assert
        assert r.cores is None
        assert r.memory is json["memory"]
        assert r.gpus is None

    def test_from_response_json_gpus(self, backend_fixtures):
        # Arrange
        json = backend_fixtures["resources"]["get_only_gpus"]["response"]

        # Act
        r = resources.Resources.from_response_json(json)

        # Assert
        assert r.cores is None
        assert r.memory is None
        assert r.gpus == json["gpus"]

    def test_from_response_json_cores_and_memory(self, backend_fixtures):
        # Arrange
        json = backend_fixtures["resources"]["get_cores_and_memory"]["response"]

        # Act
        r = resources.Resources.from_response_json(json)

        # Assert
        assert r.cores == json["cores"]
        assert r.memory == json["memory"]
        assert r.gpus is None

    def test_from_response_json_cores_and_gpus(self, backend_fixtures):
        # Arrange
        json = backend_fixtures["resources"]["get_cores_and_gpus"]["response"]

        # Act
        r = resources.Resources.from_response_json(json)

        # Assert
        assert r.cores == json["cores"]
        assert r.memory is None
        assert r.gpus == json["gpus"]

    def test_from_response_json_memory_and_gpus(self, backend_fixtures):
        # Arrange
        json = backend_fixtures["resources"]["get_memory_and_gpus"]["response"]

        # Act
        r = resources.Resources.from_response_json(json)

        # Assert
        assert r.cores is None
        assert r.memory == json["memory"]
        assert r.gpus == json["gpus"]

    def test_from_response_json_cores_memory_and_gpus(self, backend_fixtures):
        # Arrange
        json = backend_fixtures["resources"]["get_cores_memory_and_gpus"]["response"]

        # Act
        r = resources.Resources.from_response_json(json)

        # Assert
        assert r.cores == json["cores"]
        assert r.memory == json["memory"]
        assert r.gpus == json["gpus"]

    # ComponentResources

    # - from response json

    def test_from_response_json_component_resources(self, mocker):
        # Arrange
        res = {"something": "here"}
        json_decamelized = {"key": "value"}
        mock_humps_decamelize = mocker.patch(
            "humps.decamelize", return_value=json_decamelized
        )
        mock_from_json = mocker.patch(
            "hsml.resources.ComponentResources.from_json",
            return_value="from_json_result",
        )

        # Act
        result = resources.ComponentResources.from_response_json(res)

        # Assert
        assert result == "from_json_result"
        mock_humps_decamelize.assert_called_once_with(res)
        mock_from_json.assert_called_once_with(json_decamelized)

    # - constructor

    def test_constructor_component_resources_default(self, mocker, backend_fixtures):
        # Arrange
        json = backend_fixtures["resources"][
            "get_component_resources_num_instances_requests_and_limits"
        ]["response"]
        mock_default_resource_limits = mocker.patch(
            "hsml.resources.ComponentResources._get_default_resource_limits",
            return_value="limits",
        )
        mock_validate_resources = mocker.patch(
            "hsml.resources.ComponentResources._validate_resources"
        )
        mock_resources_init = mocker.patch(
            "hsml.resources.Resources.__init__", return_value=None
        )

        # Act
        pr = resources.PredictorResources(num_instances=json["num_instances"])

        # Assert
        assert pr.num_instances == json["num_instances"]
        mock_default_resource_limits.assert_called_once()
        mock_validate_resources.assert_called_once_with(pr._requests, pr._limits)
        mock_resources_init.assert_called_once_with(
            RESOURCES.MIN_CORES, RESOURCES.MIN_MEMORY, RESOURCES.MIN_GPUS
        )

    def test_constructor_component_resources(self, mocker, backend_fixtures):
        # Arrange
        json = backend_fixtures["resources"][
            "get_component_resources_num_instances_requests_and_limits"
        ]["response"]
        mock_util_get_obj_from_json = mocker.patch(
            "hsml.util.get_obj_from_json",
            side_effect=[json["requests"], json["limits"]],
        )
        mock_default_resource_limits = mocker.patch(
            "hsml.resources.ComponentResources._get_default_resource_limits",
            return_value="limits",
        )
        mock_validate_resources = mocker.patch(
            "hsml.resources.ComponentResources._validate_resources"
        )

        # Act
        pr = resources.PredictorResources(
            num_instances=json["num_instances"],
            requests=json["requests"],
            limits=json["limits"],
        )

        # Assert
        assert pr.num_instances == json["num_instances"]
        assert pr.requests == json["requests"]
        assert pr.limits == json["limits"]
        mock_default_resource_limits.assert_not_called()
        mock_validate_resources.assert_called_once_with(pr._requests, pr._limits)
        mock_util_get_obj_from_json.call_count == 2

    # - extract fields from json

    def test_extract_fields_from_json_component_resources_with_key(
        self, backend_fixtures
    ):
        # Arrange
        json = backend_fixtures["resources"][
            "get_component_resources_requested_instances_and_predictor_resources"
        ]["response"]
        copy_json = copy.deepcopy(json)
        resources.ComponentResources.RESOURCES_CONFIG_KEY = "predictor_resources"
        resources.ComponentResources.NUM_INSTANCES_KEY = "requested_instances"

        # Act
        kwargs = resources.ComponentResources.extract_fields_from_json(copy_json)

        # Assert
        assert kwargs["num_instances"] == json["requested_instances"]
        assert isinstance(kwargs["requests"], resources.Resources)
        assert (
            kwargs["requests"].cores == json["predictor_resources"]["requests"]["cores"]
        )
        assert (
            kwargs["requests"].memory
            == json["predictor_resources"]["requests"]["memory"]
        )
        assert (
            kwargs["requests"].gpus == json["predictor_resources"]["requests"]["gpus"]
        )
        assert isinstance(kwargs["limits"], resources.Resources)
        assert kwargs["limits"].cores == json["predictor_resources"]["limits"]["cores"]
        assert (
            kwargs["limits"].memory == json["predictor_resources"]["limits"]["memory"]
        )
        assert kwargs["limits"].gpus == json["predictor_resources"]["limits"]["gpus"]

    def test_extract_fields_from_json_component_resources(
        self, mocker, backend_fixtures
    ):
        # Arrange
        json = backend_fixtures["resources"][
            "get_component_resources_requested_instances_and_predictor_resources_alternative"
        ]["response"]
        copy_json = copy.deepcopy(json)
        resources.ComponentResources.RESOURCES_CONFIG_KEY = "predictor_resources"
        resources.ComponentResources.NUM_INSTANCES_KEY = "requested_instances"

        # Act
        kwargs = resources.ComponentResources.extract_fields_from_json(copy_json)

        # Assert
        assert kwargs["num_instances"] == json["num_instances"]
        assert isinstance(kwargs["requests"], resources.Resources)
        assert kwargs["requests"].cores == json["resources"]["requests"]["cores"]
        assert kwargs["requests"].memory == json["resources"]["requests"]["memory"]
        assert kwargs["requests"].gpus == json["resources"]["requests"]["gpus"]
        assert isinstance(kwargs["limits"], resources.Resources)
        assert kwargs["limits"].cores == json["resources"]["limits"]["cores"]
        assert kwargs["limits"].memory == json["resources"]["limits"]["memory"]
        assert kwargs["limits"].gpus == json["resources"]["limits"]["gpus"]

    def test_extract_fields_from_json_component_resources_flatten(
        self, backend_fixtures
    ):
        # Arrange
        json = backend_fixtures["resources"][
            "get_component_resources_num_instances_requests_and_limits"
        ]["response"]
        copy_json = copy.deepcopy(json)
        resources.ComponentResources.RESOURCES_CONFIG_KEY = "predictor_resources"
        resources.ComponentResources.NUM_INSTANCES_KEY = "requested_instances"

        # Act
        kwargs = resources.ComponentResources.extract_fields_from_json(copy_json)

        # Assert
        assert kwargs["num_instances"] == json["num_instances"]
        assert isinstance(kwargs["requests"], resources.Resources)
        assert kwargs["requests"].cores == json["requests"]["cores"]
        assert kwargs["requests"].memory == json["requests"]["memory"]
        assert kwargs["requests"].gpus == json["requests"]["gpus"]
        assert isinstance(kwargs["limits"], resources.Resources)
        assert kwargs["limits"].cores == json["limits"]["cores"]
        assert kwargs["limits"].memory == json["limits"]["memory"]
        assert kwargs["limits"].gpus == json["limits"]["gpus"]

    # - get default resource limits

    def test_get_default_resource_limits_no_hard_limit_and_lower_than_default(
        self, mocker
    ):
        # Arrange
        no_limit_res = {"cores": -1, "memory": -1, "gpus": -1}
        mock_comp_res = mocker.MagicMock()
        mock_comp_res._requests = resources.Resources(cores=0.2, memory=516, gpus=0)
        mock_comp_res._default_resource_limits = (
            resources.ComponentResources._get_default_resource_limits
        )
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=no_limit_res,  # no upper limit
        )

        # Act
        res = mock_comp_res._default_resource_limits(mock_comp_res)

        # Assert
        assert isinstance(res, resources.Resources)
        assert res.cores == RESOURCES.MAX_CORES
        assert res.memory == RESOURCES.MAX_MEMORY
        assert res.gpus == RESOURCES.MAX_GPUS
        mock_get_serving_res_limits.assert_called_once()

    def test_get_default_resource_limits_no_hard_limit_and_higher_than_default(
        self, mocker
    ):
        # Arrange
        no_limit_res = {"cores": -1, "memory": -1, "gpus": -1}
        mock_comp_res = mocker.MagicMock()
        mock_comp_res._requests = resources.Resources(cores=4, memory=2048, gpus=2)
        mock_comp_res._default_resource_limits = (
            resources.ComponentResources._get_default_resource_limits
        )
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=no_limit_res,  # no upper limit
        )

        # Act
        res = mock_comp_res._default_resource_limits(mock_comp_res)

        # Assert
        assert isinstance(res, resources.Resources)
        assert res.cores == mock_comp_res._requests.cores
        assert res.memory == mock_comp_res._requests.memory
        assert res.gpus == mock_comp_res._requests.gpus
        mock_get_serving_res_limits.assert_called_once()

    def test_get_default_resource_limits_with_higher_hard_limit_and_lower_than_default(
        self, mocker
    ):
        # Arrange
        hard_limit_res = {"cores": 3, "memory": 3072, "gpus": 3}
        mock_comp_res = mocker.MagicMock()
        mock_comp_res._requests = resources.Resources(cores=1, memory=516, gpus=0)
        mock_comp_res._default_resource_limits = (
            resources.ComponentResources._get_default_resource_limits
        )
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        res = mock_comp_res._default_resource_limits(mock_comp_res)

        # Assert
        assert isinstance(res, resources.Resources)
        assert res.cores == RESOURCES.MAX_CORES
        assert res.memory == RESOURCES.MAX_MEMORY
        assert res.gpus == RESOURCES.MAX_GPUS
        mock_get_serving_res_limits.assert_called_once()

    def test_get_default_resource_limits_with_higher_hard_limit_and_higher_than_default(
        self, mocker
    ):
        # Arrange
        hard_limit_res = {"cores": 3, "memory": 3072, "gpus": 3}
        mock_comp_res = mocker.MagicMock()
        mock_comp_res._requests = resources.Resources(cores=3, memory=2048, gpus=1)
        mock_comp_res._default_resource_limits = (
            resources.ComponentResources._get_default_resource_limits
        )
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        res = mock_comp_res._default_resource_limits(mock_comp_res)

        # Assert
        assert isinstance(res, resources.Resources)
        assert res.cores == hard_limit_res["cores"]
        assert res.memory == hard_limit_res["memory"]
        assert res.gpus == hard_limit_res["gpus"]
        mock_get_serving_res_limits.assert_called_once()

    def test_get_default_resource_limits_with_lower_hard_limit_and_lower_than_default(
        self, mocker
    ):
        # Arrange
        RESOURCES.MAX_GPUS = 1  # override default
        hard_limit_res = {"cores": 1, "memory": 516, "gpus": 0}
        mock_comp_res = mocker.MagicMock()
        mock_comp_res._requests = resources.Resources(cores=0.5, memory=256, gpus=0.5)
        mock_comp_res._default_resource_limits = (
            resources.ComponentResources._get_default_resource_limits
        )
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        res = mock_comp_res._default_resource_limits(mock_comp_res)

        # Assert
        assert isinstance(res, resources.Resources)
        assert res.cores == hard_limit_res["cores"]
        assert res.memory == hard_limit_res["memory"]
        assert res.gpus == hard_limit_res["gpus"]
        mock_get_serving_res_limits.assert_called_once()

    def test_get_default_resource_limits_with_lower_hard_limit_and_higher_than_default(
        self, mocker
    ):
        # Arrange
        RESOURCES.MAX_GPUS = 1  # override default
        hard_limit_res = {"cores": 1, "memory": 516, "gpus": 0}
        mock_comp_res = mocker.MagicMock()
        mock_comp_res._requests = resources.Resources(cores=4, memory=4080, gpus=4)
        mock_comp_res._default_resource_limits = (
            resources.ComponentResources._get_default_resource_limits
        )
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        res = mock_comp_res._default_resource_limits(mock_comp_res)

        # Assert
        assert isinstance(res, resources.Resources)
        assert res.cores == hard_limit_res["cores"]
        assert res.memory == hard_limit_res["memory"]
        assert res.gpus == hard_limit_res["gpus"]
        mock_get_serving_res_limits.assert_called_once()

    # - validate resources

    def test_validate_resources_no_hard_limits_valid_resources(self, mocker):
        # Arrange
        no_limit_res = {"cores": -1, "memory": -1, "gpus": -1}
        requests = resources.Resources(cores=1, memory=1024, gpus=0)
        limits = resources.Resources(cores=2, memory=2048, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=no_limit_res,  # upper limit
        )

        # Act
        resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()

    def test_validate_resources_no_hard_limit_invalid_cores_request(self, mocker):
        # Arrange
        no_limit_res = {"cores": -1, "memory": -1, "gpus": -1}
        requests = resources.Resources(cores=0, memory=1024, gpus=0)
        limits = resources.Resources(cores=2, memory=2048, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=no_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert "Requested number of cores must be greater than 0 cores." in str(
            e_info.value
        )

    def test_validate_resources_no_hard_limit_invalid_memory_request(self, mocker):
        # Arrange
        no_limit_res = {"cores": -1, "memory": -1, "gpus": -1}
        requests = resources.Resources(cores=1, memory=0, gpus=0)
        limits = resources.Resources(cores=2, memory=2048, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=no_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert "Requested memory resources must be greater than 0 MB." in str(
            e_info.value
        )

    def test_validate_resources_no_hard_limit_invalid_gpus_request(self, mocker):
        # Arrange
        no_limit_res = {"cores": -1, "memory": -1, "gpus": -1}
        requests = resources.Resources(
            cores=1, memory=1024, gpus=-1
        )  # 0 gpus is accepted
        limits = resources.Resources(cores=2, memory=2048, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=no_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert (
            "Requested number of gpus must be greater than or equal to 0 gpus."
            in str(e_info.value)
        )

    def test_validate_resources_no_hard_limit_cores_request_out_of_range(self, mocker):
        # Arrange
        no_limit_res = {"cores": -1, "memory": -1, "gpus": -1}
        requests = resources.Resources(cores=2, memory=1024, gpus=0)
        limits = resources.Resources(cores=1, memory=2048, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=no_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert (
            f"Requested number of cores cannot exceed the limit of {str(limits.cores)} cores."
            in str(e_info.value)
        )

    def test_validate_resources_no_hard_limit_invalid_memory_request_out_of_range(
        self, mocker
    ):
        # Arrange
        no_limit_res = {"cores": -1, "memory": -1, "gpus": -1}
        requests = resources.Resources(cores=1, memory=2048, gpus=0)
        limits = resources.Resources(cores=2, memory=1024, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=no_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert (
            f"Requested memory resources cannot exceed the limit of {str(limits.memory)} MB."
            in str(e_info.value)
        )

    def test_validate_resources_no_hard_limit_invalid_gpus_request_out_of_range(
        self, mocker
    ):
        # Arrange
        no_limit_res = {"cores": -1, "memory": -1, "gpus": -1}
        requests = resources.Resources(cores=1, memory=1024, gpus=2)
        limits = resources.Resources(cores=2, memory=2048, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=no_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert (
            f"Requested number of gpus cannot exceed the limit of {str(limits.gpus)} gpus."
            in str(e_info.value)
        )

    def test_validate_resources_with_hard_limit_valid_resources(self, mocker):
        # Arrange
        hard_limit_res = {"cores": 3, "memory": 3072, "gpus": 3}
        requests = resources.Resources(cores=1, memory=1024, gpus=0)
        limits = resources.Resources(cores=2, memory=2048, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()

    def test_validate_resources_with_hard_limit_invalid_cores_limit(self, mocker):
        # Arrange
        hard_limit_res = {"cores": 3, "memory": 3072, "gpus": 3}
        requests = resources.Resources(cores=2, memory=1024, gpus=0)
        limits = resources.Resources(cores=0, memory=2048, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert "Limit number of cores must be greater than 0 cores." in str(
            e_info.value
        )

    def test_validate_resources_with_hard_limit_invalid_memory_limit(self, mocker):
        # Arrange
        hard_limit_res = {"cores": 3, "memory": 3072, "gpus": 3}
        requests = resources.Resources(cores=2, memory=1024, gpus=0)
        limits = resources.Resources(cores=1, memory=0, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert "Limit memory resources must be greater than 0 MB." in str(e_info.value)

    def test_validate_resources_with_hard_limit_invalid_gpus_limit(self, mocker):
        # Arrange
        hard_limit_res = {"cores": 3, "memory": 3072, "gpus": 3}
        requests = resources.Resources(cores=2, memory=1024, gpus=0)
        limits = resources.Resources(cores=1, memory=2048, gpus=-1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert "Limit number of gpus must be greater than or equal to 0 gpus." in str(
            e_info.value
        )

    def test_validate_resources_with_hard_limit_invalid_cores_request(self, mocker):
        # Arrange
        hard_limit_res = {"cores": 3, "memory": 3072, "gpus": 3}
        requests = resources.Resources(cores=2, memory=1024, gpus=0)
        limits = resources.Resources(cores=4, memory=2048, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert (
            f"Limit number of cores cannot exceed the maximum of {hard_limit_res['cores']} cores."
            in str(e_info.value)
        )

    def test_validate_resources_with_hard_limit_invalid_memory_request(self, mocker):
        # Arrange
        hard_limit_res = {"cores": 3, "memory": 3072, "gpus": 3}
        requests = resources.Resources(cores=2, memory=1024, gpus=0)
        limits = resources.Resources(cores=3, memory=4076, gpus=1)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert (
            f"Limit memory resources cannot exceed the maximum of {hard_limit_res['memory']} MB."
            in str(e_info.value)
        )

    def test_validate_resources_with_hard_limit_invalid_gpus_request(self, mocker):
        # Arrange
        hard_limit_res = {"cores": 3, "memory": 3072, "gpus": 3}
        requests = resources.Resources(cores=2, memory=1024, gpus=0)
        limits = resources.Resources(cores=3, memory=2048, gpus=4)
        mock_get_serving_res_limits = mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=hard_limit_res,  # upper limit
        )

        # Act
        with pytest.raises(ValueError) as e_info:
            resources.ComponentResources._validate_resources(requests, limits)

        # Assert
        mock_get_serving_res_limits.assert_called_once()
        assert (
            f"Limit number of gpus cannot exceed the maximum of {hard_limit_res['gpus']} gpus."
            in str(e_info.value)
        )

    # PredictorResources

    def test_from_response_json_predictor_resources(self, mocker, backend_fixtures):
        mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=SERVING_RESOURCE_LIMITS,
        )
        json = backend_fixtures["resources"][
            "get_component_resources_num_instances_requests_and_limits"
        ]["response"]

        # Act
        r = resources.PredictorResources.from_response_json(json)

        # Assert
        assert r.num_instances == json["num_instances"]
        assert r.requests.cores == json["requests"]["cores"]
        assert r.requests.memory == json["requests"]["memory"]
        assert r.requests.gpus == json["requests"]["gpus"]
        assert r.limits.cores == json["limits"]["cores"]
        assert r.limits.memory == json["limits"]["memory"]
        assert r.limits.gpus == json["limits"]["gpus"]

    def test_from_response_json_predictor_resources_specific_keys(
        self, mocker, backend_fixtures
    ):
        mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=SERVING_RESOURCE_LIMITS,
        )
        json = backend_fixtures["resources"][
            "get_component_resources_requested_instances_and_predictor_resources"
        ]["response"]

        # Act
        r = resources.PredictorResources.from_response_json(json)

        # Assert
        assert r.num_instances == json["requested_instances"]
        assert r.requests.cores == json["predictor_resources"]["requests"]["cores"]
        assert r.requests.memory == json["predictor_resources"]["requests"]["memory"]
        assert r.requests.gpus == json["predictor_resources"]["requests"]["gpus"]
        assert r.limits.cores == json["predictor_resources"]["limits"]["cores"]
        assert r.limits.memory == json["predictor_resources"]["limits"]["memory"]
        assert r.limits.gpus == json["predictor_resources"]["limits"]["gpus"]

    # TransformerResources

    def test_from_response_json_transformer_resources(self, mocker, backend_fixtures):
        mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=SERVING_RESOURCE_LIMITS,
        )
        json = backend_fixtures["resources"][
            "get_component_resources_num_instances_requests_and_limits"
        ]["response"]

        # Act
        r = resources.TransformerResources.from_response_json(json)

        # Assert
        assert r.num_instances == json["num_instances"]
        assert r.requests.cores == json["requests"]["cores"]
        assert r.requests.memory == json["requests"]["memory"]
        assert r.requests.gpus == json["requests"]["gpus"]
        assert r.limits.cores == json["limits"]["cores"]
        assert r.limits.memory == json["limits"]["memory"]
        assert r.limits.gpus == json["limits"]["gpus"]

    def test_from_response_json_transformer_resources_specific_keys(
        self, mocker, backend_fixtures
    ):
        mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=SERVING_RESOURCE_LIMITS,
        )
        json = backend_fixtures["resources"][
            "get_component_resources_requested_instances_and_transformer_resources"
        ]["response"]

        # Act
        r = resources.TransformerResources.from_response_json(json)

        # Assert
        assert r.num_instances == json["requested_transformer_instances"]
        assert r.requests.cores == json["transformer_resources"]["requests"]["cores"]
        assert r.requests.memory == json["transformer_resources"]["requests"]["memory"]
        assert r.requests.gpus == json["transformer_resources"]["requests"]["gpus"]
        assert r.limits.cores == json["transformer_resources"]["limits"]["cores"]
        assert r.limits.memory == json["transformer_resources"]["limits"]["memory"]
        assert r.limits.gpus == json["transformer_resources"]["limits"]["gpus"]

    def test_from_response_json_transformer_resources_default_limits(
        self, mocker, backend_fixtures
    ):
        mocker.patch(
            "hsml.client.get_serving_resource_limits",
            return_value=SERVING_RESOURCE_LIMITS,
        )
        mocker.patch(
            "hsml.resources.ComponentResources._get_default_resource_limits",
            return_value=resources.Resources(
                cores=SERVING_RESOURCE_LIMITS["cores"],
                memory=SERVING_RESOURCE_LIMITS["memory"],
                gpus=SERVING_RESOURCE_LIMITS["gpus"],
            ),
        )
        json = backend_fixtures["resources"][
            "get_component_resources_num_instances_and_requests"
        ]["response"]

        # Act
        r = resources.TransformerResources.from_response_json(json)

        # Assert
        assert r.num_instances == json["num_instances"]
        assert r.requests.cores == json["requests"]["cores"]
        assert r.requests.memory == json["requests"]["memory"]
        assert r.requests.gpus == json["requests"]["gpus"]
        assert r.limits.cores == SERVING_RESOURCE_LIMITS["cores"]
        assert r.limits.memory == SERVING_RESOURCE_LIMITS["memory"]
        assert r.limits.gpus == SERVING_RESOURCE_LIMITS["gpus"]
