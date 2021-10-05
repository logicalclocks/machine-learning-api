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
    "model_registry.md": {
        "mr_get": ["hsml.connection.Connection.get_model_registry"],
        "mr_properties": keras_autodoc.get_properties(
            "hsml.model_registry.ModelRegistry"
        ),
        "mr_methods": keras_autodoc.get_methods(
            "hsml.model_registry.ModelRegistry", exclude=["from_response_json"]
        ),
    },
    "model.md": {
         "ml_create": ["hsml.model_registry.ModelRegistry.tensorflow"],
         "ml_get": ["hsml.model_registry.ModelRegistry.get_model"],
         "ml_properties": keras_autodoc.get_properties(
             "hsml.model.Model"
         ),
         "ml_methods": keras_autodoc.get_methods("hsml.model.Model", exclude=["from_response_json", "json", "to_dict", "update_from_response_json"]),
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
         "ml": ["hsml.model.Model"],
         "ml_create_tf": ["hsml.model_registry.ModelRegistry.tensorflow"],
         "ml_create_tf_signature": ["hsml.tensorflow.model.Model"],
         "ml_create_th": ["hsml.model_registry.ModelRegistry.torch"],
         "ml_create_th_signature": ["hsml.torch.model.Model"],
         "ml_create_sl": ["hsml.model_registry.ModelRegistry.sklearn"],
         "ml_create_sl_signature": ["hsml.sklearn.model.Model"],
         "ml_create_py": ["hsml.model_registry.ModelRegistry.python"],
         "ml_create_py_signature": ["hsml.python.model.Model"],
         "ml_get": ["hsml.model_registry.ModelRegistry.get_model"],
         "ml_properties": keras_autodoc.get_properties(
             "hsml.model.Model"
         ),
         "ml_methods": keras_autodoc.get_methods("hsml.model.Model", exclude=["from_response_json", "json", "to_dict", "update_from_response_json"]),
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
