# Plugin Architecture

Four stable abstract interfaces are provided under `factoryvision.plugins`: DatasetPlugin, ModelPlugin, IntegrationPlugin and InspectionWorkflowPlugin. Plugins own verification/preparation, model metadata/inference, event delivery or decision policy respectively. `example_contamination.py` demonstrates a community-style contamination-ratio workflow without modifying the core pipeline.

Plugin implementations must declare licences, validate schemas, avoid global tenant state, generate deterministic tests and never claim production accuracy from synthetic fixtures.
