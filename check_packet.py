"""Distribution integrity, provenance and PDF checks. No numerical solver."""
from pathlib import Path
import argparse,hashlib,json,re,subprocess,sys,os
ROOT=Path(__file__).resolve().parent

def require(ok,message):
    if not ok:raise RuntimeError(message)
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
        and not any(x in ('.git','__pycache__') for x in p.relative_to(ROOT).parts)
        and p.name not in ('MANIFEST.sha256','.DS_Store') and p.suffix!='.pyc')
def manifest():return ''.join(sha(p)+'  '+str(p.relative_to(ROOT))+'\n' for p in files())
def env():
    e=os.environ.copy();e.pop('PYTHONOPTIMIZE',None)
    e.update(PYTHONDONTWRITEBYTECODE='1',OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')
    return e
def main(write=False):
    require(__debug__,'optimized Python is refused')
    if write:
        (ROOT/'MANIFEST.sha256').write_text(manifest());return {'status':'MANIFEST_WRITTEN','files':len(files())}
    require((ROOT/'MANIFEST.sha256').read_text()==manifest(),'file membership/size/hash mismatch')
    for r in load(ROOT/'provenance.json')['files']:
        p=ROOT/r['path'];require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'export provenance: '+r['path'])
    for r in load(ROOT/'evidence-inputs.json')['files']:
        p=ROOT/r['packet_path'];require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],'evidence inventory: '+r['packet_path'])
    # Local paths/routing identifiers are checked in all text and PDF metadata.
    pattern=re.compile('|'.join([r'/'+x+r'/' for x in ('Users','Volumes','home','root')])
        +r'|[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}|BEGIN '+r'(?:RSA |OPENSSH )?PRIVATE KEY|\.ts\.net\b')
    for p in files():
        if p.suffix=='.pdf':continue
        require(not pattern.search(p.read_text()),'local/private identifier: '+str(p.relative_to(ROOT)))
    text=subprocess.check_output(['pdftotext',str(ROOT/'paper.pdf'),'-'],text=True,timeout=30)
    info=subprocess.check_output(['pdfinfo',str(ROOT/'paper.pdf')],text=True,timeout=30)
    require(not pattern.search(text+info),'PDF local/private identifiers')
    require('Version 1.0.0' in text and re.search(r'Pages:\s+10\b',info),'PDF version/page count')
    require('0.481211825059603' in text,'PDF entropy bound')
    c=load(ROOT/'claims.json')
    for claim in c['claims']:
        for ref in claim['evidence']:require((ROOT/ref).is_file(),'missing claim evidence: '+ref)
    for d in c['certificate_documentation']:require((ROOT/d['path']).is_file(),'missing method: '+d['path'])
    require(c['paper_version']=='1.0.0' and len(c['claims'])==6,'claim version/count')
    require(load(ROOT/'.zenodo.json')['version']=='1.0.0','Zenodo version')
    require('version: 1.0.0' in (ROOT/'CITATION.cff').read_text(),'citation version')
    require((ROOT/'body.tex').read_text().count('VERIFICATION-RECORD.md')==1,'one verification-history reference')
    require(all(not p.is_symlink() for p in files()),'symlink not permitted')
    return {'status':'PASS','files':len(files()),'bytes':sum(p.stat().st_size for p in files()),'pdf_pages':10}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--write-manifest',action='store_true');args=ap.parse_args()
    print(json.dumps(main(args.write_manifest),indent=2))
