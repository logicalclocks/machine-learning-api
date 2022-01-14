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

import json
import tempfile
import uuid
import time
import importlib
import os

from tqdm.auto import tqdm

from hsml.client.exceptions import RestAPIError, ModelRegistryException

from hsml import client, util, constants

from hsml.core import model_api, dataset_api

from hsml.engine import local_engine, hopsworks_engine


class ModelEngine:
    def __init__(self):
        self._model_api = model_api.ModelApi()
        self._dataset_api = dataset_api.DatasetApi()

        pydoop_spec = importlib.util.find_spec("pydoop")
        if pydoop_spec is None:
            self._engine = local_engine.LocalEngine()
        else:
            self._engine = hopsworks_engine.HopsworksEngine()

    def _poll_model_available(self, model_instance, await_registration):
        if await_registration > 0:
            model_registry_id = model_instance.model_registry_id
            sleep_seconds = 5
            for i in range(int(await_registration / sleep_seconds)):
                try:
                    time.sleep(sleep_seconds)
                    model_meta = self._model_api.get(
                        model_instance.name,
                        model_instance.version,
                        model_registry_id,
                        model_instance.shared_registry_project_name,
                    )
                    if model_meta is not None:
                        return model_meta
                except RestAPIError as e:
                    if e.response.status_code != 404:
                        raise e
            print(
                "Model not available during polling, set a higher value for await_registration to wait longer."
            )

    def _upload_additional_resources(self, model_instance):
        if model_instance._input_example is not None:
            input_example_path = os.path.join(os.getcwd(), "input_example.json")
            input_example = util.input_example_to_json(model_instance._input_example)

            with open(input_example_path, "w+") as out:
                json.dump(input_example, out, cls=util.NumpyEncoder)

            self._dataset_api.upload(input_example_path, model_instance.version_path)
            os.remove(input_example_path)
            model_instance.input_example = None
        if model_instance._model_schema is not None:
            model_schema_path = os.path.join(os.getcwd(), "model_schema.json")
            model_schema = model_instance._model_schema

            with open(model_schema_path, "w+") as out:
                out.write(model_schema.json())

            self._dataset_api.upload(model_schema_path, model_instance.version_path)
            os.remove(model_schema_path)
            model_instance.model_schema = None
        return model_instance

    def _copy_hopsfs_model(self, existing_model_path, model_version_path):
        # Strip hdfs prefix
        if existing_model_path.startswith("hdfs:/"):
            projects_index = existing_model_path.find("/Projects", 0)
            existing_model_path = existing_model_path[projects_index:]

        for entry in self._dataset_api.list(existing_model_path, sort_by="NAME:desc")[
            "items"
        ]:
            path = entry["attributes"]["path"]
            _, file_name = os.path.split(path)
            self._dataset_api.copy(path, model_version_path + "/" + file_name)

    def _upload_local_model_folder(
        self, local_model_path, model_version, dataset_model_name_path
    ):
        archive_out_dir = None
        uploaded_archive_path = None
        try:
            archive_out_dir = tempfile.TemporaryDirectory(dir=os.getcwd())
            archive_path = util.compress(
                archive_out_dir.name, str(model_version), local_model_path
            )
            uploaded_archive_path = (
                dataset_model_name_path + "/" + os.path.basename(archive_path)
            )
            self._dataset_api.upload(archive_path, dataset_model_name_path)
            self._dataset_api.unzip(uploaded_archive_path, block=True, timeout=600)
        except RestAPIError:
            raise
        finally:
            if archive_out_dir is not None:
                archive_out_dir.cleanup()
            self._dataset_api.rm(uploaded_archive_path)

    def _set_model_version(
        self, model_instance, dataset_models_root_path, dataset_model_path
    ):
        # Set model version if not defined
        if model_instance._version is None:
            current_highest_version = 0
            for item in self._dataset_api.list(dataset_model_path, sort_by="NAME:desc")[
                "items"
            ]:
                _, file_name = os.path.split(item["attributes"]["path"])
                try:
                    try:
                        current_version = int(file_name)
                    except ValueError:
                        continue
                    if current_version > current_highest_version:
                        current_highest_version = current_version
                except RestAPIError:
                    pass
            model_instance._version = current_highest_version + 1

        elif self._dataset_api.path_exists(
            dataset_models_root_path
            + "/"
            + model_instance._name
            + "/"
            + str(model_instance._version)
        ):
            raise ModelRegistryException(
                "Model with name {} and version {} already exists".format(
                    model_instance._name, model_instance._version
                )
            )
        return model_instance

    def _build_resource_path(self, model_instance, artifact):
        artifact_path = "{}/{}".format(model_instance.version_path, artifact)
        return artifact_path

    def save(self, model_instance, model_path, await_registration=480):

        _client = client.get_instance()

        is_shared_registry = model_instance.shared_registry_project_name is not None

        if is_shared_registry:
            dataset_models_root_path = "{}::{}".format(
                model_instance.shared_registry_project_name,
                constants.MODEL_SERVING.MODELS_DATASET,
            )
            model_instance._project_name = model_instance.shared_registry_project_name
        else:
            dataset_models_root_path = constants.MODEL_SERVING.MODELS_DATASET
            model_instance._project_name = _client._project_name

        if model_instance._training_metrics is not None:
            util.validate_metrics(model_instance._training_metrics)

        if not self._dataset_api.path_exists(dataset_models_root_path):
            raise AssertionError(
                "{} dataset does not exist in this project. Please enable the Serving service or create it manually.".format(
                    dataset_models_root_path
                )
            )

        # Create /Models/{model_instance._name} folder
        dataset_model_name_path = dataset_models_root_path + "/" + model_instance._name
        if not self._dataset_api.path_exists(dataset_model_name_path):
            self._dataset_api.mkdir(dataset_model_name_path)

        model_instance = self._set_model_version(
            model_instance, dataset_models_root_path, dataset_model_name_path
        )

        # Attach model summary xattr to /Models/{model_instance._name}/{model_instance._version}
        model_query_params = {}

        if "ML_ID" in os.environ:
            model_instance._experiment_id = os.environ["ML_ID"]

        model_instance._experiment_project_name = _client._project_name

        if "HOPSWORKS_JOB_NAME" in os.environ:
            model_query_params["jobName"] = os.environ["HOPSWORKS_JOB_NAME"]
        elif "HOPSWORKS_KERNEL_ID" in os.environ:
            model_query_params["kernelId"] = os.environ["HOPSWORKS_KERNEL_ID"]

        pbar = tqdm(
            [
                {"id": 0, "desc": "Creating model folder"},
                {"id": 1, "desc": "Uploading input_example and model_schema"},
                {"id": 2, "desc": "Uploading model files"},
                {"id": 3, "desc": "Registering model"},
                {"id": 4, "desc": "Waiting for model registration"},
                {"id": 5, "desc": "Model export complete"},
            ]
        )

        for step in pbar:
            try:
                pbar.set_description("%s" % step["desc"])
                if step["id"] == 0:
                    # Create folders
                    self._engine.mkdir(model_instance)
                if step["id"] == 1:
                    model_instance = self._upload_additional_resources(model_instance)
                if step["id"] == 2:
                    # Upload Model files from local path to /Models/{model_instance._name}/{model_instance._version}
                    # check local absolute
                    if os.path.exists(model_path):
                        self._upload_local_model_folder(
                            model_path,
                            model_instance.version,
                            dataset_model_name_path,
                        )
                    # check local relative
                    elif os.path.exists(
                        os.path.join(os.getcwd(), model_path)
                    ):  # check local relative
                        self._upload_local_model_folder(
                            os.path.join(os.getcwd(), model_path),
                            model_instance.version,
                            dataset_model_name_path,
                        )
                    # check project relative
                    elif self._dataset_api.path_exists(
                        model_path
                    ):  # check hdfs relative and absolute
                        self._copy_hopsfs_model(model_path, model_instance.version_path)
                    else:
                        raise IOError(
                            "Could not find path {} in the local filesystem or in HopsFS".format(
                                model_path
                            )
                        )
                if step["id"] == 3:
                    model_instance = self._model_api.put(
                        model_instance, model_query_params
                    )
                if step["id"] == 4:
                    model_instance = self._poll_model_available(
                        model_instance, await_registration
                    )
                if step["id"] == 5:
                    pass
            except BaseException as be:
                self._dataset_api.rm(model_instance.version_path)
                raise be

        print(
            "Exported model {} with version {}".format(
                model_instance.name, model_instance.version
            )
        )

        return model_instance

    def download(self, model_instance):
        model_name_path = os.path.join(
            os.getcwd(), str(uuid.uuid4()), model_instance._name
        )
        model_version_path = model_name_path + "/" + str(model_instance._version)
        zip_path = model_version_path + ".zip"
        os.makedirs(model_name_path)

        temp_download_dir = "/Resources" + "/" + str(uuid.uuid4())
        try:
            self._dataset_api.mkdir(temp_download_dir)
            self._dataset_api.zip(
                model_instance.version_path,
                destination_path=temp_download_dir,
                block=True,
                timeout=600,
            )
            self._dataset_api.download(
                temp_download_dir + "/" + str(model_instance._version) + ".zip",
                zip_path,
            )
            self._dataset_api.rm(temp_download_dir)
            util.decompress(zip_path, extract_dir=model_name_path)
            os.remove(zip_path)
        except BaseException as be:
            raise be
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            self._dataset_api.rm(temp_download_dir)

        return model_version_path

    def read_file(self, model_instance, resource):
        hdfs_resource_path = self._build_resource_path(
            model_instance, os.path.basename(resource)
        )
        if self._dataset_api.path_exists(hdfs_resource_path):
            try:
                resource = os.path.basename(resource)
                tmp_dir = tempfile.TemporaryDirectory(dir=os.getcwd())
                local_resource_path = os.path.join(tmp_dir.name, resource)
                self._dataset_api.download(
                    hdfs_resource_path,
                    local_resource_path,
                )
                with open(local_resource_path, "r") as f:
                    return f.read()
            finally:
                if tmp_dir is not None and os.path.exists(tmp_dir.name):
                    tmp_dir.cleanup()

    def read_json(self, model_instance, resource):
        hdfs_resource_path = self._build_resource_path(model_instance, resource)
        if self._dataset_api.path_exists(hdfs_resource_path):
            try:
                tmp_dir = tempfile.TemporaryDirectory(dir=os.getcwd())
                local_resource_path = os.path.join(tmp_dir.name, resource)
                self._dataset_api.download(
                    hdfs_resource_path,
                    local_resource_path,
                )
                with open(local_resource_path, "rb") as f:
                    return json.loads(f.read())
            finally:
                if tmp_dir is not None and os.path.exists(tmp_dir.name):
                    tmp_dir.cleanup()

    def delete(self, model_instance):
        self._engine.delete(model_instance)

    def set_tag(self, model_instance, name, value):
        """Attach a name/value tag to a model."""
        self._model_api.set_tag(model_instance, name, value)

    def delete_tag(self, model_instance, name):
        """Remove a tag from a model."""
        self._model_api.delete_tag(model_instance, name)

    def get_tag(self, model_instance, name):
        """Get tag with a certain name."""
        return self._model_api.get_tags(model_instance, name)[name]

    def get_tags(self, model_instance):
        """Get all tags for a model."""
        return self._model_api.get_tags(model_instance)
