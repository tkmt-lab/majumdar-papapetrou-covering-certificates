"""Task-local ARM build of pinned CAPD; no install, new runtime or cloud use."""
from pathlib import Path
import datetime,hashlib,json,os,platform,subprocess,time,traceback
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
S=ROOT/'studies/R015/speedup/.cache/CAPD';CMAKE=ROOT/'studies/R015/speedup/.cache/build-venv/bin/cmake';B=P/'.cache/build'
PIN='37057e5899bccaa6cd5701057b7e6ea5e232ef8b';start=time.monotonic();out={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'platform':platform.platform(),'machine':platform.machine(),'status':'ERROR','commands':[],'numeric_trials':0,'native_default_interval':'NATIVE ARM64 rounding implementation in pinned source','numerical_solver_scalar':'MpInterval/MPFR, not the native double interval','global_install':False,'threads':2,'queue_memory_GiB':2}
def run(cmd):
 r=subprocess.run(list(map(str,cmd)),capture_output=True,text=True,timeout=max(1,540-(time.monotonic()-start)),env={**os.environ,'OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
 out['commands'].append({'argv':list(map(str,cmd)),'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});assert r.returncode==0,'build command failed';return r.stdout
try:
 assert run(['git','-C',S,'rev-parse','HEAD']).strip()==PIN
 assert not run(['git','-C',S,'status','--porcelain'])
 raw=subprocess.check_output(['git','-C',str(S),'archive','--format=tar',PIN]);out['capd_archive_sha256']=hashlib.sha256(raw).hexdigest();assert out['capd_archive_sha256']=='960768c4aabfcf55799ca85f0dc2bcf449ed6e0355f46ba19dad8413c4d09024';del raw
 B.mkdir(parents=True,exist_ok=True)
 run([CMAKE,'-S',S,'-B',B,'-DCMAKE_CXX_COMPILER=/opt/homebrew/bin/g++-16','-DCMAKE_C_COMPILER=/opt/homebrew/bin/gcc-16','-DCMAKE_BUILD_TYPE=Release','-DCAPD_ENABLE_MULTIPRECISION=ON','-DCAPD_INTERVAL_TYPE=NATIVE','-DCMAKE_PREFIX_PATH=/opt/homebrew','-DCMAKE_CXX_FLAGS=-I/opt/homebrew/include','-DCMAKE_EXE_LINKER_FLAGS=-L/opt/homebrew/lib'])
 run([CMAKE,'--build',B,'--parallel','2'])
 out['status']='BUILT_PENDING_MULTIPRECISION_CONTROLS';out['capd_config']=str(B/'bin/capd-config');out['compiler']=run(['/opt/homebrew/bin/g++-16','--version'])
except Exception as e:out['error']=str(e);out['traceback']=traceback.format_exc()
finally:
 out['elapsed_seconds']=time.monotonic()-start;out['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();(P/'build-result.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['commands','traceback','compiler']}))
