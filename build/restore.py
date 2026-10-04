"""Restore exact current.glb files from checked, deterministic gzip parts."""
import argparse
import gzip
import os
from pathlib import Path
import tempfile
from package_io import ROOT, load_manifest, safe_path, sha256, verify_bytes, verify_stored_files

def restore(output):
    manifest = load_manifest()
    verify_stored_files(manifest)
    for model in manifest["models"]:
        if model["storage"] == "direct":
            data = safe_path(ROOT, model["path"]).read_bytes()
        elif model["storage"] == "gzip-parts":
            compressed = b"".join(safe_path(ROOT, part).read_bytes() for part in model["parts"])
            if len(compressed) != model["gzip_bytes"] or sha256(compressed) != model["gzip_sha256"]:
                raise ValueError(f"Compressed stream mismatch: {model['name']}")
            data = gzip.decompress(compressed)
        else:
            raise ValueError("Unknown storage format")
        verify_bytes(data, model)
        target = safe_path(output, model["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            verify_bytes(target.read_bytes(), model)
        else:
            fd, temporary = tempfile.mkstemp(prefix=".restore-", dir=target.parent)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(data)
                os.replace(temporary, target)
            finally:
                if Path(temporary).exists():
                    Path(temporary).unlink()
        print(f"Restored {model['path']}: {len(data):,} bytes, SHA-256 verified")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT, help="Destination root (default: repository root)")
    restore(parser.parse_args().output)
