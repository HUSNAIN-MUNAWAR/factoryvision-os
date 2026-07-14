from __future__ import annotations
from pathlib import Path
import cv2
import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, jaccard_score


def pixel_features(image: np.ndarray) -> np.ndarray:
    bgr=image.reshape(-1,3).astype(np.float32)/255.0
    hsv=cv2.cvtColor(image, cv2.COLOR_BGR2HSV).reshape(-1,3).astype(np.float32)
    hsv[:,0]/=179.0; hsv[:,1:]/=255.0
    gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).reshape(-1,1).astype(np.float32)/255.0
    return np.concatenate([bgr,hsv,gray],axis=1)

class PixelSegmentationModel:
    """Small supervised segmentation baseline that is fast enough for a CPU demo."""
    def __init__(self, model: LogisticRegression | None = None):
        self.model=model or LogisticRegression(max_iter=220, class_weight="balanced")

    def fit(self, image_paths: list[Path], mask_paths: list[Path], pixels_per_image: int=5000, seed: int=7):
        rng=np.random.default_rng(seed); xs=[]; ys=[]
        for ip,mp in zip(image_paths,mask_paths, strict=True):
            img=cv2.imread(str(ip)); mask=cv2.imread(str(mp),cv2.IMREAD_GRAYSCALE)
            feat=pixel_features(img); labels=mask.reshape(-1)
            n=min(pixels_per_image,len(labels)); idx=rng.choice(len(labels),n,replace=False)
            xs.append(feat[idx]); ys.append(labels[idx])
        self.model.fit(np.vstack(xs),np.concatenate(ys)); return self

    def predict(self,image: np.ndarray) -> tuple[np.ndarray,np.ndarray]:
        h,w=image.shape[:2]; feat=pixel_features(image)
        labels=self.model.predict(feat).reshape(h,w).astype(np.uint8)
        probs=self.model.predict_proba(feat).max(axis=1).reshape(h,w).astype(np.float32)
        return labels,probs

    def save(self,path:Path): path.parent.mkdir(parents=True,exist_ok=True); joblib.dump(self.model,path)
    @classmethod
    def load(cls,path:Path): return cls(joblib.load(path))

    def evaluate(self,image_paths:list[Path],mask_paths:list[Path]) -> dict:
        ys=[]; ps=[]
        for ip,mp in zip(image_paths,mask_paths,strict=True):
            img=cv2.imread(str(ip)); gt=cv2.imread(str(mp),cv2.IMREAD_GRAYSCALE)
            pred,_=self.predict(img); ys.append(gt.reshape(-1)); ps.append(pred.reshape(-1))
        y=np.concatenate(ys); p=np.concatenate(ps)
        return {"pixel_accuracy":float(accuracy_score(y,p)),"mean_iou":float(jaccard_score(y,p,average="macro",zero_division=0))}
