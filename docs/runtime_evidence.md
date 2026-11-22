# Runtime evidence

The reproducible demo command is:

```bash
make demo
python scripts/validate_release.py
```

The first command generates the deterministic CC0 conveyor smoke dataset,
trains the checked-in CPU pixel-segmentation baseline and anomaly baselines,
runs the actual 54-frame video pipeline, persists decisions/reports, and
renders the tracked [`inspection-demo.gif`](../artifacts/screenshots/inspection-demo.gif).
The release validator then verifies the generated summary, model artifacts,
video/report outputs, screenshots, and SHA-256 release manifest.

The current run recorded 5 tracked objects, 5 temporal decisions, 2 copper
rejects, 1 review, 54 decoded frames, and 116 detection events. Segmentation
and both anomaly baselines ran locally. ONNX Runtime/OpenVINO were explicitly
marked unavailable because the optional `edge` extra was not installed; this is
an honest dependency boundary, not an edge benchmark claim.

The input remains generated smoke data, not a real factory dataset. Real SteelDS
and VisA sources and licensing boundaries are documented in
[`DATASETS.md`](DATASETS.md).
