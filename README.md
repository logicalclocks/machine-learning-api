# Hopsworks Model Management

<p align="center">
  <a href="https://community.hopsworks.ai"><img
    src="https://img.shields.io/discourse/users?label=Hopsworks%20Community&server=https%3A%2F%2Fcommunity.hopsworks.ai"
    alt="Hopsworks Community"
  /></a>
    <a href="https://docs.hopsworks.ai"><img
    src="https://img.shields.io/badge/docs-HSML-orange"
    alt="Hopsworks Model Management Documentation"
  /></a>
  <a href="https://pypi.org/project/hsml/"><img
    src="https://img.shields.io/pypi/v/hsml?color=blue"
    alt="PyPiStatus"
  /></a>
  <a href="https://archiva.hops.works/#artifact/com.logicalclocks/hsml"><img
    src="https://img.shields.io/badge/java-HSML-green"
    alt="Scala/Java Artifacts"
  /></a>
  <a href="https://pepy.tech/project/hsml/month"><img
    src="https://pepy.tech/badge/hsml/month"
    alt="Downloads"
  /></a>
  <a href="https://github.com/psf/black"><img
    src="https://img.shields.io/badge/code%20style-black-000000.svg"
    alt="CodeStyle"
  /></a>
  <a><img
    src="https://img.shields.io/pypi/l/hsml?color=green"
    alt="License"
  /></a>
</p>

HSML is the library to interact with the Hopsworks Model Registry and Model Serving. The library makes it easy to export, manage and deploy models.

The library automatically configures itself based on the environment it is run.
However, to connect from an external Python environment additional connection information, such as host and port, is required. For more information about the setup from external environments, see the setup section.

## Getting Started On Hopsworks

Instantiate a connection and get the project model registry and serving handles
```python
import hsml

# Create a connection
connection = hsml.connection()

# Get the model registry handle for the project's model registry
mr = connection.get_model_registry()

# Get the model serving handle for the current model registry
ms = connection.get_model_serving()
```

Create a new model
```python
model = mr.tensorflow.create_model(name="mnist",
                                   version=1,
                                   metrics={"accuracy": 0.94},
                                   description="mnist model description")
model.save("/tmp/model_directory") # or /tmp/model_file
```

Download a model
```python
model = mr.get_model("mnist", version=1)

model_path = model.download()
```

Delete a model
```python
model.delete()
```

Get best performing model
```python
best_model = mr.get_best_model('mnist', 'accuracy', 'max')

```

Deploy a model
```python
deployment = model.deploy()
```

Start a deployment
```python
deployment.start()
```

Make predictions with a deployed model
```python
data = { "instances": [ model.input_example ] }

predictions = deployment.predict(data)
```

You can find more examples on how to use the library in [examples.hopsworks.ai](https://examples.hopsworks.ai).

## Documentation

Documentation is available at [Hopsworks Model Management Documentation](https://docs.hopsworks.ai/).

## Issues

For general questions about the usage of Hopsworks Machine Learning please open a topic on [Hopsworks Community](https://community.hopsworks.ai/).
Please report any issue using [Github issue tracking](https://github.com/logicalclocks/machine-learning-api/issues).


## Contributing

If you would like to contribute to this library, please see the [Contribution Guidelines](CONTRIBUTING.md).
