from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
import cv2
import numpy as np

@dataclass
class ObjectState:
    object_id: int
    kind: str
    center: tuple[int, int]
    velocity: tuple[int, int]
    size: tuple[int, int]

COLORS = {"steel": (145, 150, 155), "copper": (45, 105, 190)}  # BGR
LABELS = {"background": 0, "steel": 1, "copper": 2}


def _draw_object(frame: np.ndarray, mask: np.ndarray, obj: ObjectState) -> None:
    color = COLORS[obj.kind]
    label = LABELS[obj.kind]
    cx, cy = obj.center
    sx, sy = obj.size
    if obj.object_id % 2:
        cv2.ellipse(frame, (cx, cy), (sx, sy), obj.object_id * 13 % 180, 0, 360, color, -1)
        cv2.ellipse(mask, (cx, cy), (sx, sy), obj.object_id * 13 % 180, 0, 360, label, -1)
    else:
        pts = np.array([[cx-sx, cy-sy//2], [cx+sx, cy-sy], [cx+sx//2, cy+sy], [cx-sx, cy+sy//2]])
        cv2.fillPoly(frame, [pts], color)
        cv2.fillPoly(mask, [pts], label)
    # Add realistic highlights and texture while preserving the class signal.
    cv2.line(frame, (cx-sx//2, cy), (cx+sx//2, cy), tuple(min(255, c+35) for c in color), 2)


def generate_dataset(out_dir: Path, frames: int = 54, width: int = 640, height: int = 360, seed: int = 7) -> dict:
    rng = np.random.default_rng(seed)
    images = out_dir / "images"
    masks = out_dir / "masks"
    images.mkdir(parents=True, exist_ok=True)
    masks.mkdir(parents=True, exist_ok=True)
    objects = [
        ObjectState(1, "steel", (-80, 105), (9, 0), (38, 20)),
        ObjectState(2, "copper", (-190, 180), (11, 0), (26, 16)),
        ObjectState(3, "steel", (-320, 270), (8, 0), (48, 24)),
        ObjectState(4, "copper", (-450, 80), (10, 0), (20, 28)),
        ObjectState(5, "steel", (-570, 215), (12, 0), (34, 22)),
    ]
    annotations=[]
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_path = out_dir / "conveyor.mp4"
    writer = cv2.VideoWriter(str(video_path), fourcc, 12.0, (width, height))
    for i in range(frames):
        base = np.full((height, width, 3), (35, 38, 40), dtype=np.uint8)
        # conveyor texture
        noise = rng.normal(0, 7, base.shape).astype(np.int16)
        frame = np.clip(base.astype(np.int16)+noise, 0, 255).astype(np.uint8)
        for y in range(0, height, 45):
            cv2.line(frame, (0, y), (width, y), (48, 50, 52), 1)
        mask = np.zeros((height, width), dtype=np.uint8)
        frame_objects=[]
        for obj in objects:
            x = obj.center[0] + obj.velocity[0] * i
            y = obj.center[1] + int(5*np.sin((i+obj.object_id)/6))
            if -70 < x < width+70:
                current = ObjectState(obj.object_id, obj.kind, (x,y), obj.velocity, obj.size)
                _draw_object(frame, mask, current)
                frame_objects.append({"id":obj.object_id,"class":obj.kind,"center":[x,y]})
        # Lighting drift and one deliberately blurred frame exercise camera-health checks.
        if i > frames*0.72:
            frame = cv2.convertScaleAbs(frame, alpha=1.0, beta=15)
        if i == frames//2:
            frame = cv2.GaussianBlur(frame, (17,17), 0)
        cv2.imwrite(str(images/f"frame_{i:04d}.png"), frame)
        cv2.imwrite(str(masks/f"frame_{i:04d}.png"), mask)
        writer.write(frame)
        annotations.append({"frame": i, "objects": frame_objects})
    writer.release()
    manifest={"source":"FactoryVision synthetic conveyor generator","license":"CC0-1.0","frames":frames,"fps":12,"video":str(video_path),"annotations":annotations}
    (out_dir/"manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def generate_anomaly_dataset(out_dir: Path, count: int = 24, seed: int = 13) -> dict:
    rng=np.random.default_rng(seed)
    normal=out_dir/'normal'; anomaly=out_dir/'anomaly'; masks=out_dir/'masks'
    for p in (normal, anomaly, masks): p.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        img=np.full((192,192,3), 155, np.uint8)
        img=np.clip(img.astype(np.int16)+rng.normal(0,5,img.shape),0,255).astype(np.uint8)
        cv2.rectangle(img,(30,42),(162,150),(125,130,135),-1)
        cv2.line(img,(40,65+i%8),(150,65+i%8),(165,170,175),2)
        cv2.imwrite(str(normal/f"normal_{i:03d}.png"),img)
    for i in range(8):
        img=cv2.imread(str(normal/f"normal_{i:03d}.png")); m=np.zeros((192,192),np.uint8)
        if i%2:
            cv2.line(img,(65,85),(140,115),(25,25,25),5); cv2.line(m,(65,85),(140,115),255,7)
        else:
            cv2.circle(img,(110,95),12,(35,55,180),-1); cv2.circle(m,(110,95),14,255,-1)
        cv2.imwrite(str(anomaly/f"anomaly_{i:03d}.png"),img); cv2.imwrite(str(masks/f"anomaly_{i:03d}.png"),m)
    return {"normal":count,"anomaly":8,"license":"CC0-1.0"}
