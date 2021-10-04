# Model

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L27)</span>

### Model


```python
hsml.model.Model(
    id,
    name,
    version=None,
    created=None,
    environment=None,
    description=None,
    experiment_id=None,
    project_name=None,
    experiment_project_name=None,
    metrics=None,
    program=None,
    user_full_name=None,
    signature=None,
    training_dataset=None,
    input_example=None,
    framework=None,
    model_registry_id=None,
    href=None,
    expand=None,
    items=None,
    count=None,
    type=None,
)
```


Metadata object representing a model in the Model Registry.


----



## Creation

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/tensorflow/signature.py#L24)</span>

### create_model


```python
hsml.tensorflow.signature.create_model(
    name,
    version=None,
    metrics=None,
    description=None,
    input_example=None,
    signature=None,
    training_dataset=None,
)
```


Create a model metadata object.

!!! note "Lazy"
    This method is lazy and does not persist any metadata or uploads model artifacts in the
    model registry on its own. To save the model object and the model artifacts, call the `save()` method with a
    local file path to the directory containing the model artifacts.

__Arguments__

- __name__ `str`: Name of the model to create.
- __version__ `Optional[int]`: Optionally version of the model to create, defaults to `None` and
    will create the model with incremented version from the last
    version in the model registry.
- __description__ `Optional[str]`: Optionally a string describing the model, defaults to empty string
    `""`.
- __input_example__ `Optional[Union[pandas.core.frame.DataFrame, numpy.ndarray]]`: Optionally an input example that represents inputs for the model, defaults to `None`.
- __signature__ `Optional[hsml.utils.signature.Signature]`: Optionally a signature for the model for inputs and/or predictions.
- __training_dataset__ `Optional[hsfs.training_dataset.TrainingDataset]`: Optionally a training dataset used to train the model.

__Returns__

`Model`. The model metadata object.


----



## Retrieval

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



## Properties

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L187)</span>

### created


Creation date of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L178)</span>

### description


Description of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L196)</span>

### environment


Input example of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L207)</span>

### experiment_id


Experiment Id of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L302)</span>

### experiment_project_name


experiment_project_name of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L254)</span>

### framework


framework of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L151)</span>

### id


Id of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L243)</span>

### input_example


input_example of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L160)</span>

### name


Name of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L311)</span>

### path


path of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L225)</span>

### program


Executable used to export the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L293)</span>

### project_name


project_name of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L263)</span>

### signature


signature of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L274)</span>

### training_dataset


training_dataset of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L216)</span>

### training_metrics


Training metrics of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L234)</span>

### user


user_full_name of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L234)</span>

### user


user_full_name of the model.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L169)</span>

### version


Version of the model.


----



## Methods

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L320)</span>

### add_tag


```python
Model.add_tag(name, value)
```


Attach a tag to a feature group.
A tag consists of a <name,value> pair. Tag names are unique identifiers across the whole cluster.
The value of a tag can be any valid json - primitives, arrays or json objects.
__Arguments__

- __name__ `str`: Name of the tag to be added.
- __value__: Value of the tag to be added.

__Raises__

`RestAPIError` in case the backend fails to add the tag.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L102)</span>

### delete


```python
Model.delete()
```


Delete the model

!!! danger "Potentially dangerous operation"
    This operation drops all metadata associated with **this version** of the
    model **and** in addition to the model artifacts.

__Raises__

`RestAPIError`.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L333)</span>

### delete_tag


```python
Model.delete_tag(name)
```


Delete a tag attached to a feature group.
__Arguments__

- __name__ `str`: Name of the tag to be removed.

__Raises__

`RestAPIError` in case the backend fails to delete the tag.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L98)</span>

### download


```python
Model.download()
```


Download the model files to a local folder.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L114)</span>

### from_response_json


```python
Model.from_response_json(json_dict)
```


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L342)</span>

### get_tag


```python
Model.get_tag(name)
```


Get the tags of a feature group.
__Arguments__

- __name__ `str`: Name of the tag to get.

__Returns__

tag value

__Raises__

`RestAPIError` in case the backend fails to retrieve the tag.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L353)</span>

### get_tags


```python
Model.get_tags()
```


Retrieves all tags attached to a feature group.
__Returns__

`Dict[str, obj]` of tags.

__Raises__

`RestAPIError` in case the backend fails to retrieve the tags.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L130)</span>

### json


```python
Model.json()
```


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L92)</span>

### save


```python
Model.save(model_path, await_registration=480)
```


Persist the model metadata object to the model registry.


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L133)</span>

### to_dict


```python
Model.to_dict()
```


----

<span style="float:right;">[[source]](https://github.com/logicalclocks/machine-learning-api/blob/master/python/hsml/model.py#L124)</span>

### update_from_response_json


```python
Model.update_from_response_json(json_dict)
```


----


