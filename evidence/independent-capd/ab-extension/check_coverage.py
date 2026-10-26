"""Independent exact union-of-parameter-cells checker; never trusts job exit0 alone."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,re,datetime
A=Path(__file__).resolve().parent;P=A.parent;source=hashlib.sha256((P/'return_check.cpp').read_bytes()).hexdigest()
rx=re.compile(r'^CELL (\d+) (C1|L|R) (\d+)/(\d+) (\d+)/(\d+) (PASS|CONTRARY|UNRESOLVED|ERROR)\b',re.M)
def union_length(intervals):
 seg=sorted(intervals);end=F(0);total=F(0)
 for lo,hi in seg:
  assert 0<=lo<=hi<=1
  if hi>end:total+=hi-max(lo,end);end=hi
 return total
def area(rects):
 xs=sorted({F(0),F(1)}|{x for a,b,_,_ in rects for x in [a,b]});out=F(0)
 for a,b in zip(xs,xs[1:]):
  intervals=[(c,d) for l,r,c,d in rects if l<=a and b<=r]
  out+=(b-a)*union_length(intervals)
 return out
# Overlap must not be counted twice; a mixed-resolution cover must be complete.
assert union_length([(F(0),F(3,4)),(F(1,2),F(1))])==1
assert area([(F(0),F(1,2),F(0),F(1)),(F(1,2),F(1),F(0),F(1,2))])==F(3,4)
assert area([(F(0),F(1,2),F(0),F(1)),(F(1,2),F(1),F(0),F(1,2)),(F(1,2),F(1),F(1,2),F(1))])==1
cells={};inputs=[]
for name in ['refined-pilot-result.json','refinement-feasibility-result.json','coverage-result.json','ab-extension/pilot-result.json','ab-extension/refine-pilot-result.json','ab-extension/full-result.json']:
 p=P/name
 if not p.exists():continue
 raw=p.read_bytes();r=json.loads(raw);assert r['source_sha256']==source
 inputs.append({'file':name,'sha256':hashlib.sha256(raw).hexdigest(),'finished_utc':r.get('finished_utc')})
 rows=r.get('cells',r.get('records',[]))
 for i,c in enumerate(rows):
  if c.get('returncode')!=0:continue
  m=rx.search(c.get('stdout',''))
  if not m:continue
  task=[int(m[1]),m[2],*[int(m[k]) for k in range(3,7)]];assert task==c['task']
  e,k,iu,nu,is_,ns=task;assert 0<=e<5 and 0<=iu<nu and 0<=is_<ns
  if m[7] not in ['PASS','CONTRARY']:continue
  key=tuple(task);rec={'task':task,'verdict':m[7],'file':name,'row':i,'line':m[0]}
  if key in cells:assert cells[key]['verdict']==m[7]
  cells[key]=rec
edges=['O->O','O->A','A->B','B->O','B->A'];result=[]
for e,label in enumerate(edges):
 rect=[];left=[];right=[];bad=[]
 for task,rec in cells.items():
  ee,k,iu,nu,is_,ns=task
  if ee!=e:continue
  if rec['verdict']=='CONTRARY':bad.append(rec);continue
  if k=='C1':rect.append((F(iu,nu),F(iu+1,nu),F(is_,ns),F(is_+1,ns)))
  elif k=='L':left.append((F(is_,ns),F(is_+1,ns)))
  elif k=='R':right.append((F(is_,ns),F(is_+1,ns)))
 a,l,r=area(rect),union_length(left),union_length(right)
 c1='FAIL_COUNTEREXAMPLE' if any(x['task'][1]=='C1' for x in bad) else 'PASS' if a==1 else 'UNRESOLVED'
 c2='FAIL_COUNTEREXAMPLE' if any(x['task'][1] in ['L','R'] for x in bad) else 'PASS' if l==r==1 else 'UNRESOLVED'
 result.append({'edge':label,'C1':c1,'C2':c2,'covered_parameter_area_C1':str(a),'covered_left_fraction':str(l),'covered_right_fraction':str(r),'contrary_records':bad})
out={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':source,'inputs':inputs,'method':'exact rational union of finite closed rectangles/segments in normalized strip parameters; area1 iff full coverage; only rc0 CELL PASS accepted','edges':result,'all_five_covering_conditions':all(x['C1']==x['C2']=='PASS' for x in result),'entropy_bound_status':'CONFIRMED_COVERING_PREMISES' if all(x['C1']==x['C2']=='PASS' for x in result) else 'CONDITIONAL_ONLY_GOLDEN_RATIO_GRAPH_DOES_NOT_ESTABLISH_DYNAMICAL_BOUND','accepted_records':list(cells.values())};(A/'coverage-check.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='accepted_records'},indent=2))
