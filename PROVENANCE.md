# Provenance and license scope

## Original custom character sources

The six original character meshes and their existing textures were supplied as project assets. Their names identify custom, unofficial character interpretations. This repository preserves a bounded WIP export of each character and does not include any other application content or prior repository history. No new ownership or blanket redistribution license is asserted for those original assets or the supplied reference artwork.

The GLB files preserve source provenance metadata where present. Each restored file's exact hash is recorded in `manifest.json`. The procedural refinements and painting work are unfinished and should be assessed in an actual 3D viewer before use.

## Generated painting inputs

Four image-generation outputs are preserved because they cannot be recreated byte-for-byte from a text prompt:

- `textures/green/hand-skin-paint-plate.png`: multi-view skin-paint input used for the rebuilt hand; exact source projection, registration and baking are separate modeling steps.
- `textures/mustard/skin-albedo-source.png`: neutral skin microcolor input used in the pointing-hand material work.
- `textures/mustard/twill-albedo-source.png`: future cloth microcolor input; **not used in the current Mustard context83 model**.
- `textures/peacock/face-paint-plate.png`: registered facial repaint source used during the bounded face refinement.

Adjacent prompt/provenance JSON files record their purpose and generation instructions. These are inputs, not final rendered proof or material-quality approval. No extra image generation is required to restore or view the included models.

## MakeHuman donor asset data

The rebuilt Green and Mustard hand geometry uses official MakeHuman asset data from:

- Upstream: https://github.com/makehumancommunity/makehuman
- Pinned public commit: `a8bc2d54ff0ac92e78ff71431b1023eda42bf482`
- Asset paths: `makehuman/data/3dobjs/base.obj`, `makehuman/data/rigs/default.mhskel`, `makehuman/data/rigs/default_weights.mhw`
- Asset license: [CC0 1.0 Universal](licenses/MakeHuman-ASSETS-CC0.md)
- Official scope statement: https://github.com/makehumancommunity/makehuman/blob/a8bc2d54ff0ac92e78ff71431b1023eda42bf482/LICENSE.md

Only asset data was used with project-side processing; the upstream executable application code is not included here. MakeHuman distinguishes its CC0 assets from its AGPL application code. The CC0 notice applies to that identified donor contribution, not to original character geometry, source artwork, other textures, or this entire repository.

The current whole-character Plum snapshot has no integrated donor replacement anatomy; separate anatomy experiments are intentionally absent. Peacock, Scarlett and White current snapshots have no newly incorporated MakeHuman donor geometry.
