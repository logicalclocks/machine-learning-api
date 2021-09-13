# Python Environments (Local or Kubeflow)

Connecting to the Model Registry from any Python environment requires setting up a Model Registry API key and installing the library. This guide explains step by step how to connect to the Model Registry from any Python environment such as your local environment.

## Generate an API key

In Hopsworks, click on your *username* in the top-right corner and select *Settings* to open the user settings. Select *API keys*. Give the key a name and select the project, model_registry, dataset.create, dataset.view, dataset.delete scopes before creating the key. Copy the key into your clipboard.

Create a file called `modelregistry.key` in your designated Python environment and save the API key from your clipboard in the file.

!!! success "Scopes"
    The API key should contain at least the following scopes:

    1. project
    2. model_registry
    3. dataset.create
    4. dataset.view
    5. dataset.delete

<p align="center">
  <figure>
    <img src="../../../assets/images/api-key.png" alt="Generating an API key on Hopsworks">
    <figcaption>API keys can be created in the User Settings on Hopsworks</figcaption>
  </figure>
</p>

!!! info
    You are only able to retrieve the API key once. If you did not manage to copy it to your clipboard, delete it and create a new one.

## Install **HSML**

To be able to access the Hopsworks Model Registry, the `HSML` Python library needs to be installed in the environment from which you want to connect to the Model Registry. You can install the library through pip. We recommend using a Python environment manager such as *virtualenv* or *conda*.

```
pip install hsml~=[HOPSWORKS_VERSION]
```

!!! attention "Matching Hopsworks version"
    The **major version of `HSML`** needs to match the **major version of Hopsworks**.


<p align="center">
    <figure>
        <img src="../../assets/images/hopsworks-version.png" alt="HSML version needs to match the major version of Hopsworks">
        <figcaption>You find the Hopsworks version inside any of your Project's settings tab on Hopsworks</figcaption>
    </figure>
</p>

## Connect to the Model Registry

You are now ready to connect to the Hopsworks Model Registry from your Python environment:

```python
import hsml
conn = hsml.connection(
    host='my_instance',                 # DNS of your Model Registry instance
    port=443,                           # Port to reach your Hopsworks instance, defaults to 443
    project='my_project',               # Name of your Hopsworks Model Registry project
    api_key_value='apikey',             # The API key to authenticate with Hopsworks
    hostname_verification=True          # Disable for self-signed certificates
)
fs = conn.get_model_registry()           # Get the project's default model registry
```

!!! info "Ports"

    If you have trouble to connect, please ensure that your Model Registry can receive incoming traffic from your Python environment on port 443.

## Next Steps

For more information about how to connect, see the [Connection](../generated/project.md) guide.
