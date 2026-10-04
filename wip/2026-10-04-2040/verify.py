"""Verify the frozen checkpoint bytes and archived recipe members."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parent
M=json.loads((ROOT/'MANIFEST.json').read_text())
for x in M['files']:
    p=(ROOT/x['path']).resolve()
    if not p.is_relative_to(ROOT) or p==ROOT:raise ValueError('Unsafe manifest path')
    b=p.read_bytes()
    if len(b)!=x['bytes'] or hashlib.sha256(b).hexdigest()!=x['sha256']:raise ValueError('Mismatch: '+x['path'])
for archive in M['recipe_archives']:
    with zipfile.ZipFile(ROOT/archive['path']) as z:
        if z.testzip() is not None:raise ValueError('Corrupt recipe archive')
        for info in z.infolist():
            if Path(info.filename).is_absolute() or '..' in Path(info.filename).parts:raise ValueError('Unsafe member')
        print('Verified recipe archive: '+archive['path'])
print('Checkpoint integrity passed. This is not a procedural replay or appearance approval.')
