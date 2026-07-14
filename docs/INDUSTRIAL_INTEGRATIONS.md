# Industrial Integrations

FactoryVision OS v0.2.0 defines `IndustrialEvent` version 1.0 with tenant/site/line/station/camera/batch/product/track identity, decision, confidence, finding, model, timestamp, evidence URI, correlation ID and deterministic idempotency key.

## MQTT

The offline publisher persists canonical JSON lines, prevents re-enqueue after acknowledged delivery, retries with bounded exponential backoff and retains failures for inspection. The configuration includes broker, port, TLS, QoS, retained-message choice and topic template. A real broker client is intentionally an optional adapter; no production broker connection is claimed in this release.

## OPC-UA simulator

The isolated simulator maps inspection events to CurrentProductId, InspectionResult, RejectCommand, ModelVersion, CameraHealth, LineState, BatchId and Timestamp. It is a contract demonstration, not a safety PLC, certified interlock or live plant connection.

## Reliability rules

Consumers must treat `event_id` as trace identity and `idempotency_key` as duplicate-prevention identity. Reject actions require downstream acknowledgement, audit recording and site-specific fail-safe engineering.
