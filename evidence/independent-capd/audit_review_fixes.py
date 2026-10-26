"""Offline provenance/margin audit for review items 3c--3e and 5b--5d.
Only saved records and the original exact-coverage checkers are evaluated.
No numerical solver, compiler, network request or ODE integration is invoked.
"""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import argparse,hashlib,json,re,shutil,subprocess,sys,tempfile

C=Path(__file__).resolve().parent;H=C.parent/'hset-check';P=C.parent.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
SOURCE='1cafbf1b8dad5580a5bd9d45c49247ef8d8dcaba8b97f2e23eae342e30fc411f'
CHECKER='e62eed123fc363954541ba7369a9786406ff4c832951dd7d020894ac853b15c1'
RX=re.compile(r'\b(u|s|time|vz)=\[([^,]+),([^\]]+)\]')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',required=True);a=ap.parse_args()
    expected=read(C/'ab-extension/expected-coverage-check.json')
    assert sha(C/'return_check.cpp')==expected['source_sha256']==SOURCE
    assert sha(C/'ab-extension/check_coverage.py')==CHECKER
    cache={}
    for x in expected['inputs']:
        f=C/x['file'];assert sha(f)==x['sha256'];cache[x['file']]=read(f)
        assert cache[x['file']]['source_sha256']==SOURCE
    records=expected['accepted_records'];assert len(records)==2381
    counts=Counter();byfile=Counter();minima={};seen=set()
    for position,r in enumerate(records):
        assert r['verdict']=='PASS' and r['task'][1] in ('C1','L','R')
        assert tuple(r['task']) not in seen;seen.add(tuple(r['task']))
        data=cache[r['file']];row=data.get('cells',data.get('records',[]))[r['row']]
        assert row['returncode']==0 and row['task']==r['task']
        line=next(s for s in row['stdout'].splitlines() if s.startswith('CELL '))
        assert line.startswith(r['line']) and ' M1 ' not in line
        ints={k:(F(lo),F(hi)) for k,lo,hi in RX.findall(line)}
        assert set(ints)=={'u','s','time','vz'} and all(lo<=hi for lo,hi in ints.values())
        assert ints['time'][0]>0 and ints['vz'][0]>0
        e,k,*_=r['task']
        margin=1-max(abs(x) for x in ints['s']) if k=='C1' else -1-ints['u'][1] if k=='L' else ints['u'][0]-1
        assert margin>0
        counts[e,k]+=1;byfile[r['file']]+=1
        key=(e,k)
        if key not in minima or margin<F(minima[key]['margin_rational_from_printed_endpoints']):
            minima[key]={'edge':e,'condition':k,'task':r['task'],'accepted_record_index_zero_based':position,
                         'file':r['file'],'row_zero_based':r['row'],'file_sha256':sha(C/r['file']),
                         'stdout_sha256':hashlib.sha256(row['stdout'].encode()).hexdigest(),
                         'CELL_line':line,'margin_rational_from_printed_endpoints':str(margin),
                         'margin_approx':float(margin),'table_display_6sig':format(float(margin),'.6g')}
    original=read(C/'ab-extension/proof-summary.json')
    paper=read(P/'audit-result.json')
    for (e,k),m in minima.items():
        value=F(m['margin_rational_from_printed_endpoints'])
        assert value==F(paper['capd_printed_margin_rationals'][str(e)][k])
        assert abs(float(value)-original['metrics'][str(e)]['min_margin'][k])<1e-12
    table=[]
    for e,label in enumerate(('OO','OA','AB','BO','BA')):
        sides=[minima[e,k] for k in ('L','R')];c2=min(sides,key=lambda x:F(x['margin_rational_from_printed_endpoints']))
        table.append({'edge':label,'C1':minima[e,'C1'],'C2':c2,'L':minima[e,'L'],'R':minima[e,'R']})
    # Re-run only the original checker scripts in disposable copies. Expected
    # results and all original numerical logs remain byte-for-byte untouched.
    with tempfile.TemporaryDirectory(prefix='r029-review-') as td:
        t=Path(td);tc=t/'independent-capd';th=t/'hset-check'
        for name in ['return_check.cpp','ab-extension/check_coverage.py']+[x['file'] for x in expected['inputs']]:
            dst=tc/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(C/name,dst)
        r=subprocess.run([sys.executable,'-B',str(tc/'ab-extension/check_coverage.py')],capture_output=True,text=True,timeout=120)
        assert r.returncode==0,r.stderr
        actual=read(tc/'ab-extension/coverage-check.json')
        for key in ('source_sha256','inputs','edges','accepted_records','all_five_covering_conditions'):
            assert actual[key]==expected[key],key
        th.mkdir()
        for name in ['check_coverage.py','coverage.jsonl','strips.json']:
            shutil.copyfile(H/name,th/name)
        r=subprocess.run([sys.executable,'-B',str(th/'check_coverage.py')],capture_output=True,text=True,timeout=120)
        assert r.returncode==0,r.stderr
        h=read(th/'coverage-audit.json');old=read(H/'expected-coverage-audit.json')
        for key in ('results','verdict','exact_tree_nodes_checked','adjacency_five_bands','coverage_sha256','checker_sha256'):
            assert h[key]==old[key],key
    out={'status':'PASS_SAVED_RECORD_PROVENANCE_AND_MARGINS','new_ODE_integrations':0,
         'accepted_records':len(records),'M1_records_accepted':0,
         'numerical_source':{'path':'return_check.cpp','sha256':SOURCE},
         'coverage_checker':{'path':'ab-extension/check_coverage.py','sha256':CHECKER},
         'accepted_by_kind':{k:sum(v for (e,kind),v in counts.items() if kind==k) for k in ('C1','L','R')},
         'accepted_by_input_file':dict(byfile),'source_inputs':expected['inputs'],
         'all_native_decisions_are_saved_CELL_PASS':True,
         'margins_are_diagnostics_not_outward_endpoint_certificates':True,'table5_capd_provenance':table,
         'expected_outputs_match_rerun_checkers':True,
         'hset_expected_name':'../hset-check/expected-coverage-audit.json',
         'hset_generated_name':'../hset-check/coverage-audit.json',
         'capd_expected_name':'ab-extension/expected-coverage-check.json',
         'capd_generated_name':'ab-extension/coverage-check.json',
         'pointwise_cross_implementation_enclosure_intersection_tested':False,
         'auditor_sha256':sha(Path(__file__))}
    Path(a.out).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'accepted_records':len(records),'M1_accepted':0,
                     'table5':[{k:v for k,v in x.items() if k=='edge'}|{k:x[k]['table_display_6sig'] for k in ('C1','C2')} for x in table],
                     'new_ODE_integrations':0},indent=2))
if __name__=='__main__':main()
