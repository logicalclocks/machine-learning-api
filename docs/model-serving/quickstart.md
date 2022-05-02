# Quickstart Guide

The Hopsworks Model Serving provides operational capabilities on top of the Model Registry (see the [docs](../model-registry/quickstart.md)), for the deployment and operation of trained models.

<!--
A model is the product of training a machine learning algorithm with training data. It could be an image classifier used to detect objects in an image, such as for example detecting cancer in an MRI scan. -->

In this Quickstart Guide we are going to focus on how to configure the deployment of an existing model in the Model Registry and start making predictions with it.


### HSML library

The Hopsworks Model Serving library is part of `hsml` (**H**opswork**s** **M**achine **L**earning).
The library is Apache V2 licensed and available [here](https://github.com/logicalclocks/machine-learning-api). It currently comes with a Python SDK.
If you want to connect to the Model Serving from outside Hopsworks, see our [integration guides](../integrations/setup.md).

The library is build around metadata-objects, representing entities within Model Serving. You can modify metadata by changing it in the metadata-objects and subsequently persisting it to the Model Serving. In fact, the Model Serving itself is also represented by an object. Furthermore, these objects have methods to operate with the deployments in the Model Serving.


### Guide Notebooks

This guide is based on a [series of notebooks](https://github.com/logicalclocks/hops-examples/tree/master/notebooks/ml), which are available in the Deep Learning Demo Tour Project on Hopsworks.


### Connection, Project and Model Serving

The first step is to establish a connection with your Hopsworks Model Serving instance and retrieve the object that represents the Model Serving you'll be working with.

By default `connection.get_model_serving()` returns the Model Serving of the project you are working with.

=== "Python"

    ```python
    import hsml

    # Create a connection
    connection = hsml.connection()

    # Get the model serving handle for the project's model serving
    ms = connection.get_model_serving()
    ```


### Integration with the Model Registry

The Model Serving library integrates smoothly with the Model Registry library. Metadata objects such as [Model](../generated/registry/model.md) can be used in multiple methods in the Model Serving library to simplify the code and avoid duplication of parameters.

As a result, the easiest way to deploy an existing model is using the `model.deploy()` method available in the model metadata object. For instance, the version with highest accuracy of a trained model can be deployed with the following lines.

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

Assuming you have already created a model in the Model Registry, a deployment can now be created to prepare a model artifact for this model and make it accessible for running predictions behind a REST endpoint. A model artifact is a package containing all necessary files for the deployment of a model, including the model file and/or custom scripts for loading the model (aka. predictor script) or transforming the model inputs at inference time (aka. transformer script).

See the [example notebooks](https://github.com/logicalclocks/hops-examples/blob/master/notebooks/ml/hsml).

#### Predictors and Transformers

Predictors are in charge of running a model server that loads a trained model, handles inference requests and returns predictions. These inference requests can be transformed at inference time by configuring a transformer.

Transformers are used to apply transformations on the model inputs before sending them to the model for making predictions.

As an example, consider a model trained to detect unusual activity of users within a platform. Instead of sending all the recent activity records of a user each time we want to predict if the use is abnormal, we can simply send the _user_id_ and build/enrich the model input in the transformer before sending it to the predictor, by retrieving the most recent activity from an external source such as a [Feature Store](https://docs.hopsworks.ai/feature-store-api/latest/).


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

By default, the name of the deployment is inferred from the model name. To learn about the different parameters to configure a deployment see the [Deployment Guide](../generated/serving/deployment.md).




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

#### Start and Stop

The deployment metadata object provides methods for starting or stopping an existing deployment.

=== "Python"

    ```python
    # Start an existing deployment
    deployment.start()

    # Stop a running deployment
    deployment.stop()
    ```

#### Status

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

#### Predictions

Inference requests can be sent directly to the deployment using the `deployment.predict()` method available in the metadata object.

=== "Python"

    ```python
    data = { "instances": model.input_example }

    # Make predictions with the deployed model
    predictions = deployment.predict(data)
    ```
