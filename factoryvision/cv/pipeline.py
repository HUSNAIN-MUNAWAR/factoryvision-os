from __future__ import annotations
from pathlib import Path
import json,time
import cv2
import numpy as np
from .supervised import PixelSegmentationModel
from .tracker import CentroidTracker,Detection
from .temporal import TemporalDecisionEngine
from .quality import CameraHealthMonitor

PALETTE={1:(210,210,210),2:(35,120,255)}

def detections_from_mask(mask:np.ndarray,probs:np.ndarray,min_area:int=90)->list[Detection]:
    out=[]
    for label,name in ((1,'steel'),(2,'copper')):
        binary=(mask==label).astype(np.uint8)*255
        contours,_=cv2.findContours(binary,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            area=int(cv2.contourArea(c))
            if area<min_area: continue
            x,y,w,h=cv2.boundingRect(c); region=probs[y:y+h,x:x+w]
            out.append(Detection((x,y,x+w,y+h),name,float(region.mean()),area))
    return out

def run_video(video_path:Path,model_path:Path,out_dir:Path)->dict:
    out_dir.mkdir(parents=True,exist_ok=True)
    model=PixelSegmentationModel.load(model_path); tracker=CentroidTracker(); temporal=TemporalDecisionEngine(); health=CameraHealthMonitor()
    cap=cv2.VideoCapture(str(video_path)); fps=cap.get(cv2.CAP_PROP_FPS) or 12; width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer=cv2.VideoWriter(str(out_dir/'overlay.mp4'),cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height))
    events=[]; health_history=[]; frame_idx=0; started=time.perf_counter(); best={}
    while True:
        ok,frame=cap.read()
        if not ok: break
        mask,probs=model.predict(frame); dets=tracker.update(detections_from_mask(mask,probs))
        q=health.assess(frame,fps); q['frame']=frame_idx; health_history.append(q)
        overlay=frame.copy()
        for label,color in PALETTE.items():
            layer=np.zeros_like(frame); layer[mask==label]=color; overlay=cv2.addWeighted(overlay,1.0,layer,.22,0)
        for d in dets:
            temporal.observe(d.track_id,d.class_name,d.confidence,d.area,frame_idx)
            x1,y1,x2,y2=d.bbox; color=PALETTE[2 if d.class_name=='copper' else 1]
            cv2.rectangle(overlay,(x1,y1),(x2,y2),color,2); cv2.putText(overlay,f"#{d.track_id} {d.class_name} {d.confidence:.2f}",(x1,max(20,y1-7)),cv2.FONT_HERSHEY_SIMPLEX,.52,color,2)
            if d.track_id not in best or d.confidence>best[d.track_id][0]: best[d.track_id]=(d.confidence,overlay.copy())
            events.append({"frame":frame_idx,"track_id":d.track_id,"class":d.class_name,"confidence":d.confidence,"area":d.area,"bbox":d.bbox})
        cv2.putText(overlay,f"frame {frame_idx} | health: {','.join(q['alerts']) or 'ok'}",(15,28),cv2.FONT_HERSHEY_SIMPLEX,.62,(50,230,160),2)
        writer.write(overlay); frame_idx+=1
    cap.release(); writer.release(); elapsed=time.perf_counter()-started
    evdir=out_dir/'evidence'; evdir.mkdir(exist_ok=True)
    for tid,(_,img) in best.items(): cv2.imwrite(str(evdir/f'track_{tid}.jpg'),img)
    decisions=temporal.all_decisions(); copper=sum(d['action']=='reject' for d in decisions); processed=len(decisions)
    summary={"frames":frame_idx,"elapsed_seconds":elapsed,"processing_fps":frame_idx/max(elapsed,.001),"objects_processed":processed,"copper_rejects":copper,"estimated_purity_percent":100*(processed-copper)/max(1,processed),"objects_per_minute":processed/max(frame_idx/fps/60,.001),"decisions":decisions,"camera_alert_frames":sum(bool(h['alerts']) for h in health_history),"events":len(events)}
    (out_dir/'events.json').write_text(json.dumps(events,indent=2)); (out_dir/'camera_health.json').write_text(json.dumps(health_history,indent=2)); (out_dir/'summary.json').write_text(json.dumps(summary,indent=2))
    return summary
