from __future__ import annotations
from dataclasses import dataclass,field
from statistics import mean

@dataclass
class TrackEvidence:
    track_id:int; classes:list[str]=field(default_factory=list); confidences:list[float]=field(default_factory=list); areas:list[int]=field(default_factory=list); frames:list[int]=field(default_factory=list); locked_action:str|None=None; manual_override:str|None=None

class TemporalDecisionEngine:
    def __init__(self,minimum_observed_frames=3,minimum_positive_ratio=.55,minimum_mean_confidence=.60,minimum_anomaly_area=80,maximum_confidence=.72,persistence_threshold=2,hysteresis=.05,review_min=.30,review_max=.72,decision_lock=True):
        self.min_frames=minimum_observed_frames; self.min_ratio=minimum_positive_ratio; self.min_conf=minimum_mean_confidence; self.min_area=minimum_anomaly_area; self.max_conf=maximum_confidence; self.persistence=persistence_threshold; self.hysteresis=hysteresis; self.review_min=review_min; self.review_max=review_max; self.decision_lock=decision_lock; self.evidence={}
    def observe(self,track_id:int,class_name:str,confidence:float,area:int,frame:int):
        e=self.evidence.setdefault(track_id,TrackEvidence(track_id)); e.classes.append(class_name); e.confidences.append(confidence); e.areas.append(area); e.frames.append(frame)
    def override(self,track_id:int,action:str): self.evidence[track_id].manual_override=action
    def decision(self,track_id:int)->dict:
        e=self.evidence[track_id]
        if e.manual_override: action=e.manual_override; rule='manual_override'
        elif e.locked_action and self.decision_lock: action=e.locked_action; rule='decision_locked'
        else:
            n=len(e.frames); positives=[i for i,c in enumerate(e.classes) if c=='copper']; ratio=len(positives)/max(1,n); conf=mean(e.confidences); persistent=max((sum(1 for j in positives if j>=i and j<i+self.persistence) for i in positives),default=0)>=self.persistence
            if n<self.min_frames: action='review'; rule='insufficient_observations'
            elif conf<self.min_conf: action='review'; rule='low_mean_confidence'
            elif ratio>=self.min_ratio and max(e.areas)>=self.min_area and persistent and max(e.confidences)>=self.max_conf: action='reject'; rule='persistent_positive_ratio_area_confidence'
            elif self.review_min<=ratio<=self.review_max: action='review'; rule='review_band'
            else: action='pass'; rule='negative_or_below_threshold'
            if self.decision_lock and action in {'pass','reject'}: e.locked_action=action
        n=len(e.frames); ratio=sum(c=='copper' for c in e.classes)/max(1,n); conf=mean(e.confidences)
        return {'track_id':track_id,'observed_frames':n,'copper_ratio':ratio,'mean_confidence':conf,'maximum_confidence':max(e.confidences),'max_area':max(e.areas),'action':action,'rule':rule,'first_frame':min(e.frames),'last_frame':max(e.frames),'locked':bool(e.locked_action)}
    def all_decisions(self): return [self.decision(t) for t in sorted(self.evidence)]
