from __future__ import annotations
from pathlib import Path
import json

def scan_mvtec_style(root:Path)->dict:
    items=[]
    for split in ('train','test'):
        p=root/split
        if not p.exists(): continue
        for label_dir in p.iterdir():
            if label_dir.is_dir():
                for img in label_dir.glob('*.*'): items.append({"path":str(img),"split":split,"label":label_dir.name})
    return {"format":"mvtec-style","root":str(root),"items":items,"count":len(items)}

def write_manifest(data:dict,path:Path): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(data,indent=2))
