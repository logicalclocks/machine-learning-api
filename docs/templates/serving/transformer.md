# Transformer

Transformers are used to apply transformations on the model inputs before sending them to the model for making predictions. They run on a built-in Flask server provided by Hopsworks and require the implementation of a python script with the following class and methods:

=== "Python"

    ```python
    class Transformer(object):
        def __init__(self):
            # Initialization code goes here
            pass

        def preprocess(self, inputs):
            # Transform the request inputs here. The object returned by this method will be used as model input.
            return inputs

        def postprocess(self, outputs):
            # Transform the predictions computed by the model before returning a response.
            return outputs
    ```

Once the transformer script is implemented, you can

As an example, consider a model trained to detect unusual activity of users within a platform. Instead of sending all recent activity records of a specific user each time we want to predict if the use is abnormal, we can simply send the _user_id_ and build/enrich the model input in the transformer before sending it to the predictor, by retrieving the most recent activity from an external source such as a [Feature Store](https://docs.hopsworks.ai/feature-store-api/latest/).

## Properties

{{trans_properties}}

## Methods

{{trans_methods}}
