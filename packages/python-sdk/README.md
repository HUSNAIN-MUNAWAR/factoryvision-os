# FactoryVision Python SDK

A compact synchronous SDK for health checks, authentication, dashboard queries,
video submission, job execution, review actions and batch-report generation.

```bash
pip install httpx
PYTHONPATH=packages/python-sdk python packages/python-sdk/examples/demo_client.py
```

The client always sends `X-Tenant-ID` and can attach a bearer token after login.
