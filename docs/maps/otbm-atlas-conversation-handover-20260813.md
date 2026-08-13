# Full OTBM atlas — durable conversation handover (2026-08-13)

This document preserves the owner decisions, verified repository state, reference artifacts, UX direction, and continuation requirements established during the 2026-08-13 atlas work. It exists so future agents can resume from Git/repository state instead of reconstructing the previous chat.

## Canonical repository state

Repository: `blakinio/Otheryn`.

Merged source-data PRs:

- PR #371 recorded the canonical CrystalServer map source.
- PR #372 vendored the actual map-analysis source data and exact Tibia client assets.
- PR #373 merged the repository-owned deterministic OTBM atlas pipeline.

PR #373 merged as `ef1d848c1854fdececa34a5fc084a32bf86e32d7` from head `22f7814e33f1bf698c95cf6e729c17970abf0080`.

## Canonical world and assets

Canonical CrystalServer revision:

`zimbadev/crystalserver@5e89bf8329ea406cb4ea8f4a18f32954f13e5418`

Canonical world tree:

`vendor/map-analysis/crystalserver/data-global/world/`

Primary world:

`vendor/map-analysis/crystalserver/data-global/world/world.otbm`

Canonical Tibia assets:

`vendor/map-analysis/tibia-client/15.25.bd5a04/assets/`

The asset subset contains exactly 6031 owner-selected canonical files and is pinned/provenanced in `vendor/map-analysis/README.md`.

The canonical `world.otbm` SHA-256 recorded by the atlas task is:

`3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`

## Verified parser/render facts

The current active atlas task record is:

`docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md`

Verified facts already recorded there include:

- canonical OTBM is gzip-wrapped and structurally balanced;
- 25,170,978 framed nodes were observed;
- semantic strict scan covers 18,997,668 tiles across populated `Z=0..15` with zero diagnostics;
- pinned assets decode to 42,107 object appearances and 4,927 sprite sheets;
- 75,623 referenced sprite IDs have zero missing catalog sprites;
- Thais canonical render is 5152x4832 and has zero missing appearances/sprites;
- one full canonical spool produced 3,494 bounded 128x128 map chunks;
- the spool covers all populated `Z=0..15`;
- spawn indexing found 87,565 monster records and 1,068 NPC records from 8 canonical XML sources;
- factual mechanics indexing found 2,311 AID records, 597 UID records, 2,406 teleports, 109,744 house tiles, 4,527 house doors, 33 towns, and 18 waypoints;
- static script resolution currently yields RESOLVED / AMBIGUOUS / UNRESOLVED / UNKNOWN states rather than guessing.

## Mandatory Thais regression region

The durable visual/parser regression region is:

- `X=32280..32440`
- `Y=32155..32305`
- `Z=7`

Historical independently verified reference characteristics:

- 161 x 151 map positions;
- 24,311 tiles;
- 24,292 ground items;
- historical renderer counted 15,037 child items;
- 39,329 render operations;
- 872 unique appearance IDs;
- 1,000 unique sprite IDs;
- zero missing appearances;
- zero missing sprites;
- zero unknown tile attributes.

The newer semantic parser currently reports 14,993 decoded child items. This 44-item discrepancy must not be force-corrected. It must be explained using authoritative OTBM/item/appearance semantics, or documented as a difference in counting definition.

## Product goal

The product is not a single giant render. The complete canonical OTBM must be preprocessed/indexed once, while the browser loads only the current viewport plus a small prefetch margin.

The viewer must support the complete world without loading the entire OTBM, a world-sized canvas, one giant PNG, or one giant overlay payload into the browser.

Map imagery, mechanics, spawns, NPCs, houses, and other high-volume data should remain spatially chunked and floor-addressable.

## Default browsing UX

The desired normal browsing experience is similar to:

- `https://tibiamaps.io/map#32823,31962,7:0`
- `https://tibiaroute.com/pl/bestiary-tracker`

These are UX references only and are not authoritative Otheryn map sources.

The default view should be a lightweight slippy-map style overview/minimap that is fast to pan/zoom over large distances.

At maximum/detail zoom the viewer should reveal the exact canonical sprite render generated from the pinned OTBM plus pinned Tibia assets.

## Viewer implementation reference

`https://github.com/tibiamaps/tibia-map` should be evaluated as a viewer/slippy-map implementation reference or possible viewer-core source before unnecessarily rebuilding generic map navigation behavior.

