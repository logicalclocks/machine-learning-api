# Model schema

A Model schema describes the input and outputs for a model. It provides a functional description of the model which makes it simpler to get started working with it. For example if the model inputs a tensor, the model schema can define the shape and data type of the tensor.

A Model schema is composed of two Schema objects, one to describe the inputs and one to describe the outputs. It is not mandatory to define both the input and output schema when creating the Model schema.

There are two different types of schemas, a column-based or tensor-based schema.

## Columnar schema

A column-based schema is composed of one or more columns, each column having a name if defined, and a data type. This maps directly to the schema you may find on for example a Spark or Pandas DataFrame.

### Build a schema

A column-based schema can be constructed manually by creating a list of `dicts` containing the mandatory `type` key which defines the data type. The optional keys `name` defines the column name, and `description` describe the field.

In the following example, the model schema for a model trained on the [Iris](https://en.wikipedia.org/wiki/Iris_flower_data_set) dataset is defined.

```python

# Import a Schema and ModelSchema definition
from hsml.utils.model_schema import ModelSchema
from hsml.utils.schema import Schema

# Model inputs for iris dataset
inputs = [{'name': 'sepal_length', 'type': 'float', 'description': 'length of sepal leaves (cm)'}, 
          {'name': 'sepal_width', 'type': 'float', 'description': 'width of sepal leaves (cm)'},
          {'name': 'petal_length', 'type': 'float', 'description': 'length of petal leaves (cm)'},
          {'name': 'petal_width', 'type': 'float', 'description': 'length of petal leaves (cm)'}]
                 
# Build the input schema
input_schema = Schema(inputs)

# Create ModelSchema object
model_schema = ModelSchema(input_schema=input_schema)

```

The created model schema can then be attached as metadata during creation of the Models object.

```python

import hsml
conn = hsml.connection()
mr = conn.get_model_registry()

mnist_model = mr.python.create_model("iris", model_schema=model_schema)

```

### Infer a schema

A schema can also be inferred given a data object, such as for example a Pandas or Spark DataFrame. For a list of supported objects consult [this](../api/model_schema_api).

```python
import pandas

# Import a Schema and ModelSchema definition
from hsml.utils.model_schema import ModelSchema
from hsml.utils.schema import Schema

# Model inputs defined in Pandas DataFrame
data = [[5.1, 3.5, 1.4, 0.2], 
        [4.9, 3.0, 1.4, 0.2]]
pandas_df = pandas.DataFrame(data, columns = ['sepal_length', 'sepal_width', 'petal_length', 'petal_width'])

# Infer the inputs schema                 
input_schema = Schema(pandas_df)

# Create ModelSchema object
ModelSchema(input_schema=input_schema)

```

## Tensor schema

A tensor-based schema consists of one or more tensors, each tensor having a data type and a shape. This maps directly to the schema you may find on a `numpy.ndarray`.

### Build a schema

An inputs or outputs schema can be constructed manually by creating a list of `dicts` containing the mandatory key `type` defining the data type and `shape` defining the shape of the tensor. The optional key `name` defines the tensor name and `description` describe the field.

In the following example, the model schema for a model trained on the [MNIST](https://en.wikipedia.org/wiki/MNIST_database) dataset is defined.

```python

# Import a Schema and ModelSchema definition
from hsml.utils.model_schema import ModelSchema
from hsml.utils.schema import Schema

# Model inputs for MNIST dataset
inputs = [{'type': 'uint8', 'shape': [28, 28, 1], 'description': 'grayscale representation of 28x28 MNIST images'}]
               
# Build the input schema                 
input_schema = Schema(inputs)

# Model outputs
outputs = [{'type': 'float32', 'shape': [10]}]

# Build the output schema                 
output_schema = Schema(outputs)

# Create ModelSchema object
model_schema = ModelSchema(input_schema=input_schema, output_schema=output_schema)

```

The created model schema can then be attached as metadata during creation of the Models object.

```python

import hsml
conn = hsml.connection()
mr = conn.get_model_registry()

mnist_model = mr.tensorflow.create_model("mnist", model_schema=model_schema)

```


### Infer a schema

A Tensor schema can also be inferred given a data object, currently we support `numpy.ndarray`. For a list of supported objects consult [this](../api/model_schema_api).

```python

import numpy

# Import a Schema and ModelSchema definition
from hsml.utils.model_schema import ModelSchema
from hsml.utils.schema import Schema

# Model inputs defined in numpy.ndarray
ndarr = numpy.random.rand(28,28,1).astype("uint8")

# Infer the inputs schema                 
input_schema = Schema(ndarr)

# Create ModelSchema object
ModelSchema(input_schema=input_schema)

```
