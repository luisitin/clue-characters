"""Standard-library helpers for the portable character snapshot."""
from pathlib import Path
import hashlib
import json
import struct

ROOT = Path(__file__).resolve().parents[1]

def safe_path(root, relative):
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or path == root:
        raise ValueError(f"Unsafe relative path: {relative}")
    return path

def load_manifest():
    data = json.loads((ROOT / "manifest.json").read_text())
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported manifest schema")
    return data

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def verify_bytes(data, entry):
    if len(data) != entry["bytes"] or sha256(data) != entry["sha256"]:
        raise ValueError(f"Size or SHA-256 mismatch: {entry['path']}")

def verify_stored_files(manifest):
    for entry in manifest["files"]:
        verify_bytes(safe_path(ROOT, entry["path"]).read_bytes(), entry)

def parse_glb(data):
    if len(data) < 20:
        raise ValueError("Truncated GLB")
    magic, version, length = struct.unpack_from("<4sII", data)
    if magic != b"glTF" or version != 2 or length != len(data):
        raise ValueError("Invalid GLB magic, version or length")
    chunks = []
    offset = 12
    while offset < len(data):
        if offset + 8 > len(data):
            raise ValueError("Truncated GLB chunk header")
        size, kind = struct.unpack_from("<II", data, offset)
        offset += 8
        if size % 4 or offset + size > len(data):
            raise ValueError("Invalid GLB chunk alignment or range")
        chunks.append((kind, data[offset:offset + size]))
        offset += size
    if not chunks or chunks[0][0] != 0x4E4F534A:
        raise ValueError("First GLB chunk must be JSON")
    if len(chunks) != 2 or chunks[1][0] != 0x004E4942:
        raise ValueError("This snapshot expects one JSON and one BIN chunk")
    document = json.loads(chunks[0][1])
    binary = chunks[1][1]
    if document.get("asset", {}).get("version") != "2.0":
        raise ValueError("Unexpected glTF version")
    buffers = document.get("buffers", [])
    if len(buffers) != 1 or "uri" in buffers[0]:
        raise ValueError("Snapshot GLBs must contain one embedded buffer")
    length = buffers[0]["byteLength"]
    if length > len(binary) or len(binary) - length > 3:
        raise ValueError("Invalid embedded buffer size")
    for view in document.get("bufferViews", []):
        start = view.get("byteOffset", 0)
        size = view["byteLength"]
        if view.get("buffer", 0) != 0 or start < 0 or size < 0 or start + size > length:
            raise ValueError("Invalid bufferView range")
    views = document.get("bufferViews", [])
    for image in document.get("images", []):
        if "uri" in image or not 0 <= image.get("bufferView", -1) < len(views):
            raise ValueError("Snapshot images must use valid embedded bufferViews")
    return document, binary