Its map data must never replace the Otheryn canonical OTBM.

If code is reused, verify and comply with its license and attribution requirements.

## Oteryn UI visual reference

The owner prefers the earlier Oteryn Thais interactive prototype as the primary visual/interaction reference for the production viewer.

Reference artifact name:

`oteryn-thais-interactive-demo(1).zip`

The exact owner-provided ZIP used in this conversation has SHA-256:

`def2d4348a31f06362eec707a07c29a55235a1b55cb51470b0919ea6d7b6ffa5`

Its contents are:

- `README.md`
- `provenance.json`
- `thais-z7-minimap.png`
- `npcs.json`
- `app.css`
- `index.html`
- `standalone.html`
- `app.js`

The production viewer should feel like a scalable evolution of that prototype, not an unrelated frontend.

Preserve/adapt where practical:

- dark Oteryn Maps visual language;
- map-dominant central canvas/surface;
- top search/navigation;
- compact layer controls;
- coordinate display/copy;
- X/Y/Z navigation;
- floor switching;
- zoom controls and mouse-wheel zoom;
- pan/drag navigation;
- clickable markers;
- marker tooltips;
- details/info side panel;
- URL state for coordinates/zoom/view state.

Before changing the viewer UI, future implementation work should explicitly classify prototype components as PRESERVED, ADAPTED, or REPLACED.

## Multi-resolution map behavior

The agreed model is:

- low zoom: lightweight overview/minimap tiles;
- medium zoom: progressively more detailed overview tiles as useful;
- maximum/detail zoom: exact canonical 32 px-per-map-tile sprite render.

Exact zoom thresholds are implementation parameters and should be selected from measured behavior rather than copied blindly from this document.

Overview tiles remain derived from canonical Otheryn world data; they are not a substitute source of truth.

## User-selectable render modes

Add a first-class user control:

`Render mode: Auto | Detailed | Performance`

### Auto

Default mode.

- low/medium zoom uses lightweight overview/minimap tiles;
- high/detail zoom switches to canonical sprite-render tiles.

### Detailed / Always Detailed

Use canonical sprite-render imagery at every supported zoom level.

This must still use viewport/chunk/lazy-loading architecture. It must never load the whole detailed world into browser memory.

The owner reports that continuous detailed rendering currently appears smooth on his desktop. Treat this as owner feedback, not a benchmark. Do not artificially disable or heavily restrict Detailed mode; it is a first-class supported option with bounded cache/resource usage.

### Performance

Always use lightweight overview/minimap imagery and never automatically request detailed sprite tiles.

This is intended for lower-end hardware, mobile, large navigation jumps, and bandwidth-sensitive use.

## Render-mode persistence and state

Render mode must:

- persist in `localStorage`;
- be representable in URL state;
- use explicit URL state as precedence over stored preference;
- switch without a full-page reload;
- preserve current X/Y/Z;
- preserve zoom;
- preserve enabled layers;
- preserve selected marker where practical;
- preserve search/navigation context where practical.

Changing the base-map render mode must not alter factual overlay data.

## Browser cache/resource model

Detailed mode must have bounded cache behavior.

Use a sane LRU or equivalent policy:

- viewport-required chunks remain loaded;
- nearby/recent chunks may remain cached;
- distant chunks are evicted;
- previously visited floors must not accumulate forever;
- cache limits must be documented;
- measurements must be factual, not invented.

An optional diagnostics panel may expose current render mode, X/Y/Z, zoom, visible/loaded chunk counts, approximate cache size when reliably measurable, active base layer, enabled overlay count, and recent chunk load timing.

Do not show fake FPS or fabricated metrics.

## Toggleable factual layers

The owner explicitly wants layers that can be enabled/disabled independently.

At minimum support factual layers for:

- NPCs;
- monsters;
- bosses only where authoritative classification exists;
- ActionIDs;
- UniqueIDs;
- teleports;
- houses;
- house doors;
- towns;
- temples;
- waypoints;
- resolved quest/mechanics/script links;
- other useful verified OTBM metadata.

Do not classify a creature as a boss based on name heuristics.

Layer state should persist in localStorage and be shareable in URL state.

For large datasets, overlays must be viewport/chunk loaded rather than world-loaded. At low zoom use clustering or visibility thresholds where appropriate to avoid thousands of markers at once.

## Search behavior

