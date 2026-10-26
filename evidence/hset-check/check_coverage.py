"""Exact dyadic tree audit of the emitted certificates; does not rerun ODE."""
from pathlib import Path
from fractions import Fraction as F
from itertools import permutations
from math import isqrt
import json, time, resource, hashlib, sys
p=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent; start=time.monotonic()
rows=[json.loads(x) for x in (p/'coverage.jsonl').read_text().splitlines()]
bands=json.loads((p/'strips.json').read_text())['strips']
def cell(r):return tuple(F(v) for key in ('u','s') for v in r[key])
def mul(a,b):
 c=[0]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):c[i+j]+=x*y
 return c
def charpoly(A):
 n=len(A);out=[0]*(n+1)
 for perm in permutations(range(n)):
  sign=(-1)**sum(perm[i]>perm[j] for i in range(n) for j in range(i+1,n));poly=[sign]
  for i,j in enumerate(perm):poly=mul(poly,[-A[i][j],1] if i==j else [-A[i][j]])
  for i,v in enumerate(poly):out[i]+=v
 return out
results=[]; count=0
for e,b in enumerate(bands):
 for kind in ('C2L','C2R','C1'):
  selected=[(ln,r) for ln,r in enumerate(rows,1) if r.get('edge')==e and r.get('condition')==kind]
  nodes={r['path']:(ln,r) for ln,r in selected if r.get('coverage_node')}
  certs={r['path']:(ln,r) for ln,r in selected if r.get('kind')=='coverage_cell'}
  summaries=[(ln,r) for ln,r in selected if r.get('task_summary')]
  assert len(summaries)==1
  assert len(nodes)==sum(bool(r.get('coverage_node')) for _,r in selected)
  assert len(certs)==sum(r.get('kind')=='coverage_cell' for _,r in selected)
  u0=F(b['u'][1] if kind=='C2R' else b['u'][0]);u1=F(b['u'][1]) if kind=='C1' else u0
  todo=[('',(u0,u1,F(-1),F(1)))];visited=set();leafs=[];nonproof=[]
  while todo:
   path,expected=todo.pop();ln,r=nodes[path];assert cell(r)==expected and path not in visited;visited.add(path)
   a,c,d,f=expected;act=r['action'];count+=1
   if act=='split':
    if r['axis']=='s':m=(d+f)/2;left=(a,c,d,m);right=(a,c,m,f)
    else:assert r['axis']=='u' and kind=='C1';m=(a+c)/2;left=(a,m,d,f);right=(m,c,d,f)
    todo.extend([(path+'0',left),(path+'1',right)])
   elif act=='leaf':
    cln,cr=certs[path];assert cell(cr)==expected and cr['source']==b['source'] and cr['target']==b['target']
    assert cr['return_proved'] and cr['condition_proved'] and cr['reason']=='validated_first_upward_return'
    assert F(cr['rmin_lower'])>F(1,5) and F(cr['R2_upper'])<64
    assert F(cr['vz_lower_event'])>0 and cr['z_before_upper']<0<cr['z_after_lower']
    assert 0<cr['tau'][0]<cr['tau'][1]<=60 and cr['down_windows']==1
    coord=cr['target_coordinates'][b['target']];U,S=coord['U'],coord['S']
    assert (-1<F(S[0])<=F(S[1])<1) if kind=='C1' else (F(U[1])<-1 if kind=='C2L' else F(U[0])>1)
    leafs.append((cln,cr))
   else:assert act in ('unresolved','pending_budget');nonproof.append((ln,r))
  assert visited==set(nodes)
  sln,summary=summaries[0];complete=not nonproof
  assert summary['complete']==complete and summary['leaves']==len(leafs)
  result={'edge':e,'source':b['source'],'target':b['target'],'condition':kind,'complete':complete,'leaf_count':len(leafs),'unresolved_count':len(nonproof),'summary_line':sln,'tree_nodes':len(nodes),'nonproof_lines':[ln for ln,r in nonproof]}
  if leafs:
   key='S' if kind=='C1' else 'U';pairs=[r['target_coordinates'][b['target']][key] for _,r in leafs]
   result.update(coordinate=key,image_hull=[min(v[0] for v in pairs),max(v[1] for v in pairs)],tau_hull=[min(r['tau'][0] for _,r in leafs),max(r['tau'][1] for _,r in leafs)],rmin_lower=min(r['rmin_lower'] for _,r in leafs),R2_upper=max(r['R2_upper'] for _,r in leafs),vz_lower=min(r['vz_lower_event'] for _,r in leafs),leaf_certificate_lines=[ln for ln,r in leafs])
  results.append(result)
all_pass=all(r['complete'] for r in results)
# State splitting is necessary because distinct outgoing bands share a parent box.
A=[[1,1,0],[0,0,1],[1,1,0]]
B=[[int(x['target']==y['source']) for y in bands] for x in bands]
assert charpoly(A)==[0,-1,-1,1] and charpoly(B)==[0,0,0,-1,-1,1]
# sqrt(5) and log(phi)=2*atanh(sqrt(5)-2), entirely rational.
D=10**30;k=isqrt(5*D*D);rootlo,roothi=F(k,D),F(k+1,D)
assert rootlo**2<=5<=roothi**2
zl,zh=rootlo-2,roothi-2;terms=30
lower=2*sum(zl**(2*j+1)/F(2*j+1) for j in range(terms))
upper=2*sum(zh**(2*j+1)/F(2*j+1) for j in range(terms))+2*zh**(2*terms+1)/F(2*terms+1)/(1-zh*zh)
# Decimal integers are outward rounded from the rational series bounds.
scale=10**15;lo_dec=lower.numerator*scale//lower.denominator;hi_dec=-(-upper.numerator*scale//upper.denominator)
out={'verdict':'ALL_FIVE_BANDS_PROVED' if all_pass else 'NOT_ALL_FIVE_PROVED','interpretation':'binary64 JSON numbers are parsed as the same exact binary endpoints; tree check is independent of solver traversal, ODE mathematics still trusted as documented','exact_tree_nodes_checked':count,'results':results,'adjacency_original':A,'adjacency_five_bands':B,'charpoly_original_ascending':charpoly(A),'charpoly_bands_ascending':charpoly(B),'rho':'(1+sqrt(5))/2','log_rho_rigorous_decimal_interval':[f'{lo_dec//scale}.{lo_dec%scale:015}',f'{hi_dec//scale}.{hi_dec%scale:015}'],'entropy_conclusion_authorized':all_pass,'log_series_terms':terms,'wall_seconds':time.monotonic()-start,'cpu_seconds':resource.getrusage(resource.RUSAGE_SELF).ru_utime+resource.getrusage(resource.RUSAGE_SELF).ru_stime,'peak_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'coverage_sha256':hashlib.sha256((p/'coverage.jsonl').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(p/'coverage-audit.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='results'},indent=2))
for r in results:print(json.dumps({k:v for k,v in r.items() if k not in ('leaf_certificate_lines','nonproof_lines')}))
