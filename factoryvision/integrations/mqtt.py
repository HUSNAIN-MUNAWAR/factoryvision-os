from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import json, time
from .contracts import IndustrialEvent

@dataclass
class MQTTConfig:
    broker:str='localhost'; port:int=1883; qos:int=1; retain:bool=False; tls:bool=False
    topic_template:str='factoryvision/{organization}/{site}/{line}/inspection'

@dataclass
class OfflinePublisher:
    queue_path:Path
    delivered:set[str]=field(default_factory=set)
    def __post_init__(self): self.queue_path.parent.mkdir(parents=True,exist_ok=True)
    def enqueue(self,event:IndustrialEvent):
        if event.idempotency_key in self.delivered: return False
        with self.queue_path.open('a',encoding='utf-8') as f: f.write(event.canonical_json()+'\n')
        return True
    def drain(self,send,max_retries:int=3):
        if not self.queue_path.exists(): return {'delivered':0,'failed':0}
        rows=[json.loads(x) for x in self.queue_path.read_text().splitlines() if x.strip()]
        failed=[]; delivered=0
        for row in rows:
            key=row['idempotency_key']
            if key in self.delivered: continue
            ok=False
            for attempt in range(max_retries):
                try: send(row); ok=True; break
                except Exception:
                    if attempt+1<max_retries: time.sleep(min(.01*(2**attempt),.05))
            if ok: self.delivered.add(key); delivered+=1
            else: failed.append(row)
        self.queue_path.write_text('\n'.join(json.dumps(x,sort_keys=True) for x in failed)+ ('\n' if failed else ''))
        return {'delivered':delivered,'failed':len(failed)}
