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

import pathlib
import shutil

import keras_autodoc

PAGES = {
    "project.md": {
        "connection": ["hsml.connection.Connection"],
        "connection_methods": keras_autodoc.get_methods(
            "hsml.connection.Connection", exclude=["connection"]
        ),
    },
    "model.md": {
         "ml_create_tf": ["hsml.model_registry.ModelRegistry.tensorflow.create_model"],
         "ml_get": ["hsml.model_registry.ModelRegistry.get_model"],
         "ml_properties": keras_autodoc.get_properties(
             "hsml.model.Model"
         ),
         "ml_methods": keras_autodoc.get_methods("hsml.model.Model", exclude=["from_response_json", "json", "to_dict", "update_from_response_json", "deploy"]),
    },
    "model_schema.md": {},
    "model_registry.md": {
        "mr_get": ["hsml.connection.Connection.get_model_registry"],
        "mr_properties": keras_autodoc.get_properties(
            "hsml.model_registry.ModelRegistry"
        ),
        "mr_methods": keras_autodoc.get_methods(
            "hsml.model_registry.ModelRegistry", exclude=["from_response_json"]
        ),
    },
    "api/connection_api.md": {
        "connection": ["hsml.connection.Connection"],
        "connection_properties": keras_autodoc.get_properties(
            "hsml.connection.Connection"
        ),
        "connection_methods": keras_autodoc.get_methods("hsml.connection.Connection"),
    },
    "api/model_registry_api.md": {
         "mr": ["hsml.model_registry.ModelRegistry"],
         "mr_get": ["hsml.connection.Connection.get_model_registry"],
         "mr_properties": keras_autodoc.get_properties(
             "hsml.model_registry.ModelRegistry"
         ),
         "mr_methods": keras_autodoc.get_methods("hsml.model_registry.ModelRegistry", exclude=["from_response_json"]),
    },
    "api/model_api.md": {
         "ml_create_tf": ["hsml.model_registry.ModelRegistry.tensorflow.create_model"],
         "ml_create_th": ["hsml.model_registry.ModelRegistry.torch.create_model"],
         "ml_create_sl": ["hsml.model_registry.ModelRegistry.sklearn.create_model"],
         "ml_create_py": ["hsml.model_registry.ModelRegistry.python.create_model"],
         "ml_get": ["hsml.model_registry.ModelRegistry.get_model"],
         "ml_properties": keras_autodoc.get_properties(
             "hsml.model.Model"
        ),
        "ml_methods": keras_autodoc.get_methods("hsml.model.Model", exclude=["from_response_json", "json", "to_dict", "update_from_response_json", "deploy"]),
    },
    "api/model_schema_api.md": {
         "schema": ["hsml.schema.Schema"],
         "schema_dict": ["hsml.schema.Schema.to_dict"],
         "model_schema": ["hsml.model_schema.ModelSchema"],
         "model_schema_dict": ["hsml.model_schema.ModelSchema.to_dict"],
    }
}

hsml_dir = pathlib.Path(__file__).resolve().parents[0]


def generate(dest_dir):
    doc_generator = keras_autodoc.DocumentationGenerator(
        PAGES,
        project_url="https://github.com/logicalclocks/machine-learning-api/blob/master/python",
        template_dir="./docs/templates",
        titles_size="###",
        extra_aliases={},
        max_signature_line_length=100,
    )
    shutil.copyfile(hsml_dir / "CONTRIBUTING.md", dest_dir / "CONTRIBUTING.md")
    shutil.copyfile(hsml_dir / "README.md", dest_dir / "index.md")

    doc_generator.generate(dest_dir / "generated")


if __name__ == "__main__":
    generate(hsml_dir / "docs")
