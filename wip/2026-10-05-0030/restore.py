"""Restore the exact dated WIP model bytes without running modeling recipes."""
from pathlib import Path
import argparse,gzip,hashlib,json
ROOT=Path(__file__).resolve().parent

def safe(root,relative):
    root=root.resolve();path=(root/relative).resolve()
    if not path.is_relative_to(root) or path==root:raise ValueError('Unsafe path: '+relative)
    return path

def check(data,item):
    if len(data)!=item['bytes'] or hashlib.sha256(data).hexdigest()!=item['sha256']:
        raise ValueError('Checksum mismatch: '+item.get('path',item.get('name','model')))

def restore(output,names):
    data=json.loads((ROOT/'MANIFEST.json').read_text())
    for m in data['models']:
        if names and m['name'] not in names:continue
        parts=[]
        for p in m['parts']:
            b=safe(ROOT,p['path']).read_bytes();check(b,p);parts.append(b)
        glb=gzip.decompress(b''.join(parts));check(glb,m)
        dest=safe(output,m['restored_path'])
        if dest.exists() and dest.read_bytes()!=glb:raise FileExistsError('Refusing to replace changed model: '+str(dest))
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(glb)
        print('Verified WIP model: '+m['name'])
    if names and not names.issubset({m['name'] for m in data['models']}):raise ValueError('Unknown model name')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,default=ROOT/'restored');ap.add_argument('--model',action='append',default=[]);a=ap.parse_args();restore(a.output,set(a.model))
