from __future__ import annotations
from pathlib import Path
import json
from .config import settings
from .cv.synthetic import generate_dataset,generate_anomaly_dataset
from .cv.supervised import PixelSegmentationModel
from .cv.anomaly import FeatureMemoryAnomaly
from .cv.pipeline import run_video
from .cv.export import export_pixel_classifier, benchmark_edge_backends
from .db import init_db,SessionLocal
from .models import Organization,Site,ProductionLine,Camera,Batch,VisionModel,ModelVersion,InferenceJob,Finding,RejectEvent,DriftAlert,Report,AuditEvent,User,InspectionWorkflow,DatasetVersion,TrainingExperiment,Deployment
from .security import hash_password
from .events import build_reject_event,publish_simulated
from .reports import batch_report,shift_report,model_performance_report,camera_health_report,finding_evidence_report

def run_demo(root:Path|None=None)->dict:
    root=root or settings.root; artifacts=root/'artifacts'; data=artifacts/'demo_data'; models_dir=artifacts/'models'; run_dir=artifacts/'runs'/'demo'; reports=artifacts/'reports'
    for p in (data,models_dir,run_dir,reports): p.mkdir(parents=True,exist_ok=True)
    generate_dataset(data/'conveyor'); generate_anomaly_dataset(data/'anomaly')
    images=sorted((data/'conveyor'/'images').glob('*.png')); masks=sorted((data/'conveyor'/'masks').glob('*.png'))
    split=int(len(images)*.7); seg=PixelSegmentationModel().fit(images[:split],masks[:split]); seg_path=models_dir/'pixel_segmentation.joblib'; seg.save(seg_path); seg_metrics=seg.evaluate(images[split:],masks[split:])
    normal=sorted((data/'anomaly'/'normal').glob('*.png')); abnormal=sorted((data/'anomaly'/'anomaly').glob('*.png'))
    anomaly=FeatureMemoryAnomaly().fit(normal[:18]); anomaly_path=models_dir/'feature_memory.joblib'; anomaly.save(anomaly_path); anomaly_metrics=anomaly.evaluate(normal[18:],abnormal)
    try:
        from .cv.anomaly_autoencoder import AutoencoderAnomaly
        autoencoder=AutoencoderAnomaly(); ae_history=autoencoder.fit(normal[:18],epochs=8); ae_path=models_dir/'tiny_autoencoder.pt'; autoencoder.save(ae_path,ae_history); ae_metrics=autoencoder.evaluate(normal[18:],abnormal)
    except ImportError as exc:
        ae_metrics={'status':'unavailable','reason':str(exc),'install_extra':'torch'}
    try:
        onnx_path=export_pixel_classifier(seg_path,models_dir/'pixel_segmentation.onnx')
        edge_benchmark=benchmark_edge_backends(onnx_path,images[-1],artifacts/'benchmarks'/'edge_benchmark.json')
    except ImportError as exc:
        edge_benchmark={'status':'unavailable','reason':str(exc),'install_extra':'edge'}
    summary=run_video(data/'conveyor'/'conveyor.mp4',seg_path,run_dir); summary['segmentation_metrics']=seg_metrics; summary['anomaly_metrics']={'feature_memory':anomaly_metrics,'autoencoder':ae_metrics,'comparison':{'winner_by_image_auroc':'feature_memory' if ae_metrics.get('status')=='unavailable' or anomaly_metrics['image_auroc']>=ae_metrics['image_auroc'] else 'autoencoder'}}; summary['edge_benchmark']=edge_benchmark
    init_db(); db=SessionLocal(); tenant='demo-manufacturing'
    # Recreate deterministic demo records without relying on externally provisioned services.
    for table in (RejectEvent,Finding,InferenceJob,Report,Deployment,TrainingExperiment,DatasetVersion,ModelVersion,VisionModel,Camera,Batch,ProductionLine,Site,InspectionWorkflow,DriftAlert,AuditEvent,User): db.query(table).delete()
    db.query(Organization).delete(); db.commit()
    org=Organization(name='FactoryVision Demo Manufacturing',slug=tenant); db.add(org)
    site=Site(tenant_id=tenant,name='Rawalpindi Demo Plant',location='Punjab, Pakistan'); db.add(site); db.flush()
    line=ProductionLine(tenant_id=tenant,site_id=site.id,name='Metal Sorting Line 01',status='active'); db.add(line); db.flush()
    cam=Camera(tenant_id=tenant,line_id=line.id,name='Conveyor Camera A',source_uri='demo://conveyor',status='warning' if summary['camera_alert_frames'] else 'healthy',blur_score=42.1); db.add(cam)
    batch=Batch(tenant_id=tenant,line_id=line.id,code='FV-DEMO-001',status='complete',purity_percent=summary['estimated_purity_percent']); db.add(batch); db.flush()
    workflow=InspectionWorkflow(tenant_id=tenant,name='Steel and Copper Scrap Sorting',slug='steel-scrap',config_json=json.dumps({"minimum_observed_frames":3,"minimum_positive_ratio":.55})); db.add(workflow)
    user=User(tenant_id=tenant,email='admin@factoryvision.local',password_hash=hash_password('factoryvision'),role='administrator'); db.add(user)
    ds=DatasetVersion(tenant_id=tenant,name='FactoryVision demo conveyor',version='1.0',manifest_uri=str(data/'conveyor'/'manifest.json'),license='CC0-1.0'); db.add(ds)
    vm=VisionModel(tenant_id=tenant,name='Pixel Segmentation Baseline',task='semantic-segmentation'); db.add(vm); db.flush()
    mv=ModelVersion(tenant_id=tenant,model_id=vm.id,version='1.0',stage='production',metrics_json=json.dumps(seg_metrics),artifact_uri=str(seg_path)); db.add(mv); db.flush()
    exp=TrainingExperiment(tenant_id=tenant,name='demo-pixel-segmentation',status='complete',metrics_json=json.dumps(seg_metrics)); db.add(exp)
    dep=Deployment(tenant_id=tenant,model_version_id=mv.id,target='cpu-laptop',status='ready'); db.add(dep)
    job=InferenceJob(tenant_id=tenant,batch_id=batch.id,status='complete',input_uri=str(data/'conveyor'/'conveyor.mp4'),output_uri=str(run_dir/'overlay.mp4'),metrics_json=json.dumps(summary)); db.add(job); db.flush()
    for d in summary['decisions']:
        uri=str(run_dir/'evidence'/f"track_{d['track_id']}.jpg")
        f=Finding(tenant_id=tenant,job_id=job.id,track_id=d['track_id'],class_name='copper' if d['copper_ratio']>=.5 else 'steel',confidence=d['mean_confidence'],decision=d['action'],evidence_uri=uri,review_status='pending' if d['action']=='review' else 'auto'); db.add(f); db.flush()
        if d['action']=='reject':
            payload=build_reject_event(d['track_id'],batch.code,d['mean_confidence']); sent=publish_simulated('mqtt',payload); db.add(RejectEvent(tenant_id=tenant,finding_id=f.id,protocol='mqtt',payload_json=json.dumps(sent),acknowledged=True))
    db.add(DriftAlert(tenant_id=tenant,metric='mean_brightness',baseline=46,current=61,severity='medium',resolved=False))
    db.add(AuditEvent(tenant_id=tenant,actor='demo-runner',action='demo.completed',entity_type='inference_job',entity_id=str(job.id),details_json=json.dumps({"metrics":summary})))
    db.commit()
    evidence=sorted((run_dir/'evidence').glob('*.jpg')); metadata={'organization':'FactoryVision Demo Manufacturing','site':'Rawalpindi Demo Plant','line':'Metal Sorting Line 01','batch':batch.code,'model':'pixel-segmentation/1.0','shift':'Shift A'}
    report_specs=[]
    pdf=reports/'batch_FV-DEMO-001.pdf'; report_specs.append(('batch_quality',pdf,batch_report(pdf,summary,evidence,metadata)))
    pdf=reports/'shift_Shift-A.pdf'; report_specs.append(('shift',pdf,shift_report(pdf,summary,metadata)))
    pdf=reports/'model_performance_demo.pdf'; report_specs.append(('model_performance',pdf,model_performance_report(pdf,summary,metadata)))
    health_history=json.loads((run_dir/'camera_health.json').read_text()); pdf=reports/'camera_health_demo.pdf'; report_specs.append(('camera_health',pdf,camera_health_report(pdf,health_history,metadata)))
    pdf=reports/'finding_evidence_demo.pdf'; report_specs.append(('finding_evidence',pdf,finding_evidence_report(pdf,summary['decisions'],evidence,metadata)))
    for report_type,pdf,digest in report_specs: db.add(Report(tenant_id=tenant,report_type=report_type,batch_id=batch.id,uri=str(pdf),sha256=digest))
    db.commit(); db.close()
    (artifacts/'demo_summary.json').write_text(json.dumps(summary,indent=2)); return summary
