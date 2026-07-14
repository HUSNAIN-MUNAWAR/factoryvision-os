from __future__ import annotations
import base64,hashlib,hmac,json,time
from .config import settings

def hash_password(password:str)->str:
    salt=hashlib.sha256(str(time.time_ns()).encode()).digest()[:16]
    digest=hashlib.pbkdf2_hmac('sha256',password.encode(),salt,240_000)
    return base64.urlsafe_b64encode(salt+digest).decode()
def verify_password(password:str,encoded:str)->bool:
    raw=base64.urlsafe_b64decode(encoded); return hmac.compare_digest(raw[16:],hashlib.pbkdf2_hmac('sha256',password.encode(),raw[:16],240_000))
def create_token(subject:str,tenant_id:str,role:str,ttl:int=3600)->str:
    payload={"sub":subject,"tenant_id":tenant_id,"role":role,"exp":int(time.time())+ttl}; body=base64.urlsafe_b64encode(json.dumps(payload,separators=(',',':')).encode()).rstrip(b'=')
    sig=hmac.new(settings.secret_key.encode(),body,hashlib.sha256).digest(); return (body+b'.'+base64.urlsafe_b64encode(sig).rstrip(b'=')).decode()
def decode_token(token:str)->dict:
    body,sig=token.encode().split(b'.'); expected=hmac.new(settings.secret_key.encode(),body,hashlib.sha256).digest()
    if not hmac.compare_digest(expected,base64.urlsafe_b64decode(sig+b'='*((4-len(sig)%4)%4))): raise ValueError('invalid signature')
    data=json.loads(base64.urlsafe_b64decode(body+b'='*((4-len(body)%4)%4)))
    if data['exp']<time.time(): raise ValueError('expired token')
    return data
