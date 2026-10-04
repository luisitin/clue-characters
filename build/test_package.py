"""Small corruption and path-safety regression tests (standard library only)."""
import struct
import unittest
from package_io import ROOT, parse_glb, safe_path, sha256, verify_bytes

class PackageTests(unittest.TestCase):
    def test_hash_rejects_changed_bytes(self):
        entry = {"path": "example", "bytes": 3, "sha256": sha256(b"abc")}
        verify_bytes(b"abc", entry)
        with self.assertRaises(ValueError):
            verify_bytes(b"abd", entry)

    def test_path_cannot_escape_root(self):
        with self.assertRaises(ValueError):
            safe_path(ROOT, "../outside")

    def test_invalid_glb_header(self):
        with self.assertRaises(ValueError):
            parse_glb(b"not a glb")
        with self.assertRaises(ValueError):
            parse_glb(struct.pack("<4sII", b"glTF", 1, 20) + bytes(8))

if __name__ == "__main__":
    unittest.main()
