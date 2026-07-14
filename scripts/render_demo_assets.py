from __future__ import annotations
from pathlib import Path
import json
import cv2
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'artifacts'
summary=json.loads((ART/'demo_summary.json').read_text())
out=ART/'screenshots'; out.mkdir(parents=True,exist_ok=True)

def font(size,bold=False):
    candidates=[
      Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),
      Path('/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf')]
    for p in candidates:
        if p.exists(): return ImageFont.truetype(str(p),size)
    return ImageFont.load_default()

W,H=1440,900
img=Image.new('RGB',(W,H),(9,12,13)); d=ImageDraw.Draw(img)
# grid
for x in range(0,W,36): d.line((x,0,x,H),fill=(18,23,24),width=1)
for y in range(0,H,36): d.line((0,y,W,y),fill=(18,23,24),width=1)
# header
d.rectangle((0,0,W,78),fill=(11,15,16)); d.line((0,78,W,78),fill=(43,54,57),width=1)
d.text((42,25),'FACTORYVISION',font=font(23,True),fill=(235,242,240)); d.text((247,25),'OS',font=font(23,True),fill=(149,245,195))
d.text((1080,30),'● CONTROL PLANE ONLINE',font=font(13,True),fill=(149,245,195))
d.text((42,120),'PLANT / OPERATIONS',font=font(14,True),fill=(149,245,195))
d.text((42,155),'Quality command deck',font=font(52,True),fill=(235,242,240))
# metrics
metrics=[('ACTIVE LINES','01'),('CAMERAS','01'),('FINDINGS',str(summary['objects_processed']).zfill(2)),('REJECTS',str(summary['copper_rejects']).zfill(2)),('REVIEW BACKLOG',str(sum(x['action']=='review' for x in summary['decisions'])).zfill(2)),('DRIFT ALERTS','01')]
y0=250; cardw=(W-84)//6
for i,(k,v) in enumerate(metrics):
    x=42+i*cardw; d.rectangle((x,y0,x+cardw-2,y0+145),fill=(17,23,25),outline=(41,51,54)); d.text((x+18,y0+18),k,font=font(11,True),fill=(133,147,143)); d.text((x+18,y0+68),v,font=font(41,True),fill=(234,241,239))
# batch panel
py=430; d.rectangle((42,py,W-42,H-42),fill=(15,21,23),outline=(41,51,54)); d.text((68,py+28),'CURRENT BATCH',font=font(12,True),fill=(149,245,195)); d.text((68,py+58),'FV-DEMO-001 · Metal Sorting Line 01',font=font(25,True),fill=(235,242,240))
vals=[('PURITY',f"{summary['estimated_purity_percent']:.1f}%"),('PIPELINE FPS',f"{summary['processing_fps']:.1f}"),('OBJECTS/MIN',f"{summary['objects_per_minute']:.1f}"),('CAMERA ALERT FRAMES',str(summary['camera_alert_frames']))]
for i,(k,v) in enumerate(vals):
    x=68+i*300; d.text((x,py+125),k,font=font(11,True),fill=(133,147,143)); d.text((x,py+155),v,font=font(34,True),fill=(149,245,195))
# decisions
start=py+245; d.text((68,start),'TRACK DECISIONS',font=font(12,True),fill=(133,147,143))
for i,item in enumerate(summary['decisions'][:5]):
    yy=start+38+i*45; action=item['action'].upper(); col=(149,245,195) if action=='PASS' else ((255,108,99) if action=='REJECT' else (255,180,93))
    d.text((68,yy),f"#{item['track_id']:02d}",font=font(15,True),fill=(235,242,240)); d.text((135,yy),f"observed {item['observed_frames']} frames",font=font(14),fill=(155,168,164)); d.text((370,yy),f"confidence {item['mean_confidence']:.3f}",font=font(14),fill=(155,168,164)); d.text((610,yy),action,font=font(14,True),fill=col)
img.save(out/'operations-overview.png')

# GIF from actual overlay video
cap=cv2.VideoCapture(str(ART/'runs/demo/overlay.mp4')); frames=[]; idx=0
while True:
    ok,fr=cap.read()
    if not ok: break
    if idx%4==0:
        fr=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB); pil=Image.fromarray(fr).resize((768,432)); frames.append(pil)
    idx+=1
cap.release()
if frames: frames[0].save(out/'inspection-demo.gif',save_all=True,append_images=frames[1:],duration=150,loop=0,optimize=True)
print(out/'operations-overview.png')
print(out/'inspection-demo.gif')
