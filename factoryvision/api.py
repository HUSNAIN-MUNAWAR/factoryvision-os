from __future__ import annotations
from pathlib import Path
from contextlib import asynccontextmanager
import json
from fastapi import FastAPI,Depends,Header,HTTPException,UploadFile,File,Form,BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .db import SessionLocal,init_db
from .models import Site,ProductionLine,Camera,InferenceJob,Finding,ReviewDecision,RejectEvent,DriftAlert,VisionModel,ModelVersion,Batch,Report,AuditEvent,User,InspectionWorkflow,DatasetVersion,TrainingExperiment,Deployment
from .security import verify_password,create_token
from .events import build_reject_event,publish_simulated
from .config import settings
from .jobs import execute_inference_job
from .reports import batch_report

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app=FastAPI(title='FactoryVision OS API',version='0.2.0',description='Industrial inspection control plane and quality operations API',lifespan=lifespan)
def get_db():
    db=SessionLocal()
    try: yield db
    finally: db.close()
def tenant(x_tenant_id:str=Header(default='demo-manufacturing')): return x_tenant_id
class Login(BaseModel): email:str; password:str
class SiteIn(BaseModel): name:str; location:str=''
class LineIn(BaseModel): site_id:int; name:str
class CameraIn(BaseModel): line_id:int; name:str; source_uri:str='demo://camera'
class ReviewIn(BaseModel): decision:str; notes:str=''; reviewer:str='reviewer@factoryvision.local'
class PromoteIn(BaseModel): stage:str='production'
class BatchIn(BaseModel): line_id:int; code:str
class UserIn(BaseModel): email:str; password:str; role:str='operator'

@app.get('/health')
def health(): return {'status':'ok','service':'factoryvision-api'}
@app.get('/ready')
def ready(db:Session=Depends(get_db)): db.execute(__import__('sqlalchemy').text('SELECT 1')); return {'status':'ready'}
@app.post('/auth/token')
def login(data:Login,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==data.email).first()
    if not user or not verify_password(data.password,user.password_hash): raise HTTPException(401,'invalid credentials')
    return {'access_token':create_token(user.email,user.tenant_id,user.role),'token_type':'bearer'}
