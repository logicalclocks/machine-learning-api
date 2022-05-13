# Deployment

Deployments are used to unify the different components involved in making one or more trained models online and accessible for the computation of predictions on demand. In each deployment, there are three main components to consider:

!!! info ""
    1. Model artifacts
    2. Predictors
    3. Transformers

See how to start creating deployments in the [Model Serving Quickstart](../../../model-serving/quickstart/#create).

## Components

### Model artifact

A model artifact is a package containing all of the necessary files for the deployment of a model. It includes the model file(s) and/or custom scripts for loading the model (predictor script) or transforming the model inputs at inference time (the transformer script).

When a new deployment is created, a model artifact is generated in two cases:

- the artifact version in the predictor is set to `CREATE` (see [Artifact Version](../predictor_api/#artifact_version))
- no model artifact with the same files has been created before.

!!! info
    Model artifacts are assigned an incremental version number, being `0` the version reserved for model artifacts that do not contain predictor or transformer scripts (i.e., shared artifacts containing only the model files).

### Predictor

Predictors are responsible for running the model server that loads the trained model, listens to inference requests and returns prediction results. To learn more about predictors, see the [Predictor Guide](predictor.md)

!!! note
    Currently, only one predictor is supported in a deployment. Support for multiple predictors (the inference graphs) is coming soon.

### Transformer

Transformers are used to apply transformations on the model inputs before sending them to the predictor for making predictions using the model. To learn more about transformers, see the [Transformer Guide](transformer.md).

!!! info
    Transformers are only supported in KServe deployments. For more details, see the [Predictor Guide](predictor.md).

## Properties

{{dep_properties}}

## Methods

{{dep_methods}}
