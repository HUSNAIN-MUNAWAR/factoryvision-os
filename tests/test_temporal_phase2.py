from factoryvision.cv.temporal import TemporalDecisionEngine

def test_temporal_explanation_lock_and_override():
    e=TemporalDecisionEngine(minimum_observed_frames=3,persistence_threshold=2)
    for i in range(3): e.observe(1,'copper',.9,120,i)
    d=e.decision(1); assert d['action']=='reject' and d['rule']=='persistent_positive_ratio_area_confidence' and d['locked']
    e.override(1,'pass'); assert e.decision(1)['rule']=='manual_override'
