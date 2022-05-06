# Quickstart Guide

Hopsworks Model Serving enables models to be deployed on serving infrastructure and made securely accessible via a network endpoint.

In this Quickstart Guide we are going to focus on how to configure the deployment of an existing model in the Model Registry and start making predictions with it via its network endpoint.


### HSML library

The Hopsworks Model Serving API is part of `hsml` (**H**opswork**s** **M**achine **L**earning).
The HSML library is Apache V2 licensed and available [here](https://github.com/logicalclocks/machine-learning-api). It currently comes with a Python SDK.
If you want to use a deployed model endpoint from outside Hopsworks, see our [integration guides](../integrations/overview.md).

The library is build around metadata-objects, representing entities within Model Serving. You can modify metadata by changing it in the metadata-objects and subsequently persisting them to Hopsworks. In fact, the Model Serving itself is also represented by an object. Furthermore, these objects have methods to deploy and undeploy models as well as perform actions on deployed models.


### Guide Notebooks

This guide is based on a [series of notebooks](https://github.com/logicalclocks/hops-examples/tree/master/notebooks/ml).


### Connection, Project and Model Serving

The first step is to establish a connection with your Hopsworks instance and retrieve the object that represents the Model Serving you'll be working with.

By default `connection.get_model_serving()` returns the Model Serving handle for the project you are working with.

=== "Python"

    ```python
    import hsml

    # Create a connection
    connection = hsml.connection()

    # Get the model serving handle for the project's model serving
    ms = connection.get_model_serving()
    ```


### Integration with the Model Registry

The Model Serving API integrates smoothly with the Model Registry API. Metadata objects such as [Model](../generated/model-registry/model.md) can be used in multiple methods in the Model Serving library to simplify the code and avoid duplication of parameters.

As a result, the easiest way to deploy an existing model is to call `model.deploy()`. For instance, the version with highest accuracy of a trained model can be deployed with the following lines.

=== "Python"

    ```python
    # Get the model registry handle for the project's model registry
    mr = connection.get_model_registry()

    # Get the version with highest accuracy
    model = mr.get_best_model('mnist', 'accuracy', 'max')

    # Create a deployment
    deployment = model.deploy()
    ```

To learn more about managing models with the Model Registry see the [Model Registry documentation](../model-registry/quickstart.md).


### Deployment

Assuming you have already created a model in the Model Registry, a deployment can now be created to prepare a model artifact for this model and make it accessible for running predictions behind a REST endpoint. A model artifact is a package containing all of the necessary files for the deployment of a model, including the model file and/or custom scripts for loading the model (the predictor script) or transforming the model inputs at inference time (the transformer script).

See the [example notebooks](https://github.com/logicalclocks/hops-examples/blob/master/notebooks/ml).

#### Predictors and Transformers

Predictors are responsible for running a model server that loads a trained model, handles inference requests and returns predictions (see the [Predictor Guide](../generated/model-serving/predictor.md)). These inference requests can be transformed at inference time by configuring a transformer.

Transformers are used to apply transformations on the model inputs before sending them to the predictor for making predictions using the model (see the [Transformer Guide](../generated/model-serving/transformer.md)).

As an example, consider a model trained to detect unusual activity of users within a platform. Instead of sending all the recent activity records of a user each time we want to predict if the use is abnormal, we can simply send the _user_id_ and build/enrich the model input in the transformer before sending it to the predictor. We enrich the model input by retrieving the most recent user activity from the [Feature Store](https://docs.hopsworks.ai/feature-store-api/latest/) using the user_id as an entity key.

#### Creation

Apart from the `model.deploy()` shortcut available in the model metadata object, deployments can be created in two additional ways: deploying a predictor or creating a deployment from scratch.

To deploy a predictor, the Model Serving handle provides the `ms.create_predictor()` method to define the predictor metadata object which can be deployed using the `predictor.deploy()` method.

=== "Python"

    ```python
    # Define a predictor for a trained model
    predictor = ms.create_predictor(model)

    # Deploy the predictor
    deployment = predictor.deploy()
    ```

Alternatively, deployments can be created and saved using the `ms.create_deployment()` and `deployment.save()` methods, respectively.

=== "Python"

    ```python
    # Define a predictor for a trained model
    predictor = ms.create_predictor(model)

    # Define a deployment
    deployment = ms.create_deployment(predictor)

    # Save the deployment in the Model Serving
    deployment.save()
    ```

By default, the name of the deployment is inferred from the model name. To learn about the different parameters to configure a deployment see the [Deployment Guide](../generated/model-serving/deployment.md).


#### Retrieval

If there were deployments previously created in your Model Serving, you can retrieve them by using the Model Serving handle. Moreover, you can retrieve a specific deployment by name or id.

=== "Python"

    ```python
    # Get all deployments
    deployments = ms.get_deployments()

    # Get deployment by name
    deployment = ms.get_deployment("mnist")

    # Get deployment by id
    deployment = ms.get_deployment_by_id(1)
    ```

#### Start and stop deployment

The deployment metadata object provides methods for starting or stopping an existing deployment.

=== "Python"

    ```python
    # Start an existing deployment
    deployment.start()

    # Stop a running deployment
    deployment.stop()
    ```

#### Get deployment status

To get the current state of a deployment, the deployment metadata object contains the method `deployment.get_state()` which provides information such as the status (e.g. running, stopped...) or inference endpoints to make prediction requests to.

=== "Python"

    ```python
    # Get the current state of a deployment
    current_state = deployment.get_state()

    # Check the deployment status
    print("%s is %s" % (deployment.name, current_state.status))

    # Print a full description of the deployment state
    current_state.describe()
    ```

#### Make predictions using a deployment

Inference requests can be sent directly to the deployment using the `deployment.predict()` method available in the metadata object.

=== "Python"

    ```python
    data = { "instances": model.input_example }

    # Make predictions with the deployed model
    predictions = deployment.predict(data)
    ```
