from fastapi.testclient import TestClient
from factoryvision.db import init_db,SessionLocal
from factoryvision.models import Site,User
from factoryvision.security import hash_password
from factoryvision.api import app

def test_health_and_tenant_isolation():
    init_db(); db=SessionLocal(); db.query(Site).delete(); db.query(User).delete(); db.add(Site(tenant_id='a',name='A',location='')); db.add(Site(tenant_id='b',name='B',location='')); db.add(User(tenant_id='a',email='a@x',password_hash=hash_password('pw'),role='admin')); db.commit(); db.close()
    c=TestClient(app); assert c.get('/health').status_code==200
    assert len(c.get('/sites',headers={'X-Tenant-ID':'a'}).json())==1
    assert c.post('/auth/token',json={'email':'a@x','password':'pw'}).status_code==200
