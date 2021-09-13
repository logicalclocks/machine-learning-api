# Project/Connection

In Hopsworks [a Project is a sandboxed set](https://www.logicalclocks.com/blog/how-we-secure-your-data-with-hopsworks) of users, data, and programs (where data can be shared in a controlled manner between projects).

Each Project can have its own Feature Store. However, it is possible to [share Feature Stores](#sharing-a-feature-store) among projects.

When working with the Feature Store from a programming [environment](../setup.md) you can connect to a single Hopsworks instance at a time, but it is possible to access multiple Feature Stores simultaneously.

A connection to a Hopsworks instance is represented by a [`Connection` object](#connection). Its main purpose is to retrieve the API Key if you are connecting from an external environment and subsequently to retrieve the needed certificates to communicate with the Feature Store services.

The [handle](#get_feature_store) can then be used to retrieve a reference to the [Feature Store](../generated/feature_store.md) you want to operate on.

## Examples

=== "Python"

    !!! example "Connecting from Hopsworks"
        ```python
        import hsfs
        conn = hsfs.connection()
        fs = conn.get_feature_store()
        ```

    !!! example "Connecting from Databricks"
        In order to connect from Databricks, follow the [integration guide](../integrations/databricks/configuration.md).

        You can then simply connect by using your chosen way of retrieving the API Key:

        ```python
        import hsfs
        conn = hsfs.connection(
            host="ec2-13-53-124-128.eu-north-1.compute.amazonaws.com",
            project="demo_fs_admin000",
            hostname_verification=False,
            secrets_store="secretsmanager"
            )
        fs = conn.get_feature_store()
        ```

        Alternatively you can pass the API Key as a file or directly:

        !!! note "Azure"
            Use this method when working with Hopsworks on Azure.

        ```python
        import hsfs
        conn = hsfs.connection(
            host="ec2-13-53-124-128.eu-north-1.compute.amazonaws.com",
            project="demo_fs_admin000",
            hostname_verification=False,
            api_key_file="featurestore.key"
            )
        fs = conn.get_feature_store()
        ```

    !!! example "Connecting from AWS SageMaker"
        In order to connect from SageMaker, follow the [integration guide](../integrations/sagemaker.md) to setup the API Key.

        You can then simply connect by using your chosen way of retrieving the API Key:

        ```python
        import hsfs
        conn = hsfs.connection(
            host="ec2-13-53-124-128.eu-north-1.compute.amazonaws.com",
            project="demo_fs_admin000",
            hostname_verification=False,
            secrets_store="secretsmanager"
            )
        fs = conn.get_feature_store()
        ```

        Alternatively you can pass the API Key as a file or directly:

        ```python
        import hsfs
        conn = hsfs.connection(
            host="ec2-13-53-124-128.eu-north-1.compute.amazonaws.com",
            project="demo_fs_admin000",
            hostname_verification=False,
            api_key_file="featurestore.key"
            )
        fs = conn.get_feature_store()
        ```

    !!! example "Connecting from Python environment"
        To connect from a simple Python environment, you can provide the API Key as a
        file as shown in the SageMaker example above, or you provide the value directly:

        ```python
        import hsfs
        conn = hsfs.connection(
            host="ec2-13-53-124-128.eu-north-1.compute.amazonaws.com",
            project="demo_fs_admin000",
            hostname_verification=False,
            api_key_value=(
                "PFcy3dZ6wLXYglRd.ydcdq5jH878IdG7xlL9lHVqrS8v3sBUqQgyR4xbpUgDnB5ZpYro6O"
                "xNnAzJ7RV6H"
                )
            )
        fs = conn.get_feature_store()
        ```

=== "Scala"

    !!! example "Connecting from Hopsworks"
        ```scala
        import com.logicalclocks.hsfs._
        val connection = HopsworksConnection.builder().build();
        val fs = connection.getFeatureStore();
        ```

    !!! example "Connecting from Databricks"
        TBD

    !!! example "Connecting from AWS SageMaker"
        The Scala client version of `hsfs` is not supported on AWS SageMaker,
        please use the Python client.

## Sharing a Feature Store

Connections are on a project-level, however, it is possible to share feature stores among projects, so even if you have a connection to one project, you can retireve a handle to any feature store shared with that project.

To share a feature store, you can follow these steps:

!!! info "Sharing a Feature Store"

    1. Open the project of the feature store that you would like to share on Hopsworks.
    2. Go to the *Data Set* browser and right click the `Featurestore.db` entry.
    3. Click *Share with*, then select *Project* and choose the project you wish to share the feature store with.
    4. Select the permissions level that the project user members should have on the feature store and click *Share*.
    4. Open the project you just shared the feature store with.
    5. Go to the *Data Sets* browser and there you should see the shared feature store as `[project_name_of_shared_feature_store]::Featurestore.db`. Click this entry, you will be asked to accept this shared Dataset, click *Accept*.
    7. You should now have access to this feature store from the other project.

<p align="center">
  <figure>
      <img src="../../assets/images/featurestore-sharing.png" width="500" alt="Sharing a feature store between projects">
    <figcaption>Sharing a feature store between projects</figcaption>
  </figure>
</p>

<p align="center">
  <figure>
      <img src="../../assets/images/featurestore-sharing-2.png" alt="Accepting a shared feature store">
    <figcaption>Accepting a shared feature store from a project</figcaption>
  </figure>
</p>

## Connection Handle

<span style="float:right;">[[source]](https://github.com/logicalclocks/models-api/blob/master/python/hsml/connection.py#L32)</span>

### Connection


```python
hsml.connection.Connection(
    host=None,
    port=443,
    project=None,
    engine=None,
    region_name="default",
    secrets_store="parameterstore",
    hostname_verification=True,
    trust_store_path=None,
    cert_folder="hops",
    api_key_file=None,
    api_key_value=None,
)
```


A Model registry connection object.

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

__Arguments__

- __host__ `Optional[str]`: The hostname of the Hopsworks instance, defaults to `None`.
- __port__ `int`: The port on which the Hopsworks instance can be reached,
    defaults to `443`.
- __project__ `Optional[str]`: The name of the project to connect to. When running on Hopsworks, this
    defaults to the project from where the client is run from.
    Defaults to `None`.
- __engine__ `Optional[str]`: Which engine to use, `"spark"`, `"hive"` or `"training"`. Defaults to `None`,
    which initializes the engine to Spark if the environment provides Spark, for
    example on Hopsworks and Databricks, or falls back on Hive if Spark is not
    available, e.g. on local Python environments or AWS SageMaker. This option
    allows you to override this behaviour. `"training"` engine is useful when only
    feature store metadata is needed, for example training dataset location and label
    information when Hopsworks training experiment is conducted.
- __region_name__ `str`: The name of the AWS region in which the required secrets are
    stored, defaults to `"default"`.
- __secrets_store__ `str`: The secrets storage to be used, either `"secretsmanager"`,
    `"parameterstore"` or `"local"`, defaults to `"parameterstore"`.
- __hostname_verification__ `bool`: Whether or not to verify Hopsworks certificate, defaults
    to `True`.
- __trust_store_path__ `Optional[str]`: Path on the file system containing the Hopsworks certificates,
    defaults to `None`.
- __cert_folder__ `str`: The directory to store retrieved HopsFS certificates, defaults to
    `"hops"`. Only required when running without a Spark environment.
- __api_key_file__ `Optional[str]`: Path to a file containing the API Key, if provided,
    `secrets_store` will be ignored, defaults to `None`.
- __api_key_value__ `Optional[str]`: API Key as string, if provided, `secrets_store` will be ignored`,
    however, this should be used with care, especially if the used notebook or
    job script is accessible by multiple parties. Defaults to `None`.

__Returns__

`Connection`. Model Registry connection handle to perform operations on a
    Hopsworks project.


----



## Methods

<span style="float:right;">[[source]](https://github.com/logicalclocks/models-api/blob/master/python/hsml/connection.py#L195)</span>

### close


```python
Connection.close()
```


Close a connection gracefully.

This will clean up any materialized certificates on the local file system of
external environments such as AWS SageMaker.

Usage is recommended but optional.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/models-api/blob/master/python/hsml/connection.py#L149)</span>

### connect


```python
Connection.connect()
```


Instantiate the connection.

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


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/models-api/blob/master/python/hsml/connection.py#L140)</span>

### get_model_registry


```python
Connection.get_model_registry()
```


Get a reference to a model registry to perform operations on.

__Returns__

`ModelRegistry`. A model registry handle object to perform operations on.


----


