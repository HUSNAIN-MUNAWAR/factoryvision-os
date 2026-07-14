from factoryvision.reports import batch_report

def test_report_generation(tmp_path):
    p=tmp_path/'r.pdf'; digest=batch_report(p,{'frames':1,'objects_processed':0,'decisions':[]},[],{'batch':'T'}); assert p.exists() and p.stat().st_size>500 and len(digest)==64
