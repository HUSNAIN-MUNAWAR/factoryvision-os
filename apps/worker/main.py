from __future__ import annotations
import argparse,time
from factoryvision.db import SessionLocal,init_db
from factoryvision.models import InferenceJob
from factoryvision.jobs import execute_inference_job

def main():
    p=argparse.ArgumentParser(); p.add_argument('--once',action='store_true'); p.add_argument('--poll-seconds',type=float,default=2.0); args=p.parse_args(); init_db()
    while True:
        db=SessionLocal(); job=db.query(InferenceJob).filter(InferenceJob.status=='queued').order_by(InferenceJob.id).first(); db.close()
        if job:
            try: execute_inference_job(job.id,job.tenant_id)
            except Exception as exc: print(f'job {job.id} failed: {exc}',flush=True)
        if args.once: break
        time.sleep(args.poll_seconds)
if __name__=='__main__': main()
