from __future__ import annotations
from pathlib import Path
import json
from .config import settings
from .db import SessionLocal
from .models import InferenceJob,ModelVersion,Finding,RejectEvent,Batch,AuditEvent
from .cv.pipeline import run_video
from .events import build_reject_event,publish_simulated


def execute_inference_job(job_id:int,tenant_id:str)->dict:
    """Idempotently execute a queued video job and persist generated findings."""
    db=SessionLocal()
    try:
        job=db.query(InferenceJob).filter(InferenceJob.id==job_id,InferenceJob.tenant_id==tenant_id).first()
        if not job: raise LookupError('job not found')
        if job.status=='complete' and job.metrics_json:
            return json.loads(job.metrics_json)
        model=db.query(ModelVersion).filter(ModelVersion.tenant_id==tenant_id,ModelVersion.stage=='production').order_by(ModelVersion.id.desc()).first()
        if not model or not Path(model.artifact_uri).exists(): raise RuntimeError('no production model artifact available')
        source=Path(job.input_uri)
        if not source.exists(): raise FileNotFoundError(source)
        job.status='running'; db.commit()
        out=settings.root/'artifacts'/'runs'/f'job_{job.id}'
        summary=run_video(source,Path(model.artifact_uri),out)
        job.status='complete'; job.output_uri=str(out/'overlay.mp4'); job.metrics_json=json.dumps(summary)
        db.query(Finding).filter(Finding.job_id==job.id,Finding.tenant_id==tenant_id).delete()
        batch=db.query(Batch).filter(Batch.id==job.batch_id,Batch.tenant_id==tenant_id).first() if job.batch_id else None
        for d in summary['decisions']:
            f=Finding(tenant_id=tenant_id,job_id=job.id,track_id=d['track_id'],class_name='copper' if d['copper_ratio']>=.5 else 'steel',confidence=d['mean_confidence'],decision=d['action'],evidence_uri=str(out/'evidence'/f"track_{d['track_id']}.jpg"),review_status='pending' if d['action']=='review' else 'auto')
            db.add(f); db.flush()
            if d['action']=='reject':
                payload=build_reject_event(d['track_id'],batch.code if batch else 'unassigned',d['mean_confidence'])
                db.add(RejectEvent(tenant_id=tenant_id,finding_id=f.id,protocol='mqtt',payload_json=json.dumps(publish_simulated('mqtt',payload)),acknowledged=True))
        db.add(AuditEvent(tenant_id=tenant_id,actor='worker',action='inference.completed',entity_type='inference_job',entity_id=str(job.id),details_json=json.dumps({'summary':summary})))
        db.commit(); return summary
    except Exception:
        job=db.query(InferenceJob).filter(InferenceJob.id==job_id,InferenceJob.tenant_id==tenant_id).first()
        if job: job.status='failed'; db.commit()
        raise
    finally:
        db.close()
