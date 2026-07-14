from __future__ import annotations
from pathlib import Path
from hashlib import sha256
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

def batch_report(path:Path,summary:dict,evidence:list[Path],metadata:dict)->str:
    path.parent.mkdir(parents=True,exist_ok=True); c=canvas.Canvas(str(path),pagesize=A4); w,h=A4
    c.setTitle('FactoryVision OS Batch Quality Report'); c.setFont('Helvetica-Bold',18); c.drawString(42,h-48,'FactoryVision OS — Batch Quality Report')
    c.setFont('Helvetica',10); y=h-78
    rows=[('Organization',metadata.get('organization','FactoryVision Demo Manufacturing')),('Site',metadata.get('site','Rawalpindi Demo Plant')),('Line',metadata.get('line','Metal Sorting Line 01')),('Batch',metadata.get('batch','FV-DEMO-001')),('Model version',metadata.get('model','pixel-segmentation/1.0')),('Frames',summary.get('frames')),('Objects processed',summary.get('objects_processed')),('Rejects',summary.get('copper_rejects')),('Estimated purity',f"{summary.get('estimated_purity_percent',0):.2f}%"),('Processing FPS',f"{summary.get('processing_fps',0):.2f}"),('Camera alert frames',summary.get('camera_alert_frames'))]
    for k,v in rows: c.setFont('Helvetica-Bold',9); c.drawString(42,y,str(k)); c.setFont('Helvetica',9); c.drawString(170,y,str(v)); y-=17
    c.setFont('Helvetica-Bold',12); c.drawString(42,y-8,'Product decisions'); y-=30
    for d in summary.get('decisions',[]):
        c.setFont('Helvetica',8); c.drawString(48,y,f"Track {d['track_id']}: {d['action'].upper()} | observations={d['observed_frames']} | copper ratio={d['copper_ratio']:.2f} | confidence={d['mean_confidence']:.2f}"); y-=14
        if y<180: c.showPage(); y=h-50
    if evidence:
        c.showPage(); c.setFont('Helvetica-Bold',14); c.drawString(42,h-45,'Evidence frames'); x,y=42,h-85
        for p in evidence[:6]:
            try: c.drawImage(ImageReader(str(p)),x,y-135,width=240,height=135,preserveAspectRatio=True); c.setFont('Helvetica',8); c.drawString(x,y-147,p.name)
            except Exception: pass
            x+=260
            if x>400: x=42; y-=180
    c.setFont('Helvetica',7); c.drawString(42,25,'Generated from stored inference results. PLC/MQTT events are explicitly simulated in the demo.'); c.save()
    return sha256(path.read_bytes()).hexdigest()

def _metric_report(path:Path,title:str,metadata:dict,sections:list[tuple[str,list[tuple[str,object]]]],evidence:list[Path]|None=None)->str:
    path.parent.mkdir(parents=True,exist_ok=True); c=canvas.Canvas(str(path),pagesize=A4); w,h=A4
    c.setTitle(title); c.setFont('Helvetica-Bold',18); c.drawString(42,h-48,title); y=h-82
    c.setFont('Helvetica',9)
    for k,v in metadata.items():
        c.setFont('Helvetica-Bold',9); c.drawString(42,y,str(k)); c.setFont('Helvetica',9); c.drawString(170,y,str(v)); y-=16
    for heading,rows in sections:
        y-=10
        if y<120: c.showPage(); y=h-50
        c.setFont('Helvetica-Bold',12); c.drawString(42,y,heading); y-=22
        for k,v in rows:
            if y<70: c.showPage(); y=h-50
            c.setFont('Helvetica-Bold',9); c.drawString(52,y,str(k)); c.setFont('Helvetica',9); c.drawString(220,y,str(v)); y-=15
    if evidence:
        c.showPage(); c.setFont('Helvetica-Bold',14); c.drawString(42,h-45,'Evidence'); x,y=42,h-85
        for p in evidence[:6]:
            try: c.drawImage(ImageReader(str(p)),x,y-135,width=240,height=135,preserveAspectRatio=True); c.setFont('Helvetica',8); c.drawString(x,y-147,p.name)
            except Exception: pass
            x+=260
            if x>400: x=42; y-=180
    c.setFont('Helvetica',7); c.drawString(42,25,'Generated from FactoryVision OS stored results and artifacts.'); c.save()
    return sha256(path.read_bytes()).hexdigest()

def shift_report(path:Path,summary:dict,metadata:dict)->str:
    return _metric_report(path,'FactoryVision OS - Shift Quality Report',metadata,[('Production',[
        ('Frames processed',summary.get('frames')),('Objects processed',summary.get('objects_processed')),('Objects per minute',f"{summary.get('objects_per_minute',0):.2f}"),('Rejects',summary.get('copper_rejects')),('Estimated purity',f"{summary.get('estimated_purity_percent',0):.2f}%")]),('Operations',[('Review items',sum(d.get('action')=='review' for d in summary.get('decisions',[]))),('Camera alert frames',summary.get('camera_alert_frames')),('Pipeline FPS',f"{summary.get('processing_fps',0):.2f}")])])

def model_performance_report(path:Path,summary:dict,metadata:dict)->str:
    seg=summary.get('segmentation_metrics',{}); anomaly=summary.get('anomaly_metrics',{}); edge=summary.get('edge_benchmark',{})
    rows=[('Pixel accuracy',seg.get('pixel_accuracy')),('Mean IoU',seg.get('mean_iou'))]
    for name,metrics in anomaly.items():
        if isinstance(metrics,dict) and 'image_auroc' in metrics: rows.extend([(f'{name} image AUROC',metrics.get('image_auroc')),(f'{name} normal score mean',metrics.get('normal_score_mean')),(f'{name} anomaly score mean',metrics.get('anomaly_score_mean'))])
    edge_rows=[]
    for name,metrics in edge.items():
        if isinstance(metrics,dict) and 'mean_latency_ms' in metrics: edge_rows.extend([(f'{name} mean latency ms',f"{metrics['mean_latency_ms']:.3f}"),(f'{name} pixels/sec',f"{metrics['pixels_per_second']:.0f}")])
    return _metric_report(path,'FactoryVision OS - Model Performance Report',metadata,[('Evaluation metrics',rows),('Edge benchmark',edge_rows)])

def camera_health_report(path:Path,history:list[dict],metadata:dict)->str:
    alerts={}
    for h in history:
        for a in h.get('alerts',[]): alerts[a]=alerts.get(a,0)+1
    rows=[('Frames assessed',len(history)),('Mean blur score',f"{np.mean([x.get('blur_score',0) for x in history]):.2f}" if history else 'n/a'),('Mean brightness',f"{np.mean([x.get('mean_brightness',0) for x in history]):.2f}" if history else 'n/a'),('Alert frames',sum(bool(x.get('alerts')) for x in history))]
    return _metric_report(path,'FactoryVision OS - Camera Health Report',metadata,[('Camera quality',rows),('Alert counts',sorted(alerts.items()))])

def finding_evidence_report(path:Path,decisions:list[dict],evidence:list[Path],metadata:dict)->str:
    rows=[(f"Track {d.get('track_id')}",f"{d.get('action')} | observations={d.get('observed_frames')} | confidence={d.get('mean_confidence',0):.3f} | copper_ratio={d.get('copper_ratio',0):.3f}") for d in decisions]
    return _metric_report(path,'FactoryVision OS - Finding Evidence Report',metadata,[('Product decisions',rows)],evidence)
