from __future__ import annotations
import cv2
import numpy as np

class CameraHealthMonitor:
    def __init__(self): self.previous=None
    def assess(self,frame:np.ndarray,fps:float|None=None)->dict:
        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        blur=float(cv2.Laplacian(gray,cv2.CV_64F).var())
        mean=float(gray.mean()); over=float((gray>245).mean()); under=float((gray<15).mean())
        freeze=0.0 if self.previous is None else float(np.mean(cv2.absdiff(gray,self.previous))<1)
        edge=float((cv2.Canny(gray,50,150)>0).mean())
        self.previous=gray
        alerts=[]
        if blur<35: alerts.append('blur')
        if over>0.15: alerts.append('overexposure')
        if under>0.25: alerts.append('underexposure')
        if freeze>0.995: alerts.append('frame_freeze')
        if fps is not None and fps<5: alerts.append('low_frame_rate')
        return {"blur_score":blur,"mean_brightness":mean,"overexposed_ratio":over,"underexposed_ratio":under,"freeze_ratio":freeze,"edge_density":edge,"dirty_lens_risk":bool(blur<45 and edge<0.025),"alerts":alerts}
