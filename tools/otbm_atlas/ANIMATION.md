# OTBM Atlas runtime animation

The atlas animates cyclic Tibia appearances at runtime. It does **not** build one GIF, animated WebP, or video per map object.

## Source of truth

Animation data comes only from the pinned canonical inputs already used by the atlas:

- OTBM placement and stack order from `vendor/map-analysis/crystalserver/data-global/world/world.otbm`;
- object appearances from the pinned Tibia `appearances-*.dat`;
- sprite pixels from the pinned Tibia sprite sheets;
- item pattern selection from the same stack-count, hangable, fluid and coordinate rules used by `tools/otbm_atlas/render.py`.

Server-driven appearance/state changes are not inferred. If a visual change is not represented as a cyclic appearance animation in the pinned client metadata, the atlas keeps the canonical static state.

## Runtime pipeline

For every visible OTBM item whose first object frame group has more than one animation phase:

1. resolve the canonical item pattern for its position/subtype/hook context;
2. validate every phase and layer against the pinned sprite catalog;
3. resolve the sprite-sheet geometry (`32x32`, `32x64`, `64x32`, or `64x64`);
4. apply the same `shift` and `height` displacement used by the canonical static renderer;
5. preserve stack order by composing a per-instance `underlay` and optional `overdraw` around the animated entry;
6. deduplicate the actual phase images by appearance/pattern into `data/environment-animations/frames/<animationKey>/`;
7. emit a small chunk-local JSON record that references those shared phases and contains timing/geometry metadata;
8. let `viewer-runtime.js` select the phase from elapsed time and draw `underlay -> current phase -> overdraw` on the runtime animation canvas.

This means ten thousand identical torches can reuse one set of torch phase PNGs. They do not need ten thousand GIFs and they do not need ten thousand copies of every phase.

## Schema v2 record

Generated records under `data/environment-animations/chunks/z<z>/<chunk>.json` include:

- `position` and `serverId`;
- `animationKey` and shared `frames`;
- `underlay` and optional `overdraw`;
- `spriteSize` (`[width,height]`);
- `drawOffsetPixels` relative to the OTBM tile top-left;
- `stackIndex` and `stackSize`;
- phase duration ranges and deterministic runtime durations;
- synchronization, loop and default-start metadata copied from the appearance animation.

The browser remains backward-compatible with schema-v1 32x32 records by defaulting missing geometry to `32x32` with offset `0,0`.

## What can animate

The generalized compositor covers cyclic map objects such as torches, lamps, flames, water, fountains and other animated decorations when their pinned appearance metadata and local composition satisfy the safety contract. It also supports animated ground entries and safe non-topmost stack entries.

A candidate is deliberately left static when any of the following is true:

- one or more selected phase/layer sprites cannot be decoded;
- phase geometry is inconsistent;
- the object is too close to a chunk edge to reconstruct all possible contributors from that bounded spool shard;
- two independently animated visual rectangles overlap;
- the composed replacement patch is not fully opaque and could therefore reveal the static default phase underneath;
- the change is a server-driven/stateful variant rather than a cyclic client appearance animation.

These are correctness fallbacks, not missing-data guesses. Static canonical pixels are always preferable to a visually plausible but incorrect animation.

## Performance contract

Animations activate only at close zoom (`ANIMATION_ZOOM = 1.5`). Phase images and animation shards use bounded LRUs in the browser. Exported phase sprites are deduplicated; underlay/overdraw images are per-instance because their contents depend on the local map stack.

The exporter operates per 128x128 OTBM spool chunk and does not load the complete world into browser memory.

Dense overlap detection must remain spatially bounded. PR #387 replaced the initial all-pairs candidate comparison with 32-pixel spatial buckets; the regression test covers a dense 128x128 grid (16,384 candidate rectangles) and requires zero `_intersects` calls for aligned non-overlapping tiles while still detecting genuine overlap.

## Validation

Focused unit/runtime checks:

```sh
python -m unittest discover -s tools/otbm_atlas/tests -p 'test_*.py' -v
```

The dedicated workflow `.github/workflows/otbm-environment-animation-tests.yml` additionally proves:

- production `build_atlas()` exports a real canonical world animation;
- schema-v2 geometry/stack metadata is present;
- a real extended (`64x*`, `*x64`, shifted or height-displaced) cyclic object from the pinned Tibia assets can be exported through the production compositor;
- a real Chromium viewer advances the exported extended phases at runtime.

PR #387 (`feat(atlas): generalize runtime item animations`) is merged on `main` as `da553b1f2f157526e69e26d051ca3297db7abcf6`. The archived task records atlas unit/runtime, canonical Thais scan/render, real-browser Thais, canonical animation export, and extended Chromium E2E as passing on implementation head `ef099cfccdb107e1e264c8cfab6b049aef60adbd`; the later documentation-only head `e852748a0a4be8e6df9048f125c7c890bdc457fe` passed Required, CI, and autofix. The pinned-asset extended E2E selected `serverId 114`, `spriteSize [32,64]`, `drawOffsetPixels [-8,-40]` and observed six distinct runtime frames. Subsequent PR synchronization and merge preserved the implementation tree, but inherited results must not be described as exact-head evidence unless the corresponding workflow actually ran on that SHA.

A post-merge repository-wide yamllint report is not evidence of an animation regression: its reported errors are in pre-existing workflow/template files outside PR #387. In particular, `.github/workflows/otbm-atlas-tests.yml` and `.github/workflows/prs-003e-b-recovery-evidence.yml` retained identical blob SHAs across the merge. Treat cleanup of that repository-wide lint debt as a separate task.

## Visual showcase handoff

The runtime implementation is complete, but a human-viewable showcase artifact has **not** yet been produced. The final animation E2E run did not upload screenshots, frame sequences, video, GIF, or another GitHub Actions artifact. Do not claim that such a showcase already exists.

The next visual-proof task should extend the existing production/E2E path rather than invent a parallel renderer:

1. build from current `main` using the pinned canonical OTBM and Tibia assets;
2. automatically select factual exported animation records, preferably covering at least one fire/light-like cyclic object, one water/fountain-like cyclic object when available, and one extended/shifted object;
3. record each selected object's `serverId`, coordinates, `animationKey`, `spriteSize`, `drawOffsetPixels`, and phase timings;
4. open the generated atlas in real Chromium at `zoom >= ANIMATION_ZOOM`;
5. capture a human-viewable screenshot plus a bounded sequence/video showing actual phase advancement in map context;
6. upload those outputs as a GitHub Actions artifact so the owner can inspect the real renderer result;
7. never substitute an AI-generated mock-up or hand-built GIF as evidence of atlas rendering.

The showcase is evidence/UX tooling only. It must not change canonical map geometry, appearance interpretation, timing rules, static fallbacks, or the no-prebuilt-GIF runtime architecture.

## Extension rule

Future animation work should extend this pipeline rather than add prebuilt GIFs. Creature/NPC movement can reuse the same runtime timing/cache concepts, but creature frame-group/direction semantics remain a separate appearance category and must not be guessed from object appearances.
