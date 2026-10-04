"""Extract exact embedded image bytes for editing, without image conversion."""
import argparse
from pathlib import Path
from package_io import ROOT, load_manifest, safe_path, parse_glb, verify_bytes

def extract(source, output):
    suffixes = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}
    for model in load_manifest()["models"]:
        data = safe_path(source, model["path"]).read_bytes()
        verify_bytes(data, model)
        document, binary = parse_glb(data)
        for index, image in enumerate(document.get("images", [])):
            view = document["bufferViews"][image["bufferView"]]
            start = view.get("byteOffset", 0)
            suffix = suffixes.get(image.get("mimeType"), ".bin")
            target = safe_path(output, f"{model['name']}/image-{index:02d}{suffix}")
            target.parent.mkdir(parents=True, exist_ok=True)
            content = binary[start:start + view["byteLength"]]
            if target.exists() and target.read_bytes() != content:
                raise ValueError(f"Refusing to overwrite edited image: {target}")
            target.write_bytes(content)
            print(target)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "build-output" / "embedded-textures")
    args = parser.parse_args()
    extract(args.source, args.output)
