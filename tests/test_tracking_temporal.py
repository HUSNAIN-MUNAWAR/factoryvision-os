from factoryvision.cv.tracker import CentroidTracker,Detection
from factoryvision.cv.temporal import TemporalDecisionEngine

def test_stable_tracking_and_reject():
    t=CentroidTracker(max_distance=30)
    a=t.update([Detection((0,0,20,20),'copper',.9,200)])[0]
    b=t.update([Detection((4,0,24,20),'copper',.8,210)])[0]
    assert a.track_id==b.track_id
    e=TemporalDecisionEngine(minimum_observed_frames=2)
    e.observe(a.track_id,'copper',.9,200,0); e.observe(a.track_id,'copper',.8,210,1)
    assert e.decision(a.track_id)['action']=='reject'
