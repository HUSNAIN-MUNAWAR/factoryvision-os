from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass
class Detection:
    bbox: tuple[int,int,int,int]
    class_name: str
    confidence: float
    area: int
    track_id: int|None=None
    @property
    def centroid(self):
        x1,y1,x2,y2=self.bbox; return ((x1+x2)//2,(y1+y2)//2)

class CentroidTracker:
    def __init__(self,max_distance:float=90,max_missed:int=8):
        self.max_distance=max_distance; self.max_missed=max_missed; self.next_id=1; self.tracks={}; self.missed={}
    def update(self,detections:list[Detection])->list[Detection]:
        assigned=set()
        for d in detections:
            best=None; best_dist=self.max_distance
            for tid,center in self.tracks.items():
                if tid in assigned: continue
                dist=math.dist(d.centroid,center)
                if dist<best_dist: best,best_dist=tid,dist
            if best is None: best=self.next_id; self.next_id+=1
            d.track_id=best; self.tracks[best]=d.centroid; self.missed[best]=0; assigned.add(best)
        for tid in list(self.tracks):
            if tid not in assigned:
                self.missed[tid]=self.missed.get(tid,0)+1
                if self.missed[tid]>self.max_missed: self.tracks.pop(tid,None); self.missed.pop(tid,None)
        return detections
