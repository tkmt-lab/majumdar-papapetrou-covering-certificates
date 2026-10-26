from pathlib import Path
import subprocess,time,json,hashlib,datetime
P=Path(__file__).resolve().parent;ROOT=P.parents[2];S=ROOT/'studies/R015/speedup/.cache/CAPD';B=P/'.cache/build'
g=json.loads((P/'geometry.json').read_text());out=[]
for b in g['boxes'].values():out.append(b['center']+b['eu']+b['es']+b['radius'])
quote=lambda x:json.dumps(x)
rp='sqrt(x^2+(z-1)^2)';rm='sqrt(x^2+(z+1)^2)';U=f'(1+1/{rp}+1/{rm})';gx=f'(-x/({rp})^3-x/({rm})^3)';gz=f'(-(z-1)/({rp})^3-(z+1)/({rm})^3)';dot=f'({gx}*vx+{gz}*vz)'
field=f'var:x,z,vx,vz;fun:vx,vz,2/{U}*({gx}-vx*{dot}),2/{U}*({gz}-vz*{dot});'
h='const char* BOXES[3][8]={'+','.join('{'+','.join(map(quote,b))+'}' for b in out)+'};\n'
h+='const int SOURCES[5]={0,0,1,2,2},TARGETS[5]={0,1,2,0,1};\n'
h+='const char* STRIPS[5][2]={'+','.join('{'+','.join(map(quote,s.strip('[]').split(', ')))+'}' for s in g['strips'].values())+'};\n'
h+='const char* FIELD='+quote(field)+';\n';(P/'geometry_generated.h').write_text(h)
cmd=['/opt/homebrew/bin/g++-16','-std=c++17','-O2','-frounding-math','-D__USE_NATIVE__','-D__HAVE_MPFR__']
for sub in ['capdDynSys','capdAlg','capdAux','capdExt']:cmd+=['-I'+str(S/sub/'include')]
cmd+=['-I/opt/homebrew/include',str(P/'return_check.cpp'),'-L'+str(B),'-L/opt/homebrew/lib','-lcapd','-lmpfr','-lgmp','-o',str(P/'.cache/return_check')]
start=time.monotonic();r=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
res={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'compile_argv':cmd,'compile_returncode':r.returncode,'compile_stdout':r.stdout,'compile_stderr':r.stderr,'source_sha256':hashlib.sha256((P/'return_check.cpp').read_bytes()).hexdigest()}
if r.returncode==0:
 t=subprocess.run([str(P/'.cache/return_check'),'controls'],capture_output=True,text=True,timeout=120);res.update(control_returncode=t.returncode,control_stdout=t.stdout,control_stderr=t.stderr)
res['elapsed_seconds']=time.monotonic()-start;(P/'controls-result.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res));raise SystemExit(r.returncode or res.get('control_returncode',1))
