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

## Extension rule

Future animation work should extend this pipeline rather than add prebuilt GIFs. Creature/NPC movement can reuse the same runtime timing/cache concepts, but creature frame-group/direction semantics remain a separate appearance category and must not be guessed from object appearances.
