from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
@dataclass
class OPCUANodes:
    current_product_id:str=''; inspection_result:str='review'; reject_command:bool=False
    model_version:str=''; camera_health:str='unknown'; line_state:str='idle'; batch_id:str=''; timestamp:str=''
class OPCUASimulator:
    def __init__(self): self.nodes=OPCUANodes()
    def apply_event(self,event):
        self.nodes=OPCUANodes(current_product_id=event.product,inspection_result=event.decision,reject_command=event.decision=='reject',model_version=event.model_version,camera_health='healthy',line_state='running',batch_id=event.batch,timestamp=datetime.now(timezone.utc).isoformat())
        return asdict(self.nodes)
