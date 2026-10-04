# Six custom Clue characters

An isolated snapshot of six custom, unofficial character models: **Green, Mustard, Peacock, Plum, Scarlett and White**. These are unfinished work-in-progress assets, not official game models. Snapshot date: 2026-10-04.

## Get the complete models

The repository keeps durable, checksummed bytes for all six models. Plum is stored directly. The other five are stored as numbered pieces of a deterministic gzip stream so they can be transferred reliably. The pieces are not individually usable 3D models.

With Python 3.10 or newer, run from the repository root:

```sh
python3 build/restore.py
python3 build/validate.py
```

This creates `characters/<name>/current.glb` for all six characters, byte-for-byte identical to the recorded WIP exports. Every GLB embeds its required material images; no private checkout or external texture downloads are needed. Restoration refuses to overwrite a changed local model. Use `--output another-directory` to restore a clean copy separately.

Alternatively, open the repository's **Actions** tab, select a successful **Restore and validate character snapshot** run, and download its **six-character-wip-glbs** artifact. Artifacts are kept for seven days; the numbered model parts in Git remain the durable source and can always be restored locally.

## What is included

- `characters/`: the exact held, coherent whole-character snapshots and their compressed storage parts
- `textures/`: four unique generated painting inputs; current production maps are also embedded in the GLBs
- `manifest.json`: file sizes, SHA-256 hashes, storage layout and exact restored-model hashes
- `build/`: portable restore, extraction and integrity-check scripts using only Python's standard library
- `PROVENANCE.md` and `licenses/`: source and license scope notes

To extract every current embedded texture without altering its bytes:

```sh
python3 build/extract_textures.py
```

The result is written to `build-output/embedded-textures/<name>/`. Models can also be imported into a GLB-capable editor such as Blender. This snapshot reproduces the recorded exports exactly; it does **not** claim to include the complete from-original modeling history or all procedural authoring dependencies.

## Current state

| Character | Snapshot | Triangles | Important open work |
| --- | --- | ---: | --- |
| Green | Sleeve38 assembly | 167,061 | New sleeve has diagnostic cloth color/UV; eyes/lips, other hand/case, shoes and full-character review remain open |
| Mustard | Pointing context83 | 184,355 | New pointing hand and cuff/lining are assembled; gripping hand/cane, head, boots and coherent outfit materials remain open |
| Peacock | Face/eye/chin87 | 187,937 | One physical near eye and a chin-copy repair are present; lower-lid appearance, far eye, face/neck and body work remain open |
| Plum | Raw cleanup003 | 84,219 | Only proven exact duplicate/degenerate faces were removed; experimental replacement anatomy is not integrated |
| Scarlett | Lip-corner softness06 | 153,745 | Local hair/lip refinements remain WIP; eye reconstruction and broader character work are open |
| White | Refined face17 | 196,208 | Local facial refinements remain WIP; temporary 800px orbital-skin color transfer and unfinished body/garments remain |

None is approved as a finished character. Counts are snapshot inventory, not a quality target or visual approval. See the per-character metadata in `manifest.json` for exact bytes and hashes.

## Validation scope

GitHub Actions uses a standard `ubuntu-latest` runner. It reconstructs the models, verifies all stored/restored hashes, checks GLB 2 headers/chunks, buffer ranges and embedded images, and uploads the six models. It does not render them, check likeness, certify anatomy, test intersections, or declare them production-ready.

## Licensing

Public availability is not a blanket license grant. No new license is assigned here to the original custom models, original artwork or generated paint inputs. The separately identified MakeHuman donor asset data used in Green/Mustard is CC0; that does not make the entire characters CC0. See [PROVENANCE.md](PROVENANCE.md).
