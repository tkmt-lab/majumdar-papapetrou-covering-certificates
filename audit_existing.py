"""Rerun only the two saved-record checkers and their existing diagnostic predicates."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json,subprocess,hashlib,re,time,resource,datetime
P=Path(__file__).resolve().parent;start=time.monotonic()
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for x in read(P/'evidence-inputs.json')['files']:
 if 'packet_path' in x:
  q=P/x['packet_path'];assert q.stat().st_size==x['bytes'] and sha(q)==x['sha256']
H=P/'evidence/hset-check';C=P/'evidence/independent-capd';A=C/'ab-extension'
for script in [H/'check_coverage.py',A/'check_coverage.py']:
 r=subprocess.run(['python3','-B',str(script)],capture_output=True,text=True,timeout=180)
 (script.parent/'paper-audit.stdout.txt').write_text(r.stdout);(script.parent/'paper-audit.stderr.txt').write_text(r.stderr)
 assert r.returncode==0,(script,r.stderr)
h=read(H/'coverage-audit.json');c=read(A/'coverage-check.json')
assert h['verdict']=='ALL_FIVE_BANDS_PROVED' and h['entropy_conclusion_authorized'] and c['all_five_covering_conditions']
oldh=read(H/'expected-coverage-audit.json');oldc=read(A/'expected-coverage-check.json')
assert h['results']==oldh['results'] and h['adjacency_five_bands']==oldh['adjacency_five_bands']
assert c['edges']==oldc['edges'] and c['accepted_records']==oldc['accepted_records']
# Exact agreement of fixed geometry; these are the two recorded inputs.
bh=read(H/'boxes.json')['boxes'];bc=read(C/'geometry.json')['boxes']
for name,b in bh.items():
 for key in ['center','eu','es']:assert list(map(F,b[key]))==list(map(F,bc[name][key]))
 assert [F(b['ru']),F(b['rs'])]==list(map(F,bc[name]['radius']))
bands=read(H/'strips.json')['strips'];geom=read(C/'geometry.json')
for b in bands:assert list(map(F,b['u']))==[F(x.strip()) for x in geom['strips'][b['source']+'->'+b['target']].strip('[]').split(',')]
assert list(map(F,geom['s']))==[F(-1),F(1)]
# The same printed-diagnostic check used in ab-extension/verify_results.py,
# with a cache to avoid reparsing a large log for each accepted cell.
cache={x['file']:read(C/x['file']) for x in c['inputs']}
for x in c['inputs']:assert sha(C/x['file'])==x['sha256']
rx=re.compile(r'\b(u|s|time|vz)=\[([^,]+),([^\]]+)\]');metrics={};counts=Counter()
for rec in c['accepted_records']:
 assert rec['verdict']=='PASS'
 d=cache[rec['file']];cr=d.get('cells',d.get('records',[]))[rec['row']]
 line=next(s for s in cr['stdout'].splitlines() if s.startswith('CELL '))
 assert cr['returncode']==0 and line.startswith(rec['line'])
 ints={k:(F(lo),F(hi)) for k,lo,hi in rx.findall(line)}
 assert set(ints)=={'u','s','time','vz'} and all(lo<=hi for lo,hi in ints.values())
 assert ints['time'][0]>0 and ints['vz'][0]>0
 scal={k:F(re.search(r'\b'+k+r'=([^ ]+)',line)[1]) for k in ['gap','outer','crossing']};assert min(scal.values())>0
 e,k,*_=rec['task'];margin=1-max(abs(x) for x in ints['s']) if k=='C1' else -1-ints['u'][1] if k=='L' else ints['u'][0]-1;assert margin>0
 counts[e,k]+=1;m=metrics.setdefault(str(e),{});m[k]=min(m.get(k,margin),margin)
assert sum(counts.values())==2381
out={'status':'PASS_SAVED_CERTIFICATES_AND_INPUT_ALIGNMENT','new_ODE_integrations':0,'hset_conditions':15,'hset_successful_cells':sum(x['leaf_count'] for x in h['results']),'hset_tree_nodes':h['exact_tree_nodes_checked'],'capd_accepted_records':sum(counts.values()),'capd_counts':{str(e):{k:counts[e,k] for k in ['C1','L','R']} for e in range(5)},'capd_printed_margin_rationals':{e:{k:str(v) for k,v in m.items()} for e,m in metrics.items()},'capd_printed_values_are_diagnostics':True,'same_exact_box_and_strip_inputs':True,'all_saved_coverings_pass':True,'original_assertions_agree':True,'elapsed_seconds':time.monotonic()-start,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':sha(Path(__file__))}
assert out['elapsed_seconds']<580
(P/'audit-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
