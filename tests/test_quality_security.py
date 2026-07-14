import numpy as np
from factoryvision.cv.quality import CameraHealthMonitor
from factoryvision.security import hash_password,verify_password,create_token,decode_token

def test_quality_and_password():
    q=CameraHealthMonitor().assess(np.zeros((80,80,3),dtype=np.uint8)); assert 'underexposure' in q['alerts']
    h=hash_password('secret'); assert verify_password('secret',h) and not verify_password('bad',h)
    assert decode_token(create_token('a','t','operator'))['tenant_id']=='t'
