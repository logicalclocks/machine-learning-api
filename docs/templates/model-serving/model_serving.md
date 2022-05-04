# Model Serving

The Model Serving handle acts as the starting point for creating new deployments and retrieving already existing ones. To operate on specific deployments, you can get the deployment by name from the Hopsworks Model Serving using the `ms.get_deployment()` method and then use the metadata object to perform the desired actions on it.

=== "Python"

    ```python
    # Get deployment by name
    deployment = ms.get_deployment("awesome-deployment")
    ```

## Retrieval

{{ms_get}}

## Properties

{{ms_properties}}

## Methods

{{ms_methods}}
