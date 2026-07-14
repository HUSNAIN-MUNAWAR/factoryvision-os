from __future__ import annotations
from datetime import datetime,timezone
import json

def build_reject_event(track_id:int,batch_code:str,confidence:float)->dict:
    return {"event":"material.reject","track_id":track_id,"batch":batch_code,"confidence":confidence,"actuator":"air_jet_1","timestamp":datetime.now(timezone.utc).isoformat(),"simulated":True}
def publish_simulated(protocol:str,payload:dict)->dict:
    return {"protocol":protocol,"topic":"factoryvision/reject","payload":json.dumps(payload),"acknowledged":True,"mode":"simulator"}
