from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from hashlib import sha256
import json, os, shutil, sqlite3, time
@dataclass
class EdgeConfig: device_id:str; tenant_id:str; storage:Path
class EdgeAgent:
    def __init__(self,config:EdgeConfig):
        self.config=config; config.storage.mkdir(parents=True,exist_ok=True); self.db=config.storage/'edge.db'; self.models=config.storage/'models'; self.models.mkdir(exist_ok=True)
        with sqlite3.connect(self.db) as c: c.execute('CREATE TABLE IF NOT EXISTS queue(id TEXT PRIMARY KEY,payload TEXT,status TEXT DEFAULT "pending",attempts INTEGER DEFAULT 0)')
    def enqueue(self,event_id:str,payload:dict)->bool:
        try:
            with sqlite3.connect(self.db) as c: c.execute('INSERT INTO queue(id,payload) VALUES(?,?)',(event_id,json.dumps(payload,sort_keys=True)))
            return True
        except sqlite3.IntegrityError: return False
    def sync(self,sender)->dict:
        sent=failed=0
        with sqlite3.connect(self.db) as c:
            rows=c.execute('SELECT id,payload,attempts FROM queue WHERE status="pending" ORDER BY rowid').fetchall()
            for event_id,payload,attempts in rows:
                try: sender(event_id,json.loads(payload)); c.execute('UPDATE queue SET status="sent" WHERE id=?',(event_id,)); sent+=1
                except Exception: c.execute('UPDATE queue SET attempts=? WHERE id=?',(attempts+1,event_id)); failed+=1
        return {'sent':sent,'failed':failed}
    def install_model(self,source:Path,expected_sha256:str,version:str,smoke_test):
        digest=sha256(source.read_bytes()).hexdigest()
        if digest!=expected_sha256: raise ValueError('model checksum mismatch')
        target=self.models/f'{version}{source.suffix}'; shutil.copy2(source,target)
        if not smoke_test(target): target.unlink(missing_ok=True); raise ValueError('model smoke test failed')
        active=self.models/'active.json'; previous=None
        if active.exists(): previous=json.loads(active.read_text()).get('version')
        active.write_text(json.dumps({'version':version,'path':str(target),'previous':previous,'sha256':digest},indent=2)); return target
    def rollback(self):
        active=self.models/'active.json'; data=json.loads(active.read_text()); previous=data.get('previous')
        if not previous: raise ValueError('no rollback target')
        candidates=list(self.models.glob(f'{previous}.*'))
        if not candidates: raise FileNotFoundError(previous)
        active.write_text(json.dumps({'version':previous,'path':str(candidates[0]),'previous':None},indent=2)); return previous
    def health(self):
        stat=os.statvfs(self.config.storage); return {'device_id':self.config.device_id,'queue_pending':self.pending_count(),'disk_free_bytes':stat.f_bavail*stat.f_frsize,'active_model':json.loads((self.models/'active.json').read_text()).get('version') if (self.models/'active.json').exists() else None,'timestamp':time.time()}
    def pending_count(self):
        with sqlite3.connect(self.db) as c: return c.execute('SELECT count(*) FROM queue WHERE status="pending"').fetchone()[0]
