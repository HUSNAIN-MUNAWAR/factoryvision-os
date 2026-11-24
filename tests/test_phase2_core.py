from hashlib import sha256
import numpy as np
from factoryvision.integrations.contracts import IndustrialEvent
from factoryvision.integrations.mqtt import OfflinePublisher
from factoryvision.integrations.opcua_sim import OPCUASimulator
from factoryvision.mlops.gates import ReleaseGateEngine
from factoryvision.mlops.drift import population_stability_index,summarize_drift
from factoryvision.edge.agent import EdgeAgent,EdgeConfig
from factoryvision.plugins.example_contamination import ContaminationRatioWorkflow
from factoryvision.streams.health import CameraHealthMonitor
from factoryvision.cv.quality import CameraHealthMonitor as PipelineCameraHealthMonitor

def event(): return IndustrialEvent(organization='o',site='s',line='l',station='st',camera='c',batch='b',product='p',track='1',decision='reject',confidence=.91,finding_type='copper',model_version='2')
def test_event_is_deterministic_and_opcua():
    a=event(); b=event(); assert a.idempotency_key==b.idempotency_key
    nodes=OPCUASimulator().apply_event(a); assert nodes['reject_command'] is True and nodes['current_product_id']=='p'
def test_offline_publisher_idempotency(tmp_path):
    p=OfflinePublisher(tmp_path/'queue.jsonl'); e=event(); assert p.enqueue(e); sent=[]; assert p.drain(lambda row: sent.append(row))['delivered']==1; assert p.enqueue(e) is False

def test_release_gates_and_drift():
    g=ReleaseGateEngine(); result=g.evaluate({'minimum_mean_iou':.75,'maximum_cpu_latency_ms':90},{'minimum_mean_iou':.7,'maximum_cpu_latency_ms':150,'require_model_card':True},{'model_card':'x'})
    assert g.promotable(result); assert population_stability_index([1,1,1,2],[8,9,9,10])>.25; assert summarize_drift({'brightness':[1,2,3]},{'brightness':[1,2,3]})[0]['severity']=='normal'
def test_edge_queue_model_install_and_rollback(tmp_path):
    agent=EdgeAgent(EdgeConfig('edge-1','tenant',tmp_path/'edge')); assert agent.enqueue('e1',{'x':1}); assert not agent.enqueue('e1',{'x':2}); assert agent.sync(lambda i,p: None)['sent']==1
    m1=tmp_path/'m1.onnx'; m1.write_bytes(b'one'); d1=sha256(b'one').hexdigest(); agent.install_model(m1,d1,'1.0',lambda p: p.exists())
    m2=tmp_path/'m2.onnx'; m2.write_bytes(b'two'); agent.install_model(m2,sha256(b'two').hexdigest(),'2.0',lambda p: True); assert agent.rollback()=='1.0'
def test_camera_health_and_plugin():
    monitor=CameraHealthMonitor(); blank=np.zeros((64,64,3),dtype=np.uint8); first=monitor.inspect(blank,25); second=monitor.inspect(blank,25); assert second['repeated_frame']; assert first['severity'] in {'warning','critical'}
    result=ContaminationRatioWorkflow().decide([{'class_name':'steel','area':90},{'class_name':'copper','area':10}]); assert result['action']=='reject'

def test_pipeline_camera_health_exposes_alerts_contract():
    monitor=PipelineCameraHealthMonitor(); result=monitor.assess(np.zeros((64,64,3),dtype=np.uint8),25)
    assert isinstance(result['alerts'], list)
