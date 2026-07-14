# Security model

- PBKDF2-HMAC-SHA256 password hashing with per-password salt.
- Signed, expiring bearer tokens for the demo; production deployments should terminate TLS and may integrate OIDC.
- Tenant ID is applied to every operational query; tests cover cross-tenant rejection.
- Uploaded files must be allow-listed by type and size before worker handoff.
- Object storage should use private buckets and short-lived signed URLs.
- Reject adapters are simulated by default and require an explicit plant integration safety review.
- Secrets are environment variables; `.env.example` contains no credentials.
