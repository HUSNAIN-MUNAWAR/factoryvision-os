from __future__ import annotations
from datetime import datetime, timezone
from hashlib import sha256
from typing import Literal
from pydantic import BaseModel, Field
import json, uuid

Decision = Literal['pass','review','reject']
class IndustrialEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_version: str = '1.0'
    organization: str
    site: str
    line: str
    station: str
    camera: str
    batch: str
    product: str
    track: str
    decision: Decision
    confidence: float = Field(ge=0, le=1)
    finding_type: str
    model_version: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence_uri: str = ''
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    idempotency_key: str = ''
    def model_post_init(self, __context):
        if not self.idempotency_key:
            payload=f'{self.organization}|{self.site}|{self.line}|{self.batch}|{self.product}|{self.track}|{self.decision}|{self.model_version}'
            self.idempotency_key=sha256(payload.encode()).hexdigest()
    def canonical_json(self)->str:
        return json.dumps(self.model_dump(mode='json'),sort_keys=True,separators=(',',':'))
