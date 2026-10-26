"""Same bounded, read-only packet checks as CI and clean-clone preflight."""
import json,subprocess,sys
from check_packet import ROOT,require,env

def main():
    require(__debug__,'optimized Python is refused')
    results=[]
    for name in ('check_packet.py','verify.py','negative_controls.py','check_packet.py'):
        r=subprocess.run([sys.executable,'-B',str(ROOT/name)],cwd=ROOT,env=env(),capture_output=True,text=True,timeout=480)
        require(r.returncode==0,name+' failed:\n'+r.stdout[-1000:]+r.stderr[-3000:])
        results.append({'check':name,'result':json.loads(r.stdout)})
    print(json.dumps({'status':'PASS','checks':results,'new_ODE_integrations':0},indent=2))
if __name__=='__main__':main()
