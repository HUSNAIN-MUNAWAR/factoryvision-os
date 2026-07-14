from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx


class FactoryVisionError(RuntimeError):
    """Raised when the FactoryVision API returns an unsuccessful response."""


@dataclass(slots=True)
class FactoryVisionClient:
    """Synchronous client for common FactoryVision OS operations."""

    base_url: str = "http://localhost:8000"
    tenant_id: str = "demo-manufacturing"
    token: str | None = None
    timeout_seconds: float = 30.0

    def _headers(self) -> dict[str, str]:
        headers = {"X-Tenant-ID": self.tenant_id}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        headers = dict(self._headers())
        headers.update(kwargs.pop("headers", {}))
        with httpx.Client(base_url=self.base_url, timeout=self.timeout_seconds) as client:
            response = client.request(method, path, headers=headers, **kwargs)
        if response.is_error:
            raise FactoryVisionError(
                f"{response.status_code} {response.request.method} {response.request.url}: "
                f"{response.text[:500]}"
            )
        content_type = response.headers.get("content-type", "")
        return response.json() if "application/json" in content_type else response.content

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/health")

    def login(self, email: str, password: str) -> str:
        payload = self._request("POST", "/auth/token", json={"email": email, "password": password})
        self.token = payload["access_token"]
        return self.token

    def dashboard(self) -> dict[str, Any]:
        return self._request("GET", "/dashboard")

    def findings(self) -> list[dict[str, Any]]:
        return self._request("GET", "/findings")

    def review_finding(
        self, finding_id: int, decision: str, reviewer: str, notes: str = ""
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/findings/{finding_id}/review",
            json={"decision": decision, "reviewer": reviewer, "notes": notes},
        )

    def upload_video(self, video: str | Path) -> dict[str, Any]:
        path = Path(video)
        with path.open("rb") as handle:
            return self._request(
                "POST",
                "/videos/upload",
                files={"file": (path.name, handle, "video/mp4")},
            )

    def run_job(self, job_id: int) -> dict[str, Any]:
        return self._request("POST", f"/jobs/{job_id}/run")

    def generate_batch_report(self, batch_id: int) -> dict[str, Any]:
        return self._request("POST", f"/reports/batch/{batch_id}")
