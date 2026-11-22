from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "RELEASE_NOTES.md",
    "docker-compose.yml",
    "docs/DATASETS.md",
    "docs/DATASET_LINKS.md",
    "docs/RESEARCH_SOURCES.md",
    "docs/ARCHITECTURE.md",
    "docs/VALIDATION_REPORT.md",
    "docs/openapi.json",
    "packages/python-sdk/factoryvision_sdk/client.py",
    "artifacts/demo_summary.json",
    "artifacts/models/pixel_segmentation.joblib",
    "artifacts/models/feature_memory.joblib",
    "artifacts/runs/demo/overlay.mp4",
    "artifacts/runs/demo/events.json",
    "artifacts/runs/demo/evidence/track_1.jpg",
    "artifacts/reports/batch_FV-DEMO-001.pdf",
    "artifacts/reports/shift_Shift-A.pdf",
    "artifacts/reports/model_performance_demo.pdf",
    "artifacts/reports/camera_health_demo.pdf",
    "artifacts/reports/finding_evidence_demo.pdf",
    "artifacts/screenshots/operations-overview.png",
    "artifacts/screenshots/inspection-demo.gif",
    "factoryvision.db",
]

checks = {
    path: (ROOT / path).exists() and (ROOT / path).stat().st_size > 0 for path in REQUIRED
}
summary = json.loads((ROOT / "artifacts/demo_summary.json").read_text())
edge_benchmark = summary.get("edge_benchmark", {})
autoencoder = summary.get("anomaly_metrics", {}).get("autoencoder", {})
checks.update(
    {
        "actual_frames": summary.get("frames", 0) > 0,
        "actual_tracks": summary.get("objects_processed", 0) > 0,
        "actual_decisions": len(summary.get("decisions", [])) > 0,
        "actual_segmentation_metrics": bool(summary.get("segmentation_metrics")),
        "actual_two_anomaly_baselines": {
            "feature_memory",
            "autoencoder",
        }.issubset(summary.get("anomaly_metrics", {})),
        "autoencoder_boundary": (
            (ROOT / "artifacts/models/tiny_autoencoder.pt").exists()
            if autoencoder.get("status", "available") != "unavailable"
            else bool(autoencoder.get("reason") and autoencoder.get("install_extra"))
        ),
        "edge_boundary": (
            {
                "onnxruntime_cpu",
                "openvino_cpu",
            }.issubset(edge_benchmark)
            if edge_benchmark.get("status", "available") != "unavailable"
            else bool(edge_benchmark.get("reason") and edge_benchmark.get("install_extra"))
        ),
    }
)

manifest: dict[str, dict[str, str | int]] = {}
for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if any(part in {".git", "__pycache__", ".pytest_cache", "node_modules"} for part in path.parts):
        continue
    relative = str(path.relative_to(ROOT))
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    manifest[relative] = {"sha256": digest.hexdigest(), "bytes": path.stat().st_size}

payload = {"checks": checks, "files": manifest}
(ROOT / "artifacts/release_manifest.json").write_text(json.dumps(payload, indent=2))
failed = [name for name, value in checks.items() if not value]
print(json.dumps({"checks": checks, "failed": failed, "file_count": len(manifest)}, indent=2))
if failed:
    sys.exit(1)
