# Phase 2 Threat Model

| Threat | Principal controls | Remaining requirement |
|---|---|---|
| Malicious video upload | suffix/size validation, isolated processing recommendation | MIME sniffing, sandbox/transcode service |
| Model tampering | SHA-256 validation and smoke activation | artifact signatures and trusted registry |
| Dataset poisoning | checksum and lineage requirements | signed manifests and reviewer approval |
| Cross-tenant access | tenant-scoped queries and tests | universal authorization middleware |
| Unauthorized promotion | release-gate engine and audit requirement | role enforcement on every mutation |
| Forged/replayed reject event | correlation and idempotency keys | device certificates, broker ACLs, nonce policy |
| MQTT secret exposure | environment-based configuration | secret manager and rotation |
| Edge impersonation | device identity field | mutual TLS and enrollment workflow |
| Evidence modification | checksums | immutable/WORM storage and signed manifests |
| Audit tampering | append-only design guidance | external immutable audit sink |
| Denial of service | upload limits | rate limits, queue quotas, resource isolation |
