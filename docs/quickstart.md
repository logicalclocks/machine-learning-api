# Quickstart Guide

The Hopsworks model registry is a centralized repository, within an organization, to manage machine learning models. A model is the product of training a machine learning algorithm with training data. It could be an image classifier used to detect objects in an image, such as for example detecting cancer in an MRI scan.

<p align="center">
  <figure>
    <a  href="../assets/images/quickstart.png">
      <img src="../assets/images/quickstart.png" alt="The Hopsworks Feature Store">
    </a>
    <figcaption>The Hopsworks Feature Store</figcaption>
  </figure>
</p>

In this Quickstart Guide we are going to focus on the left side of the picture above. In particular how data scientists can create models and publish them to the model registry to make them available for further development and serving.

### HSML library

The Hopsworks model registry library is called `hsml` (**H**opswork**s** **M**achine **L**earning).
The library is Apache V2 licensed and available [here](https://github.com/logicalclocks/machine-learning-api). The library is currently available for Python.
If you want to connect to the Model Registry from outside Hopsworks, see our [integration guides](setup.md).

The library is build around metadata-objects, representing entities within the Model Registry. You can modify metadata by changing it in the metadata-objects and subsequently persisting it to the Model Registry. In fact, the Model Registry itself is also represented by an object. Furthermore, these objects have methods to save model artifacts along with the entities in the model registry.

### Guide Notebooks

This guide is based on a [series of notebooks](https://github.com/logicalclocks/hops-examples/tree/master/notebooks/ml/hsml), which is available in the Deep Learning Demo Tour Project on Hopsworks.

### Connection, Project and Model Registry

The first step is to establish a connection with your Hopsworks Model Registry instance and retrieve the object that represents the Model Registry you'll be working with.

By default `connection.get_model_registry()` returns the model registry of the project you are working with. However, it accepts also a project name as parameter to select a different model registry.

=== "Python"

    ```python
    import hsml

    # Create a connection
    connection = hsml.connection()

    # Get the model registry handle for the project's model registry
    mr = connection.get_model_registry()
    ```

### Models

Assuming you have done some model training, and exported a model to a directory on a local file path, the model artifacts and additional metadata can now be saved to the Model Registry. See the [example notebooks](https://github.com/logicalclocks/hops-examples/blob/master/notebooks/ml/hsml).

#### Creation

Create a model named `mnist`. As you can see, you have the possibility to set parameters for the Model, such as the `version` number, or `metrics` which is set to attach model training metrics on the model. The [Model Guide](generated/model.md) guides through the full configuration of Models.

=== "Python"

    ```python
    mnist_model_meta = mr.tensorflow.create_model(name="mnist",
        version=1,
        metrics={"accuracy": 0.94},
        description="mnist model description")
    ```

Up to this point we have just created the metadata object representing the model. However, we haven't saved the model in the model registry yet. To do so, we can call the method `save` on the metadata object created in the cell above.
The `save` method takes a single parameter which is the path to the directory on the local filesystem which contains all your model artifacts.

=== "Python"

    ```python
    mnist_model_meta.save("/tmp/model_directory")
    ```

#### Retrieval

If there were models previously created in your Model Registry, or you want to pick up where you left off before, you can retrieve and read models in a similar fashion as creating them:
Using the Model Registry object, you can retrieve handles to the entities, such as models, in the Model Registry. By default, this will return the first version of an entity, if you want a more recent version, you need to specify the version.

=== "Python"

    ```python
    mnist_model_meta = mr.get_model('mnist', version=1)

    # Download the model
    model_download_path = mnist_model_meta.download()

    # Load the model
    tf.saved_model.load(model_download_path)
    ```

To seamlessly combine HSML with model serving components the library makes it simple to also query for the best performing model. In this instance, we get the best model version by querying for the model version with the highest `accuracy` metric attached.

=== "Python"

    ```python
    mnist_model_meta = mr.get_best_model('mnist', 'accuracy', 'max')

    ```
