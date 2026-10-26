"""Reject missing/false evidence; temporary copies only, no ODE integration."""
from pathlib import Path
import json,shutil,subprocess,sys,tempfile
from check_packet import ROOT,require,load,env

def call(script):return subprocess.run([sys.executable,'-B',str(script)],capture_output=True,text=True,env=env(),timeout=120)
def run():
    require(__debug__,'optimized Python is refused')
    rejected=[]
    with tempfile.TemporaryDirectory(prefix='mp-cover-negative-') as td:
        p=Path(td);h=p/'hset';c=p/'capd';h.mkdir()
        H=ROOT/'evidence/hset-check';C=ROOT/'evidence/independent-capd'
        for f in ('check_coverage.py','strips.json'):shutil.copyfile(H/f,h/f)
        rows=[json.loads(s) for s in (H/'coverage.jsonl').read_text().splitlines()]
        idx=next(i for i,r in enumerate(rows) if r.get('kind')=='coverage_cell')
        original=json.loads(json.dumps(rows[idx]))
        for name,alter in [('missing_leaf',None),('false_return',False),('lost_transversality',0)]:
            bad=json.loads(json.dumps(rows))
            if alter is None:bad.pop(idx)
            elif name=='false_return':bad[idx]['return_proved']=False
            else:bad[idx]['vz_lower_event']=0
            (h/'coverage.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in bad))
            require(call(h/'check_coverage.py').returncode!=0,'accepted corrupt binary64 '+name);rejected.append(name)
        expected=load(C/'ab-extension/expected-coverage-check.json')
        shutil.copytree(C,c)
        # Delete all cells from one edge: the historical checker returns an
        # unresolved report, so explicitly require rejection of the final claim.
        for item in expected['inputs']:
            f=c/item['file'];d=load(f);key='cells' if 'cells' in d else 'records'
            d[key]=[r for r in d[key] if r['task'][0]!=2];f.write_text(json.dumps(d))
        r=call(c/'ab-extension/check_coverage.py')
        require(r.returncode==0 and not load(c/'ab-extension/coverage-check.json')['all_five_covering_conditions'],'accepted missing CAPD edge')
        rejected.append('missing_CAPD_edge')
        f=c/expected['inputs'][0]['file'];d=load(f);d['source_sha256']='0'*64;f.write_text(json.dumps(d))
        require(call(c/'ab-extension/check_coverage.py').returncode!=0,'accepted wrong source hash');rejected.append('wrong_source_hash')
    return {'status':'PASS','corrupt_inputs_rejected':len(rejected),'cases':rejected,'new_ODE_integrations':0}
if __name__=='__main__':print(json.dumps(run(),indent=2))
