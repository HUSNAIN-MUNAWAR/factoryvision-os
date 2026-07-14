# Performance Benchmarks

The retained Phase 1 edge benchmark is in `artifacts/benchmarks/edge_benchmark.json`. It is a local smoke benchmark, not a cross-hardware leaderboard. Phase 2 defines measurements for runtime, hardware, input shape, model size, cold start, warm latency, FPS, preprocessing, inference, post-processing, tracking and end-to-end decision latency. Results from different machines must not be combined without explicit hardware labels.

OpenVINO's official benchmark methodology distinguishes actual inference time from preprocessing/post-processing. ONNX Runtime likewise treats latency, throughput, memory and application size as separate dimensions.
