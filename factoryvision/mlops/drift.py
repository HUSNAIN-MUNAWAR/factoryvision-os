from __future__ import annotations
import math
from statistics import mean

def population_stability_index(reference:list[float],current:list[float],bins:int=10)->float:
    if not reference or not current: return 0.0
    lo=min(reference+current); hi=max(reference+current)
    if hi==lo: return 0.0
    rc=[0]*bins; cc=[0]*bins
    for seq,target in ((reference,rc),(current,cc)):
        for value in seq: target[min(bins-1,int((value-lo)/(hi-lo)*bins))]+=1
    total_r=len(reference); total_c=len(current); psi=0.0
    for r,c in zip(rc,cc):
        rp=max(r/total_r,1e-6); cp=max(c/total_c,1e-6); psi+=(cp-rp)*math.log(cp/rp)
    return psi

def summarize_drift(reference:dict[str,list[float]],current:dict[str,list[float]],warning:float=.1,critical:float=.25):
    rows=[]
    for metric,base in reference.items():
        value=population_stability_index(base,current.get(metric,[])); severity='critical' if value>=critical else 'warning' if value>=warning else 'normal'
        rows.append({'metric':metric,'psi':value,'severity':severity,'baseline_mean':mean(base) if base else 0,'current_mean':mean(current.get(metric,[])) if current.get(metric) else 0})
    return rows
