# MLOps

The demo records dataset version, model artifact, metrics, experiment, deployment target and promotion state in SQL. A production profile adds MLflow and object storage through Compose.

Release gates should cover segmentation IoU, image/pixel AUROC, calibration, latency, memory, false-reject rate, review-overturn rate and tenant-specific golden videos. Current MLflow guidance favors model aliases and tags; the `stage` field in the portable SQL model is a compatibility abstraction, not a claim that deprecated MLflow stage APIs are required.

Drift indicators: brightness, blur, class frequency, confidence, anomaly score, unknown anomaly frequency, review overturns and false rejects. Each alert records baseline/current values and severity.
