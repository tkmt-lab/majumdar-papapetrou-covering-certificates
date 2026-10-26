"""Authorized AB scan, admitted only from recorded <=3-hour pilot estimate."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
from collections import deque
import subprocess,time,json,hashlib,datetime,re
P=Path(__file__).resolve().parent;B=P.parent;binary=B/'.cache/return_check'
plan=json.loads((P/'full-plan.json').read_text());admission=json.loads((P/'admission.json').read_text())
assert admission['admit_full'] and admission['conservative_estimate_seconds']<=10800
assert plan['workers']==4 and plan['memory_GiB']==2 and plan['seconds']<=10740
source=hashlib.sha256((B/'return_check.cpp').read_bytes()).hexdigest();bh=hashlib.sha256(binary.read_bytes()).hexdigest()
assert source==admission['numeric_source_sha256'];assert bh==admission['numeric_binary_sha256']
rx=re.compile(r'^CELL (\d+) (C1|L|R) (\d+)/(\d+) (\d+)/(\d+) (PASS|CONTRARY|UNRESOLVED|ERROR)\b',re.M)
def verdict(row):
 m=rx.search(row.get('stdout',''))
 if not m:return row.get('status','ERROR')
 assert [int(m[1]),m[2],*[int(m[i]) for i in range(3,7)]]==row['task']
 return m[7] if row.get('returncode')==0 else 'ERROR'
cache={};provenance={}
for name,sha in admission['pilot_hashes'].items():
 raw=(P/name).read_bytes();assert hashlib.sha256(raw).hexdigest()==sha;d=json.loads(raw);assert d['source_sha256']==source and d['binary_sha256']==bh
 for i,row in enumerate(d['cells']):
  v=verdict(row)
  if v in ['PASS','UNRESOLVED','CONTRARY']:
   cache[tuple(row['task'])]=row;provenance[tuple(row['task'])]={'file':name,'sha256':sha,'index':i}
start=time.monotonic();deadline=start+plan['seconds'];todo=deque(plan['tasks']);seen=set();pending={};out=P/'full-result.json'
r={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorization':'[internal-routing-id]','source_sha256':source,'binary_sha256':bh,'plan':plan,'admission_sha256':hashlib.sha256((P/'admission.json').read_bytes()).hexdigest(),'records':[],'reused':[],'splits':[],'unfinished':[]}
def children(task):
 e,k,iu,nu,is_,ns=task
 if k=='C1' and nu<32:return [[e,k,2*iu,2*nu,is_,ns],[e,k,2*iu+1,2*nu,is_,ns]]
 if ns<128:return [[e,k,iu,nu,2*is_,2*ns],[e,k,iu,nu,2*is_+1,2*ns]]
 return []
def refine(task,v):
 if v not in ['PASS','CONTRARY']:
  child=children(task)
  if child:r['splits'].append({'parent':task,'children':child});todo.extendleft(reversed(child))
def save():
 r['elapsed_seconds']=time.monotonic()-start;r['queued_remaining']=len(todo);r['running_count']=len(pending)
 tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(out)
def execute(task):
 t0=time.monotonic()
 try:
  a=subprocess.run([str(binary),*map(str,task),'reserved'],capture_output=True,text=True,timeout=max(.1,min(60,deadline-time.monotonic())));row={'task':task,'returncode':a.returncode,'stdout':a.stdout,'stderr':a.stderr}
 except subprocess.TimeoutExpired as e:
  dec=lambda s:s.decode(errors='replace') if isinstance(s,bytes) else s or ''
  row={'task':task,'status':'TIMEOUT','stdout':dec(e.stdout),'stderr':dec(e.stderr)}
 row['elapsed_seconds']=time.monotonic()-t0;row['verdict']=verdict(row);return row
with ThreadPoolExecutor(max_workers=4) as pool:
 while todo or pending:
  while todo and len(pending)<4 and time.monotonic()<deadline-1:
   task=todo.popleft();key=tuple(task)
   if key in seen:continue
   seen.add(key)
   if key in cache:
    old=cache[key];v=verdict(old);r['reused'].append({'task':task,'verdict':v,'provenance':provenance[key]});refine(task,v);continue
   pending[pool.submit(execute,task)]=task
  if not pending:break
  done,_=wait(pending,timeout=1,return_when=FIRST_COMPLETED)
  for fut in done:
   task=pending.pop(fut);row=fut.result();r['records'].append(row);refine(task,row['verdict'])
   print(json.dumps({'task':task,'verdict':row['verdict'],'elapsed_seconds':row['elapsed_seconds'],'remaining':len(todo)}),flush=True)
  if done:save()
r['unfinished']=list(todo);r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();r['all_work_exhausted']=not todo;save()
