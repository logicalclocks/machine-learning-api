# Hopsworks Model Registry

<p align="center">
  <a href="https://community.hopsworks.ai"><img
    src="https://img.shields.io/discourse/users?label=Hopsworks%20Community&server=https%3A%2F%2Fcommunity.hopsworks.ai"
    alt="Hopsworks Community"
  /></a>
    <a href="https://docs.hopsworks.ai"><img
    src="https://img.shields.io/badge/docs-HSML-orange"
    alt="Hopsworks Model Registry Documentation"
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

HSML is the library to interact with the Hopsworks Model Registry. The library makes it easy to export and manage models.

The library automatically configures itself based on the environment it is run.
However, to connect from an external Python environment additional connection information, such as host and port, is required. For more information about the setup from external environments, see the setup section.

## Getting Started On Hopsworks

Instantiate a connection and get the project model registry handle
```python
import hsml

# Create a connection
connection = hsml.connection()

# Get the model registry handle for the project's model registry
mr = connection.get_model_registry()
```

Create a new model
```python
mnist_model_meta = mr.tensorflow.create_model(name="mnist",
                                              version=1,
                                              metrics={"accuracy": 0.94},
                                              description="mnist model description")
mnist_model_meta.save("/tmp/model_directory")
```

Download a model
```python
mnist_model_meta = mr.get_model("name", version=1)

model_path = mnist_model_meta.download()
```

Delete a model
```python
mnist_model_meta.delete()
```

Get best performing model
```python
mnist_model_meta = mr.get_best_model('mnist', 'accuracy', 'max')

```

You can find more examples on how to use the library in [examples.hopsworks.ai](https://examples.hopsworks.ai).

## Documentation

Documentation is available at [Hopsworks Model Registry Documentation](https://docs.hopsworks.ai/).

## Issues

For general questions about the usage of Hopsworks Machine Learning please open a topic on [Hopsworks Community](https://community.hopsworks.ai/).

Please report any issue using [Github issue tracking](https://github.com/logicalclocks/machine-learning-api/issues).


## Contributing

If you would like to contribute to this library, please see the [Contribution Guidelines](CONTRIBUTING.md).
