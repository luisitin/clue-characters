"""Verify stored bytes and restored GLB structure. This is not visual QA."""
import argparse
from pathlib import Path
from package_io import ROOT, load_manifest, safe_path, verify_bytes, verify_stored_files, parse_glb

def validate(output):
    manifest = load_manifest()
    expected = {"green", "mustard", "peacock", "plum", "scarlett", "white"}
    if {m["name"] for m in manifest["models"]} != expected or len(manifest["models"]) != 6:
        raise ValueError("Manifest must identify exactly six characters")
    verify_stored_files(manifest)
    for model in manifest["models"]:
        data = safe_path(output, model["path"]).read_bytes()
        verify_bytes(data, model)
        document, _ = parse_glb(data)
        primitives = sum(len(m.get("primitives", [])) for m in document.get("meshes", []))
        print(f"PASS {model['name']}: exact bytes, GLB 2, {primitives} primitives, {len(document.get('images', []))} embedded images")
    print("All six snapshot files pass integrity and structural checks. Appearance, anatomy and production readiness are not tested.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT, help="Root containing restored characters")
    validate(parser.parse_args().output)
