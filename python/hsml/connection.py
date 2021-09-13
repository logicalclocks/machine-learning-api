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

import os

from requests.exceptions import ConnectionError

from hsml.decorators import connected, not_connected
from hsml import client
from hsml.core import models_api, model_registry_api

AWS_DEFAULT_REGION = "default"
HOPSWORKS_PORT_DEFAULT = 443
SECRETS_STORE_DEFAULT = "parameterstore"
HOSTNAME_VERIFICATION_DEFAULT = True
CERT_FOLDER_DEFAULT = "hops"


class Connection:
    """A Model registry connection object.

    The connection is project specific, so you can access the project's own model registry.

    This class provides convenience classmethods accessible from the `hsml`-module:

    !!! example "Connection factory"
        For convenience, `hsml` provides a factory method, accessible from the top level
        module, so you don't have to import the `Connection` class manually:

        ```python
        import hsml
        conn = hsml.connection()
        ```

    !!! hint "Save API Key as File"
        To get started quickly, without saving the Hopsworks API in a secret storage,
        you can simply create a file with the previously created Hopsworks API Key and
        place it on the environment from which you wish to connect to the Hopsworks
        Model Registry.

        You can then connect by simply passing the path to the key file when
        instantiating a connection:

        ```python hl_lines="6"
            import hsml
            conn = hsml.connection(
                'my_instance',                      # DNS of your Model Registry instance
                443,                                # Port to reach your Hopsworks instance, defaults to 443
                'my_project',                       # Name of your Hopsworks Model Registry project
                api_key_file='featurestore.key',    # The file containing the API key generated above
                hostname_verification=True)         # Disable for self-signed certificates
            )
            fs = conn.get_feature_store()           # Get the project's default model registry
        ```

    Clients in external clusters need to connect to the Hopsworks Model Registry using an
    API key. The API key is generated inside the Hopsworks platform, and requires at
    least the "project" and "featurestore" scopes to be able to access a model registry.
    For more information, see the [integration guides](../setup.md).

    # Arguments
        host: The hostname of the Hopsworks instance, defaults to `None`.
        port: The port on which the Hopsworks instance can be reached,
            defaults to `443`.
        project: The name of the project to connect to. When running on Hopsworks, this
            defaults to the project from where the client is run from.
            Defaults to `None`.
        engine: Which engine to use, `"spark"`, `"hive"` or `"training"`. Defaults to `None`,
            which initializes the engine to Spark if the environment provides Spark, for
            example on Hopsworks and Databricks, or falls back on Hive if Spark is not
            available, e.g. on local Python environments or AWS SageMaker. This option
            allows you to override this behaviour. `"training"` engine is useful when only
            feature store metadata is needed, for example training dataset location and label
            information when Hopsworks training experiment is conducted.
        region_name: The name of the AWS region in which the required secrets are
            stored, defaults to `"default"`.
        secrets_store: The secrets storage to be used, either `"secretsmanager"`,
            `"parameterstore"` or `"local"`, defaults to `"parameterstore"`.
        hostname_verification: Whether or not to verify Hopsworks certificate, defaults
            to `True`.
        trust_store_path: Path on the file system containing the Hopsworks certificates,
            defaults to `None`.
        cert_folder: The directory to store retrieved HopsFS certificates, defaults to
            `"hops"`. Only required when running without a Spark environment.
        api_key_file: Path to a file containing the API Key, if provided,
            `secrets_store` will be ignored, defaults to `None`.
        api_key_value: API Key as string, if provided, `secrets_store` will be ignored`,
            however, this should be used with care, especially if the used notebook or
            job script is accessible by multiple parties. Defaults to `None`.

    # Returns
        `Connection`. Model Registry connection handle to perform operations on a
            Hopsworks project.
    """

    def __init__(
        self,
        host: str = None,
        port: int = HOPSWORKS_PORT_DEFAULT,
        project: str = None,
        engine: str = None,
        region_name: str = AWS_DEFAULT_REGION,
        secrets_store: str = SECRETS_STORE_DEFAULT,
        hostname_verification: bool = HOSTNAME_VERIFICATION_DEFAULT,
        trust_store_path: str = None,
        cert_folder: str = CERT_FOLDER_DEFAULT,
        api_key_file: str = None,
        api_key_value: str = None,
    ):
        self._host = host
        self._port = port
        self._project = project
        self._engine = engine
        self._region_name = region_name
        self._secrets_store = secrets_store
        self._hostname_verification = hostname_verification
        self._trust_store_path = trust_store_path
        self._cert_folder = cert_folder
        self._api_key_file = api_key_file
        self._api_key_value = api_key_value
        self._connected = False
        self._models_api = models_api.ModelsApi()
        self._model_registry_api = model_registry_api.ModelRegistryApi()

        self.connect()

    @connected
    def get_model_registry(self):
        """Get a reference to a model registry to perform operations on.

        # Returns
            `ModelRegistry`. A model registry handle object to perform operations on.
        """
        return self._model_registry_api.get()

    @not_connected
    def connect(self):
        """Instantiate the connection.

        Creating a `Connection` object implicitly calls this method for you to
        instantiate the connection. However, it is possible to close the connection
        gracefully with the `close()` method, in order to clean up materialized
        certificates. This might be desired when working on external environments such
        as AWS SageMaker. Subsequently you can call `connect()` again to reopen the
        connection.

        !!! example
            ```python
            import hsml
            conn = hsml.connection()
            conn.close()
            conn.connect()
            ```
        """
        self._connected = True
        try:
            # init client
            if client.base.Client.REST_ENDPOINT not in os.environ:
                client.init(
                    "external",
                    self._host,
                    self._port,
                    self._project,
                    self._engine,
                    self._region_name,
                    self._secrets_store,
                    self._hostname_verification,
                    self._trust_store_path,
                    self._cert_folder,
                    self._api_key_file,
                    self._api_key_value,
                )
            else:
                client.init("hopsworks")

            self._models_api = models_api.ModelsApi()
        except (TypeError, ConnectionError):
            self._connected = False
            raise
        print("Connected. Call `.close()` to terminate connection gracefully.")

    def close(self):
        """Close a connection gracefully.

        This will clean up any materialized certificates on the local file system of
        external environments such as AWS SageMaker.

        Usage is recommended but optional.
        """
        client.stop()
        self._models_api = None
        self._connected = False
        print("Connection closed.")

    @classmethod
    def connection(
        cls,
        host: str = None,
        port: int = HOPSWORKS_PORT_DEFAULT,
        project: str = None,
        engine: str = None,
        region_name: str = AWS_DEFAULT_REGION,
        secrets_store: str = SECRETS_STORE_DEFAULT,
        hostname_verification: bool = HOSTNAME_VERIFICATION_DEFAULT,
        trust_store_path: str = None,
        cert_folder: str = CERT_FOLDER_DEFAULT,
        api_key_file: str = None,
        api_key_value: str = None,
    ):
        """Connection factory method, accessible through `hsml.connection()`."""
        return cls(
            host,
            port,
            project,
            engine,
            region_name,
            secrets_store,
            hostname_verification,
            trust_store_path,
            cert_folder,
            api_key_file,
            api_key_value,
        )

    @property
    def host(self):
        return self._host

    @host.setter
    @not_connected
    def host(self, host):
        self._host = host

    @property
    def port(self):
        return self._port

    @port.setter
    @not_connected
    def port(self, port):
        self._port = port

    @property
    def project(self):
        return self._project

    @project.setter
    @not_connected
    def project(self, project):
        self._project = project

    @property
    def region_name(self):
        return self._region_name

    @region_name.setter
    @not_connected
    def region_name(self, region_name):
        self._region_name = region_name

    @property
    def secrets_store(self):
        return self._secrets_store

    @secrets_store.setter
    @not_connected
    def secrets_store(self, secrets_store):
        self._secrets_store = secrets_store

    @property
    def hostname_verification(self):
        return self._hostname_verification

    @hostname_verification.setter
    @not_connected
    def hostname_verification(self, hostname_verification):
        self._hostname_verification = hostname_verification

    @property
    def trust_store_path(self):
        return self._trust_store_path

    @trust_store_path.setter
    @not_connected
    def trust_store_path(self, trust_store_path):
        self._trust_store_path = trust_store_path

    @property
    def cert_folder(self):
        return self._cert_folder

    @cert_folder.setter
    @not_connected
    def cert_folder(self, cert_folder):
        self._cert_folder = cert_folder

    @property
    def api_key_file(self):
        return self._api_key_file

    @property
    def api_key_value(self):
        return self._api_key_value

    @api_key_file.setter
    @not_connected
    def api_key_file(self, api_key_file):
        self._api_key_file = api_key_file

    @api_key_value.setter
    @not_connected
    def api_key_value(self, api_key_value):
        self._api_key_value = api_key_value

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.close()
