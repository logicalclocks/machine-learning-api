# Predictor

Predictors are in charge of running a model server that loads a trained model, handles inference requests and returns predictions. They can be configured to use different model servers, serving tools, log specific inference data or scale differently. To learn about all the options available see the [Predictor Reference](predictor_api.md).

### Model servers

Hopsworks Model Serving currently supports deploying models with a Flask server for python-based models or Tensorflow Serving for tensorflow / keras models. Support for TorchServe for running PyTorch models is coming soon.

??? info "Show supported model servers"

    | Model Server       | Supported | ML Frameworks                                    |
    | ------------------ | --------- | ------------------------------------------------ |
    | Flask              | ✅        | python-based (scikit-learn, xgboost, pytorch...) |
    | Tensorflow Serving | ✅        | keras, tensorflow                                |
    | TorchServe         | ❌        | pytorch                                          |

To learn how to specify the model server used in a deployment, see [Model Server](../predictor_api/#model_server).

### Serving tools

In Hopsworks, model servers can be deployed in three different ways: directly on Docker, on raw Kubernetes deployments (a.k.a. default) or using KServe inference services.
Although the same models can be deployed in either of both serving tools, the use of KServe is highly recommended. The following is a comparitive table showing the features supported by each of them.

??? info "Show serving tools comparison"

    | Feature / requirement                          | Docker       | Kubernetes (enterprise) | KServe (enterprise)         |
    | ---------------------------------------------- | ------------ | ----------------------- | --------------------------- |
    | Autoscaling (scale-out)                        | ❌           | ✅                      | ✅                          |
    | Resource allocation                            | ➖ fixed     | ➖ min. resources       | ✅ min / max. resources     |
    | Inference logging                              | ➖ simple    | ➖ simple               | ✅ fine-grained             |
    | Inference batching                             | ➖ partially | ➖ partially            | ✅                          |
    | Scale-to-zero                                  | ❌           | ❌                      | ✅ after 30s of inactivity) |
    | Transformers                                   | ❌           | ❌                      | ✅                          |
    | Low-latency predictions                        | ❌           | ❌                      | ✅                          |
    | Multiple models                                | ❌           | ❌                      | ➖ (python-based)           |
    | Custom predictor required <br /> (python-only) | ✅           | ✅                      | ❌                          |

To learn how to specify the serving tool in a deployment, see [Serving Tool Reference](../predictor_api/#serving_tool).

### Custom predictor

Depending on the model server and serving tool used in the deployment, users can provide their own python script to load the model and make predictions.

??? info "Show supported custom predictors"

    | Serving tool | Model server       | Custom predictor script |
    | ------------ | ------------------ | ----------------------- |
    | Docker       | Flask              | ❌                      |
    |              | Tensorflow Serving | ✅                      |
    | Kubernetes   | Flask              | ❌                      |
    |              | Tensorflow Serving | ✅                      |
    | KServe       | Flask              | ✅                      |
    |              | Tensorflow Serving | ✅                      |

To configure a custom predictor, users must provide a python script implementing the following class.

=== "Python"

    ``` python
    class Predict(object):

        def __init__(self):
            """ Initialization code goes here:
                - Download the model artifact
                - Load the model
            """
            pass

        def predict(self, inputs):
            """ Serve predictions using the trained model"""
            pass
    ```

The path to this script has to be provided when calling `deploy()` or `create_predictor()` methods. Find more details in the [Predictor Reference](predictor_api.md).

See examples of custom predictor scripts in the serving [example notebooks](https://github.com/logicalclocks/hops-examples/blob/master/notebooks/ml/serving).

### Configuration

#### Resource allocation

Depending on the combination of serving tool used to deploy the a model, resource allocation can be configured at different levels. While predictors on Docker containers are fixed in resources, using Kubernetes or KServe allows a better exploitation of the resources available in the platform.

??? info "Show supported resource allocation configuration"

    | Serving tool | Component   | Resources                   |
    | ------------ | ----------- | --------------------------- |
    | Docker       | Predictor   | Fixed                       |
    |              | Transformer | ❌                          |
    | Kubernetes   | Predictor   | Minimum resources           |
    |              | Transformer | ❌                          |
    | KServe       | Predictor   | Minimum / maximum resources |
    |              | Transformer | Minimum / maximum resources |

To learn how to configure resource allocation for a deployment, see [Resources Reference](resources_api.md)

#### Inference logger

Once a model is deployed and starts making predictions as inference requests arrive, logging model inputs and predictions become essential to monitor the health of the model and take action when it degrades over time.

Hopsworks supports logging both inference requests and predictions as events into a Kafka topic for later analysis. To configure inference logging in a deployment, see [Inference Logger Reference](inference_logger_api.md).

The schema of Kafka events varies depending on the serving tool.

??? example "Show kafka topic schemas"

    === "KServe"

        ``` json
        {
            "fields": [
                { "name": "servingId", "type": "int" },
                { "name": "modelName", "type": "string" },
                { "name": "modelVersion", "type": "int" },
                { "name": "requestTimestamp", "type": "long" },
                { "name": "responseHttpCode", "type": "int" },
                { "name": "inferenceId", "type": "string" },
                { "name": "messageType", "type": "string" },
                { "name": "payload", "type": "string" }
            ],
            "name": "inferencelog",
            "type": "record"
        }
        ```

    === "Docker / Kubernetes"

        ``` json
        {
            "fields": [
                { "name": "modelId", "type": "int" },
                { "name": "modelName", "type": "string" },
                { "name": "modelVersion", "type": "int" },
                { "name": "requestTimestamp", "type": "long" },
                { "name": "responseHttpCode", "type": "int" },
                { "name": "inferenceRequest", "type": "string" },
                { "name": "inferenceResponse", "type": "string" },
                { "name": "modelServer", "type": "string" },
                { "name": "servingTool", "type": "string" }
            ],
            "name": "inferencelog",
            "type": "record"
        }
        ```

#### Inference batcher

Depending on the serving tool and the model server, inference batching can be enabled to increase inference request throughput at the cost of higher latencies. To configure inference batching in a deployment, see [Inference Batcher Reference](inference_batcher_api.md).

??? info "Show supported inference batcher configuration"

    | Serving tool | Model server       | Inference batching |
    | ------------ | ------------------ | ------------------ |
    | Docker       | Flask              | ❌                 |
    |              | Tensorflow Serving | ✅                 |
    | Kubernetes   | Flask              | ❌                 |
    |              | Tensorflow Serving | ✅                 |
    | KServe       | Flask              | ✅                 |
    |              | Tensorflow Serving | ✅                 |

## Properties

{{pred_properties}}

## Methods

{{pred_methods}}
