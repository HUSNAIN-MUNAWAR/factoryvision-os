from __future__ import annotations
from abc import ABC, abstractmethod
class DatasetPlugin(ABC):
    @abstractmethod
    def verify(self)->dict: ...
    @abstractmethod
    def prepare(self)->dict: ...
class ModelPlugin(ABC):
    @abstractmethod
    def metadata(self)->dict: ...
    @abstractmethod
    def infer(self,input_data): ...
    def warmup(self): return None
class IntegrationPlugin(ABC):
    @abstractmethod
    def publish(self,event)->dict: ...
class InspectionWorkflowPlugin(ABC):
    name='unnamed'; task='unknown'; classes=()
    @abstractmethod
    def decide(self,observations)->dict: ...
