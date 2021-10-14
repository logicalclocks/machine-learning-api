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

from hsml.client.exceptions import RestAPIError, ModelRegistryException

from hsml import client, util

from hsml.core import model_api, dataset_api

from hsml.engine import local_engine, hopsworks_engine


class Engine:
    def __init__(self):
        self._model_api = model_api.ModelApi()
        self._dataset_api = dataset_api.DatasetApi()

        pydoop_spec = importlib.util.find_spec("pydoop")
        if pydoop_spec is None:
            self._engine = local_engine.Engine()
        else:
            self._engine = hopsworks_engine.Engine()

    def _poll_model_available(self, model_instance, await_registration):
        if await_registration > 0:
            sleep_seconds = 5
            for i in range(int(await_registration / sleep_seconds)):
                try:
                    time.sleep(sleep_seconds)
                    print(
                        "Polling "
                        + model_instance.name
                        + " version "
                        + str(model_instance.version)
                        + " for model availability."
                    )
                    model = self._model_api.get(
                        name=model_instance.name, version=model_instance.version
                    )
                    if model is None:
                        print(
                            model_instance.name
                            + " not ready yet, retrying in "
                            + str(sleep_seconds)
                            + " seconds."
                        )
                    else:
                        print("Model is now registered.")
                        return model
                except RestAPIError:
                    pass
            print(
                "Model not available during polling, set a higher value for await_registration to wait longer."
            )

    def _upload_additional_resources(self, model_instance, dataset_model_version_path):

        print("upload additionals " + dataset_model_version_path)
        if model_instance.input_example is not None:
            input_example_path = os.getcwd() + "/input_example.json"
            input_example = util.input_example_to_json(model_instance.input_example)

            with open(input_example_path, "w+") as out:
                json.dump(input_example, out, cls=util.NumpyEncoder)

            self._dataset_api.upload(input_example_path, dataset_model_version_path)
            os.remove(input_example_path)
            model_instance.input_example = (
                dataset_model_version_path + "/input_example.json"
            )

        if model_instance.signature is not None:
            signature_path = os.getcwd() + "/signature.json"
            signature = model_instance.signature

            with open(signature_path, "w+") as out:
                out.write(signature.json())

            self._dataset_api.upload(signature_path, dataset_model_version_path)
            os.remove(signature_path)
            model_instance.signature = (
                dataset_model_version_path + "/signature.json"
            )
        return model_instance

    def _copy_hopsfs_model(self, model_path, dataset_model_version_path):
        for item in self._dataset_api.list(model_path, sort_by="NAME:desc")["items"]:
            self._dataset_api.copy(item["attributes"]["path"], dataset_model_version_path)

    def _upload_local_model_folder(self, model_path, dataset_model_version_path):

        print("upload model folder " + dataset_model_version_path)
        zip_out_dir = None
        try:
            zip_out_dir = tempfile.TemporaryDirectory(dir=os.getcwd())
            archive_path = util.zip(zip_out_dir.name, model_path)
            self._dataset_api.upload(archive_path, dataset_model_version_path)
        except RestAPIError:
            raise
        finally:
            if zip_out_dir is not None:
                zip_out_dir.cleanup()

        extracted_archive_path = (
            dataset_model_version_path + "/" + os.path.basename(archive_path)
        )

        self._dataset_api.unzip(extracted_archive_path, block=True, timeout=480)

        self._dataset_api.rm(extracted_archive_path)

        unzipped_model_dir = (
            dataset_model_version_path
            + "/"
            + os.path.splitext(os.path.basename(archive_path))[0]
        )

        # Observed that when unzipping a large folder and directly moving the files sometimes caused filesystem exceptions
        time.sleep(5)

        for artifact in os.listdir(model_path):
            _, file_name = os.path.split(artifact)
            self._dataset_api.move(
                unzipped_model_dir + "/" + file_name,
                dataset_model_version_path + "/" + file_name,
            )

        self._dataset_api.rm(unzipped_model_dir)

    def _set_model_version(self, model_instance, dataset_models_root_path, dataset_model_path):
        # Set model version if not defined
        if model_instance._version is None:
            current_highest_version = 0
            for item in self._dataset_api.list(dataset_model_path, sort_by="NAME:desc")["items"]:
                _, file_name = os.path.split(item["attributes"]["path"])
                try:
                    current_version = int(file_name)
                    if current_version > current_highest_version:
                        current_highest_version = current_version
                except RestAPIError:
                    pass
            model_instance._version = current_highest_version + 1

        elif self._dataset_api.path_exists(dataset_models_root_path + "/" + model_instance._name + "/" + str(model_instance._version)):
              raise ModelRegistryException(
                  "Model with name {} and version {} already exists".format(
                      model_instance._name, model_instance._version
                  )
              )
        print("model version set " + str(model_instance._version))
        return model_instance

    def _build_registry_path(self, model_instance, artifact_path):
        models_path = None
        if model_instance.shared_registry_project is not None:
          models_path = "{}::Models".format(model_instance.shared_registry_project)
        else:
          models_path = "Models"
        return artifact_path.replace("Models", models_path)

    def save(self, model_instance, model_path, await_registration=480):

        #Validate model path existence

        _client = client.get_instance()

        is_shared_registry = model_instance.shared_registry_project is not None

        if is_shared_registry:
          dataset_models_root_path = "{}::Models".format(model_instance.shared_registry_project)
          model_instance._project_name = model_instance.shared_registry_project
        else:
          dataset_models_root_path = "Models"
          model_instance._project_name = _client._project_name

        print("models root path " + dataset_models_root_path)

        if model_instance._training_metrics is not None:
            util.validate_metrics(model_instance._training_metrics)

        if not self._dataset_api.path_exists(dataset_models_root_path):
            raise AssertionError(
                "Models dataset does not exist in this project. Please enable the Serving service or create it manually."
            )
        print(model_instance.shared_registry_project)
        # Create /Models/{model_instance._name} folder
        dataset_model_path = dataset_models_root_path + "/" + model_instance._name
        if not self._dataset_api.path_exists(dataset_model_path):
            self._dataset_api.mkdir(dataset_model_path)

        model_instance = self._set_model_version(model_instance, dataset_models_root_path, dataset_model_path)
        print(model_instance.shared_registry_project)
        print(
            "Exporting model {} with version {}".format(
                model_instance.name, model_instance.version
            )
        )

        dataset_model_version_path = (
           dataset_models_root_path + "/" + model_instance._name + "/" + str(model_instance._version)
        )
        print(model_instance.shared_registry_project)
        try:
            # Create folders
            self._engine.mkdir(model_instance)

            model_query_params = {}

            if "HOPSWORKS_JOB_NAME" in os.environ:
                model_query_params["jobName"] = os.environ["HOPSWORKS_JOB_NAME"]
            elif "HOPSWORKS_KERNEL_ID" in os.environ:
                model_query_params["kernelId"] = os.environ["HOPSWORKS_KERNEL_ID"]

            if "ML_ID" in os.environ:
                model_instance._experiment_id = os.environ["ML_ID"]

            model_instance = self._upload_additional_resources(model_instance, dataset_model_version_path)

            print(model_instance.shared_registry_project)

            # Read the training_dataset location and reattach to model_instance
            if model_instance.training_dataset is not None:
                td_location_split = model_instance.training_dataset.location.split("/")
                for i in range(len(td_location_split)):
                    if td_location_split[i] == "Projects":
                        model_instance._training_dataset = (
                            td_location_split[i + 1]
                            + ":"
                            + model_instance.training_dataset.name
                            + ":"
                            + str(model_instance.training_dataset.version)
                        )

            # Attach model summary xattr to /Models/{model_instance._name}/{model_instance._version}
            self._model_api.put(model_instance, model_query_params)
            print(model_instance.shared_registry_project)

            # Upload Model files from local path to /Models/{model_instance._name}/{model_instance._version}
            if os.path.exists(model_path):
                self._upload_local_model_folder(model_path, dataset_model_version_path)
            elif self._dataset_api.path_exists(model_path):
                self._copy_hopsfs_model(model_path, dataset_model_version_path)

            print(model_instance.shared_registry_project)
            # We do not necessarily have access to the Models REST API for the shared model registry, so we do not know if it is registered or not
            print("poll")
            if not is_shared_registry:
                return self._poll_model_available(model_instance, await_registration)

        except BaseException as be:
            self._dataset_api.rm(dataset_model_version_path)
            raise be

    def download(self, model_instance):
        model_name_path = (
            os.getcwd() + "/" + str(uuid.uuid4()) + "/" + model_instance._name
        )
        model_version_path = model_name_path + "/" + str(model_instance._version)
        zip_path = model_version_path + ".zip"
        os.makedirs(model_name_path)

        dataset_model_name_path = "Models/" + model_instance._name
        dataset_model_version_path = (
            dataset_model_name_path + "/" + str(model_instance._version)
        )

        temp_download_dir = "/Resources" + "/" + str(uuid.uuid4())
        try:
            self._dataset_api.mkdir(temp_download_dir)
            self._dataset_api.zip(
                dataset_model_version_path,
                destination_path=temp_download_dir,
                block=True,
                timeout=480,
            )
            self._dataset_api.download(
                temp_download_dir + "/" + str(model_instance._version) + ".zip",
                zip_path,
            )
            self._dataset_api.rm(temp_download_dir)
            util.unzip(zip_path, extract_dir=model_name_path)
            os.remove(zip_path)
        except BaseException as be:
            raise be
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)
            self._dataset_api.rm(temp_download_dir)

        return model_version_path

    def read_input_example(self, model_instance):
        try:
            tmp_dir = tempfile.TemporaryDirectory(dir=os.getcwd())
            self._dataset_api.download(
              self._build_registry_path(model_instance, model_instance._input_example),
              tmp_dir.name + "/inputs.json"
            )
            with open(tmp_dir.name + "/inputs.json", "rb") as f:
                return json.loads(f.read())
        finally:
            if tmp_dir is not None and os.path.exists(tmp_dir.name):
                tmp_dir.cleanup()

    def read_environment(self, model_instance):
        try:
            tmp_dir = tempfile.TemporaryDirectory(dir=os.getcwd())
            self._dataset_api.download(
              self._build_registry_path(model_instance, model_instance._environment[0]),
              tmp_dir.name + "/environment.yml"
            )
            with open(tmp_dir.name + "/environment.yml", "r") as f:
                return f.read()
        finally:
            if tmp_dir is not None and os.path.exists(tmp_dir.name):
                tmp_dir.cleanup()

    def read_signature(self, model_instance):
        try:
            tmp_dir = tempfile.TemporaryDirectory(dir=os.getcwd())
            self._dataset_api.download(
              self._build_registry_path(model_instance, model_instance._signature),
              tmp_dir.name + "/signature.json"
            )
            with open(tmp_dir.name + "/signature.json", "rb") as f:
                return json.loads(f.read())
        finally:
            if tmp_dir is not None and os.path.exists(tmp_dir.name):
                tmp_dir.cleanup()

    def delete(self, model_instance):
        self._engine.delete(model_instance)

    def add_tag(self, model, name, value):
        """Attach a name/value tag to a feature group."""
        self._dataset_api.add(model.path, name, value)

    def delete_tag(self, model, name):
        """Remove a tag from a feature group."""
        self._dataset_api.delete(model.path, name)

    def get_tag(self, model, name):
        """Get tag with a certain name."""
        return self._dataset_api.get_tags(model.path, name)[name]

    def get_tags(self, model):
        """Get all tags for a feature group."""
        return self._dataset_api.get_tags(model.path)
