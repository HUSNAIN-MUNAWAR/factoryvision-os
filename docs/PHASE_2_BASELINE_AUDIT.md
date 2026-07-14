# Phase 2 Baseline Audit

Date: 2026-07-14

## Existing architecture and preserved capabilities

Phase 1 is a compact Python monolith with FastAPI, SQLAlchemy, OpenCV/scikit-learn/PyTorch artifacts, a Next.js source tree, Docker Compose definitions, generated reports and deterministic demo media. The segmentation, anomaly, tracking, temporal decision, report and tenant-scoped API modules are retained without deleting working artifacts.

## Baseline validation

- `pytest -q`: 6 tests passed before modification.
- Python package compilation: passed.
- The release archive contained the model, database, report and media artifacts described in v0.1.0.
- The previously reported Node smoke command referenced `tests/web_smoke.mjs`, but that file is absent from the v0.1.0 archive. This is recorded as a Phase 1 release-documentation defect.
- Docker Engine is not installed in the current runtime.
- `npm install` exceeded the execution timeout; a production frontend build therefore remains unverified here.

## Technical debt and limitations

The original tracker was centroid-only; temporal rules lacked explanations, locking and override state. Industrial events had no versioned contract, durable offline queue or OPC-UA example. Model promotion did not enforce evidence gates. Drift records existed, but no reusable drift calculation engine existed. The edge directory held configuration only, not a restart-safe agent. Plugin interfaces were absent. Dataset registry fields were minimal.

## Security observations

Tenant filters are present on principal list/detail routes, but authentication and role enforcement are not consistently attached to every mutation. Production deployments require centralized authorization middleware, Alembic-managed constraints, object-storage policies, signed device identity and external security testing.

## Backward compatibility commitments

Existing CLI commands, demo artifacts, API routes, model files, reports, database, synthetic workflow, centroid tracker and original temporal constructor arguments remain supported. Phase 2 additions are additive, except that API/package version metadata advances to v0.2.0.

## Upgrade order

1. Evidence honesty and baseline audit
2. Versioned industrial event contract
3. Offline edge queue and checksum-validated model lifecycle
4. Release gates and drift calculations
5. Camera-health and stream simulator
6. Plugin SDK
7. Expanded automated tests
8. Governance, threat model, integration and deployment documentation
9. SBOM, manifests and release packaging
