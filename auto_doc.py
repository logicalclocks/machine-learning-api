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
    "api/model_registry_api.md": {
        "mr": ["hsml.model_registry.ModelRegistry"],
        "mr_get": ["hsml.connection.Connection.get_model_registry"],
        "mr_properties": keras_autodoc.get_properties(
            "hsml.model_registry.ModelRegistry"
        ),
        "mr_methods": keras_autodoc.get_methods("hsml.model_registry.ModelRegistry"),
    },
}

hsml_dir = pathlib.Path(__file__).resolve().parents[0]


def generate(dest_dir):
    doc_generator = keras_autodoc.DocumentationGenerator(
        PAGES,
        project_url="https://github.com/logicalclocks/models-api/blob/master/python",
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
