from __future__ import annotations
from pathlib import Path
import cv2
import joblib
import numpy as np
from sklearn.metrics import roc_auc_score

class FeatureMemoryAnomaly:
    """One-class, feature-memory baseline inspired by PaDiM/PatchCore principles.

    It learns a per-location normal feature distribution and scores standardized
    deviations. It is intentionally small and transparent for CPU demonstration.
    """
    def __init__(self,size:tuple[int,int]=(96,96),mean=None,std=None): self.size=size; self.mean=mean; self.std=std
    def _feature(self,img:np.ndarray)->np.ndarray:
        x=cv2.resize(img,self.size).astype(np.float32)/255.0
        gray=cv2.cvtColor((x*255).astype(np.uint8),cv2.COLOR_BGR2GRAY).astype(np.float32)/255.0
        gx=cv2.Sobel(gray,cv2.CV_32F,1,0,ksize=3); gy=cv2.Sobel(gray,cv2.CV_32F,0,1,ksize=3)
        return np.dstack([x,gray,np.sqrt(gx*gx+gy*gy)])
    def fit(self,paths:list[Path]):
        stack=np.stack([self._feature(cv2.imread(str(p))) for p in paths]); self.mean=stack.mean(0); self.std=stack.std(0)+0.025; return self
    def predict(self,img:np.ndarray)->tuple[float,np.ndarray]:
        feat=self._feature(img); z=np.abs((feat-self.mean)/self.std).mean(2); z=cv2.GaussianBlur(z,(9,9),0)
        heat=cv2.resize(z,(img.shape[1],img.shape[0])); return float(np.percentile(z,99)),heat.astype(np.float32)
    def save(self,p:Path): p.parent.mkdir(parents=True,exist_ok=True); joblib.dump({"size":self.size,"mean":self.mean,"std":self.std},p)
    @classmethod
    def load(cls,p:Path): d=joblib.load(p); return cls(d['size'],d['mean'],d['std'])
    def evaluate(self,normal:list[Path],anomaly:list[Path])->dict:
        labels=[]; scores=[]
        for p in normal: labels.append(0); scores.append(self.predict(cv2.imread(str(p)))[0])
        for p in anomaly: labels.append(1); scores.append(self.predict(cv2.imread(str(p)))[0])
        return {"image_auroc":float(roc_auc_score(labels,scores)),"normal_score_mean":float(np.mean(scores[:len(normal)])),"anomaly_score_mean":float(np.mean(scores[len(normal):]))}
