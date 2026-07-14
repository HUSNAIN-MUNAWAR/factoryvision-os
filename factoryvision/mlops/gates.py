from __future__ import annotations
from dataclasses import dataclass
from typing import Any
@dataclass
class GateResult: name:str; status:str; actual:Any=None; required:Any=None; reason:str=''
class ReleaseGateEngine:
    def evaluate(self,metrics:dict,requirements:dict,evidence:dict|None=None,waivers:set[str]|None=None):
        evidence=evidence or {}; waivers=waivers or set(); out=[]
        for name,required in requirements.items():
            if name in waivers: out.append(GateResult(name,'waived',reason='explicit waiver')); continue
            if name.startswith('require_'):
                present=bool(evidence.get(name.removeprefix('require_')))
                out.append(GateResult(name,'passed' if present else 'missing_evidence',present,True)); continue
            if name not in metrics: out.append(GateResult(name,'missing_evidence',required=required)); continue
            actual=metrics[name]
            maximum=name.startswith('maximum_')
            passed=actual<=required if maximum else actual>=required
            out.append(GateResult(name,'passed' if passed else 'failed',actual,required))
        return out
    @staticmethod
    def promotable(results): return all(r.status in {'passed','waived'} for r in results)
