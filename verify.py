"""Bounded saved-evidence checks, conditional on original interval enclosures."""
from fractions import Fraction as F
import json,shutil,subprocess,sys,tempfile
from pathlib import Path
from check_packet import ROOT,require,load,env

def command(root,script,*args):
    r=subprocess.run([sys.executable,'-B',str(root/script),*map(str,args)],cwd=root,
                     capture_output=True,text=True,env=env(),timeout=240)
    require(r.returncode==0,script+' failed:\n'+r.stderr[-3000:])
    return r

def run():
    require(__debug__,'optimized Python is refused')
    with tempfile.TemporaryDirectory(prefix='mp-cover-check-') as td:
        p=Path(td)/'packet'
        shutil.copytree(ROOT,p,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc'))
        command(p,'audit_existing.py')
        audit=load(p/'audit-result.json')
        require(audit['status']=='PASS_SAVED_CERTIFICATES_AND_INPUT_ALIGNMENT','saved audit status')
        require((audit['hset_conditions'],audit['hset_successful_cells'],audit['hset_tree_nodes'],audit['capd_accepted_records'])==(15,768,1521,2381),'certificate counts')
        command(p,'evidence/independent-capd/audit_review_fixes.py','--out',p/'review-new.json')
        review=load(p/'review-new.json')
        require(review['status']=='PASS_SAVED_RECORD_PROVENANCE_AND_MARGINS' and review['M1_records_accepted']==0,'row/margin audit')
        command(p,'evidence/independent-capd/check_geometry.py')
        geometry=load(p/'evidence/independent-capd/geometry-check.json')
        require(geometry==load(ROOT/'evidence/independent-capd/geometry-check.json'),'exact geometry baseline')
        h=load(p/'evidence/hset-check/coverage-audit.json');c=load(p/'evidence/independent-capd/ab-extension/coverage-check.json')
        mapping=load(p/'correspondence.json')['conditions']
        require(len(mapping)==15,'correspondence length')
        edges=['O->O','O->A','A->B','B->O','B->A'];kinds={'C1':'C1','C2L':'L','C2R':'R'}
        require({(x['edge'],x['condition']) for x in mapping}=={(e,k) for e in edges for k in kinds},'correspondence keys')
        for m in mapping:
            edge=edges.index(m['edge']);kind=m['condition']
            row=next(x for x in h['results'] if x['edge']==edge and x['condition']==kind)
            require(row['leaf_certificate_lines']==m['hset']['leaf_certificate_lines'] and row['summary_line']==m['hset']['summary_line'],'binary64 mapping')
            actual=[x for x in c['accepted_records'] if x['task'][0]==edge and x['task'][1]==kinds[kind]]
            require(actual==m['capd']['records'] and len(actual)==m['capd']['count'],'CAPD mapping')
        intervals=[('15.288','15.296'),('15.274','15.284'),('19.070','19.110'),('15.099','15.114'),('15.085','15.100')]
        metrics=load(p/'evidence/independent-capd/ab-extension/proof-summary.json')['metrics']
        for i,(lo,hi) in enumerate(intervals):
            r=metrics[str(i)];require(F(lo)<=F(str(r['time_low']))<=F(str(r['time_high']))<=F(hi),'aggregate time containment')
        require(h['log_rho_rigorous_decimal_interval']==['0.481211825059603','0.481211825059604'],'entropy enclosure')
        return {'status':'PASS','conditions':15,'binary64_leaves':768,'tree_nodes':1521,
                'CAPD_records':2381,'M1_records':0,'correspondence_conditions':15,
                'aggregate_time_containment':5,'new_ODE_integrations':0,
                'scope':'saved certificates and exact finite implications; original interval propagation trusted'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
