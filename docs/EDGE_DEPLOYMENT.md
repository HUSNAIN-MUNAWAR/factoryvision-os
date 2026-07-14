# Edge Deployment

The Phase 2 edge agent uses local SQLite persistence and supports offline event enqueue, idempotent cloud synchronization, failed-attempt accounting, model checksum validation, shadow smoke testing, active-model metadata and rollback.

A production edge package should run as an OS-managed service, store evidence on an encrypted volume, use a device certificate, pin cloud trust roots, enforce disk quotas and expose resource telemetry. The included implementation is CPU-first and restart-safe but is not a certified safety controller.
