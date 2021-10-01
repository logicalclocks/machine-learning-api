# Model Registry

## Retrieval

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/connection.py#L140)</span>

### get_model_registry


```python
Connection.get_model_registry()
```


Get a reference to a model registry to perform operations on.

__Returns__

`ModelRegistry`. A model registry handle object to perform operations on.


----



## Properties

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model_registry.py#L111)</span>

### project_id


Id of the project in which the model registry is located.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model_registry.py#L106)</span>

### project_name


Name of the project in which the model registry is located.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model_registry.py#L121)</span>

### python


python module for the model registry.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model_registry.py#L126)</span>

### sklearn


sklearn module for the model registry.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model_registry.py#L116)</span>

### tensorflow


tensorflow module for the model registry.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model_registry.py#L131)</span>

### torch


torch module for the model registry.


----



## Methods

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model_registry.py#L85)</span>

### get_best_model


```python
ModelRegistry.get_best_model(name, metric=None, direction=None)
```


Get the best performing model entity from the model registry.
Getting the best performing model from the Model Registry means specifying in addition to the name, also a metric
name corresponding to one of the keys in the training_metrics dict of the model and a direction. For example to
get the model version with the highest accuracy, specify metric='accuracy' and direction='max'.
__Arguments__

- __name__ `str`: Name of the model to get.
- __metric__: Name of the key in the training metrics field to compare.
- __direction__: 'max' to get the model entity with the highest value of the set metric, or 'min' for the lowest.

__Returns__

`Model`: The model metadata object.

__Raises__

- __`RestAPIError`__: If unable to retrieve model from the model registry.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model_registry.py#L47)</span>

### get_model


```python
ModelRegistry.get_model(name, version=None)
```


Get a model entity from the model registry.
Getting a model from the Model Registry means getting its metadata handle
so you can subsequently download the model directory.
__Arguments__

- __name__ `str`: Name of the model to get.
- __version__ `Optional[int]`: Version of the model to retrieve, defaults to `None` and will
    return the `version=1`.

__Returns__

`Model`: The model metadata object.

__Raises__

- __`RestAPIError`__: If unable to retrieve model from the model registry.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model_registry.py#L71)</span>

### get_models


```python
ModelRegistry.get_models(name)
```


Get all model entities from the model registry for a specified name.
Getting all models from the Model Registry for a given name returns a model entity for each version registered under
the specified model name.
__Arguments__

- __name__ `str`: Name of the model to get.

__Returns__

`List[Model]`: A list of all the model versions

__Raises__

- __`RestAPIError`__: If unable to retrieve model versions from the model registry.


----


