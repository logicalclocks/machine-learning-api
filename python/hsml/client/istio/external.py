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
#

import os
import requests

from hsml.client import auth, exceptions
from hsml.client.istio import base as istio


class Client(istio.Client):
    def __init__(
        self,
        host,
        port,
        project,
        hostname_verification,
        trust_store_path,
        api_key_file,
        api_key_value,
    ):
        """Initializes a client in an external environment such as AWS Sagemaker."""
        if not host:
            raise exceptions.ExternalClientError(
                "host cannot be of type NoneType, host is a non-optional "
                "argument to connect to hopsworks from an external environment."
            )
        if not project:
            raise exceptions.ExternalClientError(
                "project cannot be of type NoneType, project is a non-optional "
                "argument to connect to hopsworks from an external environment."
            )

        self._host = host
        self._port = port
        self._base_url = "http://" + self._host + ":" + str(self._port)
        self._project_name = project

        if api_key_value is not None:
            api_key = api_key_value
        elif api_key_file is not None:
            file = None
            if os.path.exists(api_key_file):
                try:
                    file = open(api_key_file, mode="r")
                    api_key = file.read()
                finally:
                    file.close()
            else:
                raise IOError(
                    "Could not find api key file on path: {}".format(api_key_file)
                )
        else:
            raise exceptions.ExternalClientError(
                "Either api_key_file or api_key_value must be set when connecting to"
                " hopsworks from an external environment."
            )

        self._auth = auth.ApiKeyAuth(api_key)

        self._session = requests.session()
        self._connected = True
        self._verify = self._get_verify(self._host, trust_store_path)

        self._cert_key = None

    def _close(self):
        """Closes a client."""
        self._connected = False

    def replace_public_host(self, url):
        """no need to replace as we are already in external client"""
        return url

    @property
    def host(self):
        return self._host
