"""One bounded Mac job, four numeric processes (no agents), exact task grid."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,wait,FIRST_COMPLETED
from collections import deque
import subprocess,time,json,hashlib,datetime,re
P=Path(__file__).resolve().parent;Q=Path('<workspace>/research/tools/compute/queue')
control=json.loads((P/'controls-result.json').read_text());assert control['control_returncode']==0
source=hashlib.sha256((P/'return_check.cpp').read_bytes()).hexdigest();assert source==control['source_sha256']
prior=json.loads((P/'resource-ledger.json').read_text());spent=0
for rec in prior['rows']:
 j=json.loads((Q/rec['id']/'job.json').read_text());assert j.get('finished'),j['id']
 spent+=(datetime.datetime.fromisoformat(j['finished'])-datetime.datetime.fromisoformat(j['started'])).total_seconds()
CAP=2100;assert spent+CAP+60<=3600,(spent,CAP)
plan=json.loads((P/'coverage-plan.json').read_text());assert plan['seconds']==CAP and plan['workers']==4
rx=re.compile(r'^CELL (\d+) (C1|L|R) (\d+)/(\d+) (\d+)/(\d+) (PASS|CONTRARY|UNRESOLVED|ERROR)\b',re.M)
def verdict(row):
 m=rx.search(row.get('stdout',''))
 if not m:return row.get('status','ERROR')
 assert [int(m[1]),m[2],*[int(m[i]) for i in range(3,7)]]==row['task']
 return m[7]
cache={};provenance={}
for name in ['refined-pilot-result.json','refinement-feasibility-result.json']:
 raw=(P/name).read_bytes();d=json.loads(raw);assert d['source_sha256']==source
 for i,row in enumerate(d['cells']):
  if row.get('returncode')==0 and verdict(row)=='PASS':cache[tuple(row['task'])]=row;provenance[tuple(row['task'])]={'file':name,'sha256':hashlib.sha256(raw).hexdigest(),'index':i}
start=time.monotonic();wall_deadline=datetime.datetime(2026,10,26,1,35,7,tzinfo=datetime.timezone.utc);wall_remaining=(wall_deadline-datetime.datetime.now(datetime.timezone.utc)).total_seconds()
if wall_remaining<=0:
 (P/'coverage-admission-stop.json').write_text(json.dumps({'reason':'8-hour wall deadline passed before queue admission','wall_deadline_utc':wall_deadline.isoformat()},indent=2)+'\n');raise SystemExit(2)
deadline=start+min(CAP,wall_remaining);todo=deque(plan['tasks']);seen=set();pending={};out=P/'coverage-result.json'
r={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':source,'binary_sha256':hashlib.sha256((P/'.cache/return_check').read_bytes()).hexdigest(),'plan':plan,'prior_conservative_queue_seconds':spent,'wall_deadline_utc':wall_deadline.isoformat(),'effective_seconds':min(CAP,wall_remaining),'records':[],'reused':[],'splits':[],'unfinished':[]}
def save():
 r['elapsed_seconds']=time.monotonic()-start;r['queued_remaining']=len(todo);r['running_count']=len(pending)
 tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');tmp.replace(out)
def execute(task):
 t0=time.monotonic();cmd=[str(P/'.cache/return_check'),*map(str,task),'reserved']
 try:
  a=subprocess.run(cmd,capture_output=True,text=True,timeout=max(.1,min(60,deadline-time.monotonic())));row={'task':task,'returncode':a.returncode,'stdout':a.stdout,'stderr':a.stderr}
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
   if key in cache:r['reused'].append({'task':task,'provenance':provenance[key],'record':cache[key]});continue
   pending[pool.submit(execute,task)]=task
  if not pending:break
  done,_=wait(pending,timeout=1,return_when=FIRST_COMPLETED)
  for fut in done:
   task=pending.pop(fut);row=fut.result();r['records'].append(row)
   if row['verdict'] not in ['PASS','CONTRARY']:
    e,k,iu,nu,is_,ns=task;children=[]
    if k=='C1' and nu<16:children=[[e,k,2*iu,2*nu,is_,ns],[e,k,2*iu+1,2*nu,is_,ns]]
    elif ns<64:children=[[e,k,iu,nu,2*is_,2*ns],[e,k,iu,nu,2*is_+1,2*ns]]
    if children:r['splits'].append({'parent':task,'children':children});todo.extendleft(reversed(children))
   print(json.dumps({'task':task,'verdict':row['verdict'],'elapsed_seconds':row['elapsed_seconds'],'remaining':len(todo)}),flush=True)
  if done:save()
  if time.monotonic()>=deadline and not pending:break
r['unfinished']=list(todo);r['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();r['all_work_exhausted']=not todo;r['queued_remaining']=len(todo);r['running_count']=0;save()
