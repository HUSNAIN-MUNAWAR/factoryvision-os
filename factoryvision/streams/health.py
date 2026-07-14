from __future__ import annotations
from dataclasses import dataclass
import cv2, numpy as np
@dataclass
class CameraHealthRules:
    blur_warning_below:float=80; blur_critical_below:float=45; fps_warning_below:float=12; fps_critical_below:float=5; frozen_critical_after:int=10
class CameraHealthMonitor:
    def __init__(self,rules=CameraHealthRules()): self.rules=rules; self.previous=None; self.frozen=0
    def inspect(self,frame:np.ndarray,fps:float)->dict:
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY); blur=float(cv2.Laplacian(gray,cv2.CV_64F).var()); exposure=float(gray.mean()); contrast=float(gray.std())
        repeated=False
        if self.previous is not None: repeated=float(np.mean(cv2.absdiff(gray,self.previous)))<1.0
        self.frozen=self.frozen+1 if repeated else 0; self.previous=gray.copy()
        severity='critical' if blur<self.rules.blur_critical_below or fps<self.rules.fps_critical_below or self.frozen>=self.rules.frozen_critical_after else 'warning' if blur<self.rules.blur_warning_below or fps<self.rules.fps_warning_below or exposure<40 or exposure>215 else 'healthy'
        return {'blur_score':blur,'exposure':exposure,'contrast':contrast,'fps':fps,'repeated_frame':repeated,'frozen_count':self.frozen,'severity':severity}
