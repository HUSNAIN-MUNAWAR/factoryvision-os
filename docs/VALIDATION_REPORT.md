# FactoryVision OS v0.2.0 Validation Report

Date: 2026-07-14

## Verified in this runtime

| Gate | Result |
|---|---|
| Phase 1 baseline Python tests | 6 passed before changes |
| Phase 2 complete Python tests | 12 passed |
| Python source compilation | Passed |
| FastAPI OpenAPI generation | Passed; 33 paths |
| Existing release artifact checks | Passed |
| Edge durable queue and duplicate prevention | Passed |
| Edge model checksum, smoke activation and rollback | Passed |
| Industrial event schema and deterministic idempotency | Passed |
| Offline publisher retry/drain behavior | Passed |
| OPC-UA simulator mapping | Passed |
| Release gates including missing evidence/waiver semantics | Passed |
| Drift PSI calculation | Passed |
| Camera freeze/quality detection | Passed |
| Plugin example | Passed |
| ONNX Runtime/OpenVINO edge artifacts | Optional; release validation accepts either measured runtimes or an explicit missing-extra boundary |
| SBOM generation | Passed |
| Source archive integrity | Verified after packaging |

## Environment-limited gates

- Docker Engine and Docker Compose are not installed; containers were not built or started.
- `npm install --no-audit --no-fund` exceeded the execution timeout. Frontend lint, TypeScript, production build, runtime and Playwright browser tests were therefore not completed here.
- No physical webcam, RTSP camera, PLC or industrial OPC-UA server was available. Video-file camera simulation and isolated OPC-UA node mapping are implemented; real hardware acceptance is not claimed.
- No large public dataset was downloaded during Phase 2. Phase 1 synthetic model artifacts remain the executable demo evidence; registry and licence metadata were hardened, but real-factory accuracy remains unproven.

## Evidence classification

- Synthetic generated data: conveyor video, segmentation demo and operational media.
- Deterministic smoke tests: Phase 1 metric summary and Phase 2 automated tests.
- Simulated industrial events: MQTT-style publisher and OPC-UA node simulator.
- Real public dataset results: none newly produced in this execution environment.
- Production certification: none.

## Compatibility

The original demo artifacts, database, model files, API routes and constructor-compatible temporal workflow remain. New modules and endpoints are additive. API and package metadata now report v0.2.0.