Search should grow from the old prototype and support verified indexes such as:

- NPC names;
- monster names;
- towns;
- coordinates;
- AID;
- UID;
- waypoints;
- mechanics/script resolution;
- house identifiers where useful.

Selecting a result should switch to the correct floor, pan to X/Y, choose an appropriate zoom, optionally enable the relevant layer, highlight/select the result, and open details.

## Details panel

Clicking a factual marker/object should open a details panel populated only with fields supported by actual data.

Examples include:

- NPC: name, X/Y/Z, source, spawn metadata;
- monster: name, X/Y/Z, spawn time, radius/group metadata, source, authoritative classification;
- teleport: source/destination X/Y/Z, item ID, AID/UID if present, source;
- AID/UID: ID, position, item ID, source OTBM, resolution status/script;
- house: house/door ID and position;
- mechanic: registration type, identifier, script, and RESOLVED/AMBIGUOUS/UNRESOLVED/UNKNOWN state.

Missing values must not be guessed.

## Floor and coordinate UX

Support all populated `Z=0..15`.

Floor changes should preserve X/Y, zoom, render mode, and enabled layers where possible, while loading only the new floor viewport.

Coordinates are first-class UI:

- continuously visible X/Y/Z;
- jump to coordinate;
- copy coordinate;
- share coordinate URL;
- map-click coordinate;
- marker coordinate.

## Spawn semantics

For canonical XML sources with relative X/Y:

`absolute X = center X + relative X`

`absolute Y = center Y + relative Y`

Use actual source semantics for Z. The current verified canonical files use child Z as absolute and agree with group center Z for all indexed records.

Every spawn record should retain source provenance and origin/composition classification.

## Map composition

Do not blindly flatten every OTBM into the base world.

Keep factual origin classes such as:

- base world;
- runtime overlay;
- quest map;
- event map;
- optional map;
- standalone map;
- UNKNOWN.

Only present content as normal/effective world data where runtime/source evidence establishes that relationship.

## Mechanics resolution

Mechanics/script resolution must retain explicit states:

- RESOLVED
- AMBIGUOUS
- UNRESOLVED
- UNKNOWN

Never arbitrarily choose one script when multiple registrations match. Dynamic registrations that cannot be statically proven remain UNKNOWN.

Regression examples already independently resolved in prior work:

- AID `5555` -> `scripts/movements/teleport/sorcerer_guild_thais.lua`
- UID `65207` -> literal dispatch table in `quest_system2.lua`

These are regression checks, not hard-coded assumptions.

## Validation expectations

Before future atlas work is called complete, require real validation of:

- parser tests;
- asset decoder tests;
- renderer tests;
- chunk/cache tests;
- coordinate conversion tests;
- teleport extraction;
- spawn coordinate semantics;
- render-mode state/persistence;
- layer enable/disable and URL restoration;
- viewport marker loading;
- Thais real-data E2E;
- full-world generation across all populated floors;
- no silently failed chunks;
- overview/detailed spatial alignment;
- overlay/map coordinate alignment;
- canonical source fingerprints;
- exact-head CI;
- independent audit/E2E per repository governance.

## Render-mode tests explicitly requested

Add tests for:

- Auto parsing;
- Detailed parsing;
- Performance parsing;
- invalid render-mode fallback;
- URL precedence over localStorage;
- persistence;
- Auto -> Detailed -> Performance switching without coordinate/overlay loss;
- Detailed selects detailed tiles at low zoom;
- Performance never selects detailed sprite tiles;
- Auto preserves zoom-dependent behavior;
- cache remains bounded.

## Current continuation point

At the time this handover was recorded, `main` is `ef1d848c1854fdececa34a5fc084a32bf86e32d7`, PR #373 is merged, and the active task checkpoint still records the next technical action as:

`run the complete four-worker atlas build, collect time/size/missing-resource totals, then perform static-viewer E2E and exact-head CI`

Future agents must inspect live Git/PR/task/CI state before relying on that next action because it may have advanced after this document was committed.

## Source-of-truth hierarchy for continuation

Use this order:

1. current repository governance and live `main`;
2. active atlas task/checkpoint;
3. canonical vendored world/assets and their provenance;
4. this durable product/UX handover;
5. the vendored Oteryn Thais prototype reference artifact;
6. external TibiaMaps/TibiaRoute references only for UX/implementation ideas.

Never require the previous chat transcript to resume this work.
