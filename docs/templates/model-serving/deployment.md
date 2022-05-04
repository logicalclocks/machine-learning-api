# Deployment

Deployments are used to unify the different components involved in making one or more trained models online and accessible for the computation of predictions on demand. In each deployment, there are three main components to consider:

!!! info ""
    1. Model artifacts
    2. Predictors
    3. Transformers

## Components

### Model artifact

A model artifact is a package containing all necessary files for the deployment of a model. It includes the model file(s) and/or custom scripts for loading the model (a.k.a. predictor script) or transforming the model inputs at inference time (a.k.a. transformer script).

When a new deployment is created, a model artifact is generated in two cases: if a) the artifact version in the predictor is set to `CREATE` (see [Artifact Version](../predictor_api/#artifact_version)) or,b) no model artifact with the same files has been created before.

!!! info
    Model artifacts are assigned a incremental version number, being `0` the version reserved for model artifacts that do not contain predictor or transformer scripts (i.e. shared artifacts containing only the model files).

### Predictor

Predictors are in charge of running the model server that loads the trained model, listens to inference requests and returns predictions. To learn more about predictors, see the [Predictor Guide](predictor.md)

!!! note
    Currently, only one predictor is supported in a deployment. Support for multiple predictors (a.k.a. inference graphs) is coming soon.

### Transformer

Transformers are used to apply transformations on the model inputs before sending them to the model for making predictions. To learn more about transformers, see the [Transformer Guide](transformer.md).

!!! info
    Transformers are only supported in KServe deployments. For more details, see the [Predictor Guide](predictor.md).

## Properties

{{dep_properties}}

## Methods

{{dep_methods}}
