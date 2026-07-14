from __future__ import annotations
from pathlib import Path
import json,time
import cv2
import joblib
import numpy as np
from .supervised import pixel_features


def export_pixel_classifier(model_path: Path, onnx_path: Path) -> Path:
    """Export the trained classifier using portable core ONNX operators.

    The graph is MatMul + Add + Softmax + ArgMax rather than ai.onnx.ml
    operators, so it can be consumed by ONNX Runtime and OpenVINO.
    OpenCV preprocessing remains outside the graph and produces [N, 7].
    """
    import onnx
    from onnx import TensorProto, helper, numpy_helper
    model = joblib.load(model_path)
    classes = np.asarray(model.classes_, dtype=np.int64)
    if not np.array_equal(classes, np.arange(len(classes), dtype=np.int64)):
        raise ValueError("portable demo exporter expects contiguous integer classes")
    weights = np.asarray(model.coef_, dtype=np.float32).T
    bias = np.asarray(model.intercept_, dtype=np.float32)
    graph = helper.make_graph(
        [
            helper.make_node("MatMul", ["features", "weights"], ["linear"]),
            helper.make_node("Add", ["linear", "bias"], ["logits"]),
            helper.make_node("Softmax", ["logits"], ["probabilities"], axis=1),
            helper.make_node("ArgMax", ["logits"], ["labels"], axis=1, keepdims=0),
        ],
        "factoryvision_pixel_classifier",
        [helper.make_tensor_value_info("features", TensorProto.FLOAT, [None, 7])],
        [
            helper.make_tensor_value_info("labels", TensorProto.INT64, [None]),
            helper.make_tensor_value_info("probabilities", TensorProto.FLOAT, [None, len(classes)]),
        ],
        [numpy_helper.from_array(weights, "weights"), numpy_helper.from_array(bias, "bias")],
    )
    onnx_model = helper.make_model(
        graph,
        producer_name="FactoryVision OS",
        opset_imports=[helper.make_opsetid("", 18)],
        ir_version=10,
    )
    onnx.checker.check_model(onnx_model)
    onnx_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(onnx_model, onnx_path)
    return onnx_path


def benchmark_edge_backends(onnx_path: Path, image_path: Path, out_path: Path, repeats: int = 12) -> dict:
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(image_path)
    features = pixel_features(image).astype(np.float32)
    result: dict[str, object] = {
        "input_image": str(image_path),
        "feature_shape": list(features.shape),
        "repeats": repeats,
        "preprocessing": "OpenCV BGR/HSV/grayscale -> 7 float features per pixel",
    }

    import onnxruntime as ort
    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    for _ in range(2):
        session.run(None, {input_name: features})
    timings=[]
    outputs=None
    for _ in range(repeats):
        t=time.perf_counter(); outputs=session.run(None,{input_name:features}); timings.append((time.perf_counter()-t)*1000)
    ort_labels=np.asarray(outputs[0]).reshape(-1)
    result["onnxruntime_cpu"]={
        "providers": session.get_providers(),
        "mean_latency_ms": float(np.mean(timings)),
        "p95_latency_ms": float(np.percentile(timings,95)),
        "pixels_per_second": float(len(features)/(np.mean(timings)/1000)),
    }

    try:
        from openvino import Core
        core=Core(); compiled=core.compile_model(str(onnx_path),"CPU"); inp=compiled.input(0)
        for _ in range(2): compiled({inp:features})
        ov_times=[]; ov_outputs=None
        for _ in range(repeats):
            t=time.perf_counter(); ov_outputs=compiled({inp:features}); ov_times.append((time.perf_counter()-t)*1000)
        first_key=next(iter(ov_outputs)); ov_labels=np.asarray(ov_outputs[first_key]).reshape(-1)
        result["openvino_cpu"]={
            "device":"CPU",
            "mean_latency_ms":float(np.mean(ov_times)),
            "p95_latency_ms":float(np.percentile(ov_times,95)),
            "pixels_per_second":float(len(features)/(np.mean(ov_times)/1000)),
            "label_agreement_with_onnxruntime":float(np.mean(ov_labels==ort_labels)),
        }
    except Exception as exc:
        result["openvino_cpu"]={"status":"unavailable","reason":str(exc)}

    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps(result,indent=2))
    return result
