# Research Sources

Accessed **2026-07-14**. Primary and official sources were preferred.

| Topic | Source | Organization/author | Key finding | Implementation influence |
|---|---|---|---|---|
| Steel/copper conveyor sorting | https://zenodo.org/records/20271102 | Montanuniversität Leoben / SteelDS authors | CC BY 4.0, 67.6 GB, five high-resolution subsets with MD5 checksums | Dataset registry, material workflow, instance/tracking interfaces |
| SteelDS benchmark | https://arxiv.org/abs/2605.26682 | Neubauer et al. (2026) | 24,297 labelled frames, pixel masks, 396 steel and 101 copper objects | Workflow A classes and purity/throughput metrics |
| SteelDS baseline layout | https://github.com/MelanieNeubauer/SteelDS_Baseline | SteelDS authors | Baseline code expects `images/` and `labels/` folders with YOLO text label files | Real bounding-box adapter documentation |
| Lightweight steel boxes | https://universe.roboflow.com/hamdi-ali-akgungor/steel-defects-xbfez | Roboflow Universe / Hamdi Ali Akgungor | 2,294 object-detection images, 12 classes, CC BY 4.0 | Optional small bounding-box source for detector adapter smoke tests |
| Open anomaly data | https://github.com/amazon-science/spot-diff | Amazon Science | VisA has 12 objects, 10,821 images and pixel masks under CC BY 4.0 | Default legally reusable anomaly adapter |
| Domain shift/video anomaly | https://github.com/zhangzilongc/MMR | Zhang et al. | AeBAD-S/AeBAD-V explicitly test illumination/view/background shifts | Drift monitor and sequential anomaly adapter |
| Noncommercial benchmark | https://www.mvtec.com/research-teaching/datasets/mvtec-ad | MVTec | CC BY-NC-SA 4.0 and explicit commercial prohibition | Optional research-only adapter and license guardrail |
| Portable inference | https://onnxruntime.ai/docs/execution-providers/ | Microsoft | Execution Providers map one ONNX model to CPU, CUDA, TensorRT and other accelerators | Edge abstraction and deployment documentation |
| CPU optimization | https://docs.openvino.ai/ | Intel | OpenVINO supports model compilation/caching and CPU/edge optimization | CPU/industrial-PC profile |
| Model registry | https://mlflow.org/docs/latest/ml/model-registry/ | MLflow | Registry versions, aliases and tags are current lifecycle primitives | Registry metadata; aliases preferred over deprecated fixed stages in production integrations |
| MQTT standard | https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html | OASIS | Lightweight publish/subscribe with acknowledgement/reason semantics | Reject-event simulator payload and idempotency notes |
| OPC UA | https://reference.opcfoundation.org/ | OPC Foundation | Typed industrial information model and secure client/server/pub-sub patterns | Pluggable PLC/OPC-UA boundary; simulator avoids claiming hardware actuation |
| Tracking baseline | https://arxiv.org/abs/2110.06864 | Zhang et al. | ByteTrack associates low-score detections to recover occluded tracks | Production adapter recommendation; lightweight centroid tracker used in CPU demo |
| Anomaly baseline | https://arxiv.org/abs/2106.08265 | Roth et al. | PatchCore uses a memory bank of normal patch features | Transparent feature-memory one-class demo model |
| Traceability and drift | https://www.nist.gov/programs-projects/smart-manufacturing-systems-sms-test-bed | NIST | Smart manufacturing requires interoperable measurement, control and data systems | Tenant/site/line/batch hierarchy and audit/event records |

## Decisions

1. **License-first registry:** downloads are separate from source code and commercial restrictions are machine-readable.
2. **CPU-first demo:** a small supervised pixel classifier and one-class feature memory execute locally; no canned predictions are stored.
3. **Temporal product decisions:** detections are tracked before pass/review/reject actions, avoiding repeated frame counts.
4. **Explicit simulation boundary:** MQTT/PLC events are persisted as simulated acknowledgements; no claim of physical actuation is made.
5. **Production expansion path:** official adapters support SteelDS, VisA and AeBAD; ONNX Runtime/OpenVINO are optional deployment extras rather than mandatory demo dependencies.

## Phase 2 additions — accessed 2026-07-14

| Topic | Source | Organization | URL | Key finding | Implementation influence |
|---|---|---|---|---|---|
| Edge inference | High-level Performance Hints | Intel OpenVINO | https://docs.openvino.ai/2025/openvino-workflow/running-inference/optimize-inference/high-level-performance-hints.html | Runtime profiles should be selected for latency or throughput goals. | Benchmark schema separates profiles and hardware. |
| Edge inference | Performance tuning | Microsoft ONNX Runtime | https://onnxruntime.ai/docs/performance/tune-performance/ | Latency, throughput, memory and application size are distinct tuning dimensions. | Added benchmark documentation and runtime-labelled results. |
| MQTT | MQTT Version 5.0 | OASIS Open | https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html | MQTT supports publish/subscribe delivery semantics, QoS and retained messages. | Added QoS-ready configuration, idempotency and durable queue. |
| OPC-UA security | OPC UA Part 2 Security Model | OPC Foundation | https://reference.opcfoundation.org/specs/OPC-10000-2/4 | Industrial communication needs layered application and communication security. | Simulator is isolated and explicitly not production PLC certification. |
| Machine vision interoperability | OPC UA for Machine Vision | OPC Foundation | https://reference.opcfoundation.org/ | Machine-vision result and control models can be represented through OPC-UA companion specifications. | Chose explicit inspection-result nodes in simulator. |
