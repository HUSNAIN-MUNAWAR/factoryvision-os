# Phase 2 Research Decisions

| Research finding | Implementation decision | Affected modules |
|---|---|---|
| OpenVINO exposes latency/throughput performance hints and CPU thread controls. | Benchmark documentation separates latency and throughput profiles and avoids mixing hardware results. | `docs/PERFORMANCE_BENCHMARKS.md`, edge export path |
| ONNX Runtime recommends measuring latency, throughput, memory and graph/runtime configuration separately. | Phase 2 benchmark schema records cold/warm timing and runtime identity rather than a single unlabeled FPS claim. | benchmark docs and existing artifact |
| MQTT 5 defines a lightweight publish/subscribe protocol with QoS and delivery semantics. | Added a versioned event contract, QoS-ready configuration, idempotency key and durable offline queue. | `integrations/contracts.py`, `integrations/mqtt.py` |
| OPC UA is used across industrial levels and requires layered application/communication security. | Added an isolated OPC-UA node simulator only; documentation explicitly forbids treating it as production PLC certification. | `integrations/opcua_sim.py`, integrations docs |
| Industrial decisions must be product-level rather than unstable frame-level outputs. | Added persistence, maximum confidence, review band, decision locking, rule explanation and manual override. | `cv/temporal.py` |
| Production model promotion requires objective and governance evidence. | Added passed/failed/waived/missing-evidence release-gate states. | `mlops/gates.py` |
| Edge systems must survive disconnection and restart. | Added SQLite durable queue, duplicate prevention, retry state, checksum validation, smoke activation and rollback. | `edge/agent.py` |
