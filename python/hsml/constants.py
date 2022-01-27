#
#   Copyright 2022 Logical Clocks AB
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#


class MODEL_SERVING:
    MODELS_DATASET = "Models"


class RESOURCES:
    NUM_INSTANCES = 1
    CORES = 1
    MEMORY = 1024
    GPUS = 0


class KAFKA_TOPIC_CONFIG:
    NUM_REPLICAS = 1
    NUM_PARTITIONS = 1


class INFERENCE_LOGGER:
    MODE_NONE = "NONE"
    MODE_ALL = "ALL"
    MODE_MODEL_INPUTS = "MODEL_INPUTS"
    MODE_PREDICTIONS = "PREDICTIONS"


class INFERENCE_BATCHER:
    ENABLED = False


class DEPLOYMENT:
    ACTION_START = "START"
    ACTION_STOP = "STOP"


class PREDICTOR:
    MODEL_SERVER_PYTHON = "PYTHON"
    MODEL_SERVER_TF_SERVING = "TENSORFLOW_SERVING"
    SERVING_TOOL_DEFAULT = "DEFAULT"
    SERVING_TOOL_KFSERVING = "KFSERVING"


class PREDICTOR_STATE:
    STATUS_STARTING = "STARTING"
    STATUS_RUNNING = "RUNNING"
    STATUS_STOPPING = "STOPPING"
    STATUS_STOPPED = "STOPPED"
    STATUS_UPDATING = "UPDATING"