@app.get('/sites')
def sites(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(Site).filter(Site.tenant_id==tid).all()
@app.post('/sites')
def create_site(data:SiteIn,tid:str=Depends(tenant),db:Session=Depends(get_db)): s=Site(tenant_id=tid,**data.model_dump()); db.add(s); db.commit(); db.refresh(s); return s
@app.get('/lines')
def lines(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(ProductionLine).filter(ProductionLine.tenant_id==tid).all()
@app.post('/lines')
def create_line(data:LineIn,tid:str=Depends(tenant),db:Session=Depends(get_db)):
    if not db.query(Site).filter(Site.id==data.site_id,Site.tenant_id==tid).first(): raise HTTPException(404,'site not found in tenant')
    x=ProductionLine(tenant_id=tid,**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x
@app.get('/cameras')
def cameras(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(Camera).filter(Camera.tenant_id==tid).all()
@app.post('/cameras')
def create_camera(data:CameraIn,tid:str=Depends(tenant),db:Session=Depends(get_db)):
    if not db.query(ProductionLine).filter(ProductionLine.id==data.line_id,ProductionLine.tenant_id==tid).first(): raise HTTPException(404,'line not found in tenant')
    x=Camera(tenant_id=tid,**data.model_dump()); db.add(x); db.commit(); db.refresh(x); return x
@app.get('/dashboard')
def dashboard(tid:str=Depends(tenant),db:Session=Depends(get_db)):
    findings=db.query(Finding).filter(Finding.tenant_id==tid).all(); jobs=db.query(InferenceJob).filter(InferenceJob.tenant_id==tid).all()
    return {'active_lines':db.query(ProductionLine).filter(ProductionLine.tenant_id==tid,ProductionLine.status=='active').count(),'cameras':db.query(Camera).filter(Camera.tenant_id==tid).count(),'inference_jobs':len(jobs),'findings':len(findings),'rejects':sum(f.decision=='reject' for f in findings),'review_backlog':sum(f.review_status=='pending' for f in findings),'drift_alerts':db.query(DriftAlert).filter(DriftAlert.tenant_id==tid,DriftAlert.resolved==False).count(),'latest_job':json.loads(jobs[-1].metrics_json) if jobs else None}
@app.get('/jobs')
def jobs(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(InferenceJob).filter(InferenceJob.tenant_id==tid).all()
@app.get('/findings')
def findings(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(Finding).filter(Finding.tenant_id==tid).order_by(Finding.id.desc()).all()
@app.post('/findings/{finding_id}/review')
def review(finding_id:int,data:ReviewIn,tid:str=Depends(tenant),db:Session=Depends(get_db)):
    f=db.query(Finding).filter(Finding.id==finding_id,Finding.tenant_id==tid).first()
    if not f: raise HTTPException(404,'finding not found')
    f.review_status='completed'; f.decision=data.decision; r=ReviewDecision(tenant_id=tid,finding_id=f.id,reviewer=data.reviewer,decision=data.decision,notes=data.notes); db.add(r)
    if data.decision=='reject':
        batch=db.query(Batch).join(InferenceJob,Batch.id==InferenceJob.batch_id).filter(InferenceJob.id==f.job_id).first(); payload=build_reject_event(f.track_id,batch.code if batch else 'unknown',f.confidence); sent=publish_simulated('mqtt',payload); db.add(RejectEvent(tenant_id=tid,finding_id=f.id,protocol='mqtt',payload_json=json.dumps(sent),acknowledged=True))
    db.add(AuditEvent(tenant_id=tid,actor=data.reviewer,action='finding.reviewed',entity_type='finding',entity_id=str(f.id),details_json=json.dumps(data.model_dump()))); db.commit(); return {'status':'reviewed','finding_id':f.id,'decision':f.decision}
@app.get('/models')
def models(tid:str=Depends(tenant),db:Session=Depends(get_db)):
    rows=db.query(ModelVersion,VisionModel).join(VisionModel,ModelVersion.model_id==VisionModel.id).filter(ModelVersion.tenant_id==tid).all(); return [{'id':v.id,'name':m.name,'version':v.version,'stage':v.stage,'metrics':json.loads(v.metrics_json)} for v,m in rows]
@app.post('/models/{version_id}/promote')
def promote(version_id:int,data:PromoteIn,tid:str=Depends(tenant),db:Session=Depends(get_db)):
    v=db.query(ModelVersion).filter(ModelVersion.id==version_id,ModelVersion.tenant_id==tid).first()
    if not v: raise HTTPException(404,'model version not found')
    v.stage=data.stage; db.add(AuditEvent(tenant_id=tid,actor='api-user',action='model.promoted',entity_type='model_version',entity_id=str(v.id),details_json=json.dumps({'stage':data.stage}))); db.commit(); return {'id':v.id,'stage':v.stage}
@app.get('/drift')
def drift(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(DriftAlert).filter(DriftAlert.tenant_id==tid).all()
@app.get('/reports')
def reports(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(Report).filter(Report.tenant_id==tid).all()
@app.get('/reports/{report_id}/download')
def report_download(report_id:int,tid:str=Depends(tenant),db:Session=Depends(get_db)):
    r=db.query(Report).filter(Report.id==report_id,Report.tenant_id==tid).first()
    if not r or not Path(r.uri).exists(): raise HTTPException(404,'report not found')
    return FileResponse(r.uri,media_type='application/pdf',filename=Path(r.uri).name)


@app.get('/roles')
def roles():
    return ['administrator','ml_engineer','quality_manager','line_operator','reviewer','auditor','read_only']

@app.get('/users')
def users(tid:str=Depends(tenant),db:Session=Depends(get_db)):
    return [{'id':u.id,'email':u.email,'role':u.role,'active':u.active} for u in db.query(User).filter(User.tenant_id==tid).all()]

@app.post('/users')
def create_user(data:UserIn,tid:str=Depends(tenant),db:Session=Depends(get_db)):
    from .security import hash_password
    if data.role not in roles(): raise HTTPException(422,'unsupported role')
    u=User(tenant_id=tid,email=data.email,password_hash=hash_password(data.password),role=data.role); db.add(u); db.commit(); db.refresh(u); return {'id':u.id,'email':u.email,'role':u.role}

@app.get('/batches')
def batches(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(Batch).filter(Batch.tenant_id==tid).all()

@app.post('/batches')
def create_batch(data:BatchIn,tid:str=Depends(tenant),db:Session=Depends(get_db)):
    if not db.query(ProductionLine).filter(ProductionLine.id==data.line_id,ProductionLine.tenant_id==tid).first(): raise HTTPException(404,'line not found in tenant')
    b=Batch(tenant_id=tid,line_id=data.line_id,code=data.code,status='open',purity_percent=0); db.add(b); db.commit(); db.refresh(b); return b

@app.get('/workflows')
def workflows(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(InspectionWorkflow).filter(InspectionWorkflow.tenant_id==tid).all()

@app.get('/dataset-versions')
def dataset_versions(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(DatasetVersion).filter(DatasetVersion.tenant_id==tid).all()

@app.get('/training-runs')
def training_runs(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(TrainingExperiment).filter(TrainingExperiment.tenant_id==tid).all()

@app.get('/deployments')
def deployments(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(Deployment).filter(Deployment.tenant_id==tid).all()

@app.get('/reject-events')
def reject_events(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(RejectEvent).filter(RejectEvent.tenant_id==tid).order_by(RejectEvent.id.desc()).all()

@app.get('/audit-logs')
def audit_logs(tid:str=Depends(tenant),db:Session=Depends(get_db)): return db.query(AuditEvent).filter(AuditEvent.tenant_id==tid).order_by(AuditEvent.id.desc()).limit(200).all()

@app.get('/camera-health')
def camera_health(tid:str=Depends(tenant),db:Session=Depends(get_db)):
    cameras=db.query(Camera).filter(Camera.tenant_id==tid).all(); latest=db.query(InferenceJob).filter(InferenceJob.tenant_id==tid,InferenceJob.status=='complete').order_by(InferenceJob.id.desc()).first()
    history=[]
    if latest and latest.output_uri:
        p=Path(latest.output_uri).parent/'camera_health.json'
        if p.exists(): history=json.loads(p.read_text())[-20:]
    return {'cameras':cameras,'recent_frames':history}

@app.post('/videos/upload')
async def upload_video(file:UploadFile=File(...),batch_id:int|None=Form(default=None),tid:str=Depends(tenant),db:Session=Depends(get_db)):
    suffix=Path(file.filename or '').suffix.lower()
    if suffix not in {'.mp4','.avi','.mov','.mkv'}: raise HTTPException(415,'unsupported video type')
    if batch_id is not None and not db.query(Batch).filter(Batch.id==batch_id,Batch.tenant_id==tid).first(): raise HTTPException(404,'batch not found in tenant')
    data=await file.read(settings.upload_max_mb*1024*1024+1)
    if len(data)>settings.upload_max_mb*1024*1024: raise HTTPException(413,'upload too large')
    upload_dir=settings.root/'artifacts'/'uploads'; upload_dir.mkdir(parents=True,exist_ok=True)
    safe=''.join(c for c in Path(file.filename or 'video.mp4').stem if c.isalnum() or c in '-_')[:80] or 'video'
    target=upload_dir/f'{tid}_{safe}{suffix}'; target.write_bytes(data)
    job=InferenceJob(tenant_id=tid,batch_id=batch_id,status='queued',input_uri=str(target),output_uri='',metrics_json='{}'); db.add(job); db.commit(); db.refresh(job); return job

@app.post('/jobs/{job_id}/run')
def run_job(job_id:int,background_tasks:BackgroundTasks,background:bool=True,tid:str=Depends(tenant),db:Session=Depends(get_db)):
    job=db.query(InferenceJob).filter(InferenceJob.id==job_id,InferenceJob.tenant_id==tid).first()
    if not job: raise HTTPException(404,'job not found')
    if background:
        background_tasks.add_task(execute_inference_job,job_id,tid); return {'status':'accepted','job_id':job_id}
    try: return execute_inference_job(job_id,tid)
    except Exception as exc: raise HTTPException(500,str(exc))

@app.post('/reports/batch/{batch_id}')
def create_batch_report(batch_id:int,tid:str=Depends(tenant),db:Session=Depends(get_db)):
    batch=db.query(Batch).filter(Batch.id==batch_id,Batch.tenant_id==tid).first()
    if not batch: raise HTTPException(404,'batch not found')
    job=db.query(InferenceJob).filter(InferenceJob.batch_id==batch.id,InferenceJob.tenant_id==tid,InferenceJob.status=='complete').order_by(InferenceJob.id.desc()).first()
    if not job: raise HTTPException(409,'no completed job for batch')
    summary=json.loads(job.metrics_json); evidence=sorted((Path(job.output_uri).parent/'evidence').glob('*.jpg'))
    path=settings.root/'artifacts'/'reports'/f'batch_{batch.code}.pdf'; digest=batch_report(path,summary,evidence,{'batch':batch.code})
    r=Report(tenant_id=tid,report_type='batch_quality',batch_id=batch.id,uri=str(path),sha256=digest); db.add(r); db.commit(); db.refresh(r); return r


# Phase 2 operational endpoints
from .integrations.contracts import IndustrialEvent
from .integrations.opcua_sim import OPCUASimulator
from .mlops.gates import ReleaseGateEngine
from .mlops.drift import summarize_drift

class GateEvaluationIn(BaseModel):
    metrics:dict
    requirements:dict
    evidence:dict={}
    waivers:list[str]=[]

class DriftEvaluationIn(BaseModel):
    reference:dict[str,list[float]]
    current:dict[str,list[float]]

@app.get('/industrial-events/schema')
def industrial_event_schema(): return IndustrialEvent.model_json_schema()

@app.post('/integrations/opcua/simulate')
def simulate_opcua(event:IndustrialEvent): return OPCUASimulator().apply_event(event)

@app.post('/mlops/release-gates/evaluate')
def evaluate_release_gates(data:GateEvaluationIn):
    engine=ReleaseGateEngine(); rows=engine.evaluate(data.metrics,data.requirements,data.evidence,set(data.waivers))
    return {'promotable':engine.promotable(rows),'results':[r.__dict__ for r in rows]}

@app.post('/drift/evaluate')
def evaluate_drift(data:DriftEvaluationIn): return summarize_drift(data.reference,data.current)

@app.get('/operational-readiness')
def operational_readiness(db:Session=Depends(get_db)):
    db.execute(__import__('sqlalchemy').text('SELECT 1'))
    return {'status':'ready','version':'0.2.0','database':'reachable','edge_contract':'1.0','synthetic_demo':True,'production_certified':False}
