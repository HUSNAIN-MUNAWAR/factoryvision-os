# Deployment profiles

| Profile | Runtime | Use |
|---|---|---|
| CPU laptop | scikit-learn/OpenCV, SQLite | self-contained demo and development |
| Industrial PC | ONNX Runtime or OpenVINO, PostgreSQL/Redis/MinIO | line-side deployment |
| NVIDIA GPU | ONNX Runtime CUDA/TensorRT | high-resolution multi-camera workloads |
| Jetson | TensorRT/DeepStream adapter | optional edge target |

`docker compose up --build` starts PostgreSQL, Redis, MinIO, MLflow, API and web. `make demo` remains independent of these services.
