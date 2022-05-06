# Project/Connection

In Hopsworks [a Project is a sandboxed collection](https://www.logicalclocks.com/blog/how-we-secure-your-data-with-hopsworks) of users, data, and programs (where data can be shared in a controlled manner between projects).

Each Project can have its own Model Management (Registry and Serving). However, it is possible to [share a Model Registry](#sharing-a-model-registry) and a Model Serving among projects.

When working with the Model Management (Registry and Serving) from a programming [environment](../../integrations/overview.md) you can connect to a single Hopsworks instance at a time, but it is possible to access multiple Model Registries and Model Servings simultaneously.

The connection object to a Hopsworks instance is represented by a [`Connection` object](#connection).

The [handle](#get_model_registry) can then be used to retrieve a reference to the Model Management ([Registry](../model-registry/model_registry.md) and [Serving](model_serving.md)) you want to operate on.

## Examples

=== "Python"

    !!! example "Connecting from Hopsworks"
        ```python
        import hsml
        conn = hsml.connection()
        ```

    !!! example "Connecting from Python environment"
        To connect from an external Python environment you have to provide the api key, project name, and hostname for your Hopsworks cluster. Here, we pass the api key with the insecure api_key_value parameter:

        ```python
        import hsml
        conn = hsml.connection(
            host="ec2-13-53-124-128.eu-north-1.compute.amazonaws.com",
            project="demo_ml_admin000",
            hostname_verification=False,
            api_key_value="PFcy3dZ6wLXYglRd.ydcdq5jH878IdG7xlL9lHVqrS8v3sBUqQgyR4xbpUgDnB5ZpYro6O"
            )
        ```

        A more secure approach for passing the API key is as a file:

        ```python
        import hsml
        conn = hsml.connection(
            host="ec2-13-53-124-128.eu-north-1.compute.amazonaws.com",
            project="demo_ml_admin000",
            hostname_verification=False,
            api_key_file="modelregistry.key"
            )
        ```

    !!! example "Getting the Model Management (Registry and Serving) handle"
        ```python
        mr = conn.get_model_registry()
        ms = conn.get_model_serving()
        ```

## Sharing a Model Registry

Connections are on a project-level, however, it is possible to share model registries among projects, so even if you have a connection to one project, you can retrieve a handle to any model registry shared with that project.

To share a model registry, you should follow these steps:

!!! info "Sharing a Model Registry"

    1. Open the project of the model registry that you would like to share on Hopsworks.
    2. Go to the *Data Set* browser and right click the `Models` entry.
    3. Click *Share with*, then select *Project* and choose the project you wish to share the model registry with.
    4. Select the permissions level that the project user members should have on the model registry and click *Share*.
    4. Open the project you just shared the model registry with.
    5. Go to the *Data Sets* browser and there you should see the shared model registry as `[project_name_of_shared_model_registry]::Models`. Click this entry, you will be asked to accept this shared Dataset, click *Accept*.
    7. You should now have access to this model registry from the other project.

<p align="center">
  <figure>
      <img src="../../assets/images/modelregistry-sharing.png" width="500" alt="Sharing a model registry between projects">
    <figcaption>Sharing a model registry between projects</figcaption>
  </figure>
</p>

<p align="center">
  <figure>
      <img src="../../assets/images/modelregistry-sharing-2.png" alt="Accepting a shared model registry">
    <figcaption>Accepting a shared model registry from a project</figcaption>
  </figure>
</p>

## Connection Handle

{{connection}}

## Methods

{{connection_methods}}
