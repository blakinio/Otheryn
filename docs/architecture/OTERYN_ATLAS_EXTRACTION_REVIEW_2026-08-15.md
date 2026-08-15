# Verdict

EXTRACTABLE_WITH_REFACTOR

**FACT.** At audited `main` `5e87f6cb50681b3f9b00d3eb4fbdaf2c0509f461`, most Atlas implementation is physically concentrated in `tools/otbm_atlas/`, with factual-content analysis in `tools/otbm_atlas_facts/` and dedicated Atlas workflows in `.github/workflows/`. However, the current namespace mixes three future responsibilities: legacy OTBM import/decoding, canonical-content interpretation, and browser/publication runtime.

**INFERENCE.** History-preserving extraction is practical for the browser/runtime and derived-publication portions, but a wholesale `git filter-repo --path tools/otbm_atlas` into `Oteryn-Atlas` would place OTBM importer and CrystalServer-content semantics in the wrong future repository. A selective extraction can preserve useful history only after ownership is separated or by extracting a historical seed and immediately deleting/replacing Game-owned components in the destination. The latter is less clean and is not recommended.

**RECOMMENDATION.** Treat this repository only as LEGACY / MIGRATION SOURCE / HISTORICAL REFERENCE. Split by responsibility before any repository extraction. `Oteryn-Game` must become the sole owner of OTBM ingestion, legacy IR, server/content interpretation and canonical World Model production. `Oteryn-Atlas` must consume only a versioned immutable Atlas export and own browser presentation, derived indexing/cache/publication and Atlas-specific rendering/runtime concerns.

# Atlas Inventory

Audit basis: `tools/otbm_atlas/README.md`, implementation under `tools/otbm_atlas/`, `tools/otbm_atlas_facts/`, Atlas tests, `.github/workflows/otbm-atlas-*`, current product-readiness documentation, generated-artifact rules, and path-scoped Git history.

| Path / module | CURRENT RESPONSIBILITY | DEPENDENCIES | CANARY/CRYSTAL COUPLING | OTBM COUPLING | WEB/UI COUPLING | TARGET OWNER | HISTORY PRESERVATION IMPORTANCE | MIGRATION RISK |
|---|---|---|---|---|---|---|---|---|
| `tools/otbm_atlas/nodefile.py` | bounded-memory escaped node-stream framing, gzip/raw input | Python stdlib; Remere framing semantics | low | **very high** | none | **Oteryn-Game** | high: parser evolution/provenance | P0 if duplicated in Atlas |
| `tools/otbm_atlas/semantic.py` | OTBM node/attribute decoding into `MapHeader`, `Tile`, `Item`, `Town`, `Waypoint` | `nodefile.py`; OTBM enums/layout | medium through historical format assumptions | **very high** | none | **Oteryn-Game / Rewrite** | very high | P0 |
| `tools/otbm_atlas/scan.py` | diagnostic bounded OTBM scanner and factual counters | semantic parser | medium | high | none | Legacy only; selected tests/ideas to Game | medium | P2 |
| `tools/otbm_atlas/atlas.py` | current end-to-end orchestrator: validates pinned Crystal roots, spools OTBM, chunks, renders, extracts facts, builds overlays/search/viewer | nearly all Atlas Python modules; `tools.otbm_atlas_facts`; vendored Crystal/Tibia corpus | **very high**: hard-coded `vendor/map-analysis/crystalserver/...` roots | **very high** | high through viewer/output generation | **Rewrite** into Game exporter + Atlas publisher/build tooling | very high | **P0** |
| `atlas.py` spool encoding/`spool_map` | temporary binary tile chunks and direct map facts | current `Tile` IR | medium | high | none | **Oteryn-Game / Rewrite** as internal legacy-import/compiler cache, not public Atlas contract | high concept, low exact format | P1 |
| `tools/otbm_atlas/render.py` | deterministic map tile rasterization from item appearances | `assets.py`, semantic `Tile`/`Item`, Pillow/assets | low Crystal; high Tibia-asset lineage | medium because input is legacy `Tile` | output is Atlas imagery | **Rewrite**, likely split: canonical render inputs from Game, raster publication in Atlas/tooling | high | P1 |
| `tools/otbm_atlas/assets.py` | decodes pinned appearance/sprite assets and supplies raster renderer metadata | protobuf/LZMA/image sheet semantics; pinned client assets | not server-coupled; tightly historical-client-coupled | low | high for imagery | **Oteryn-Atlas** only if Atlas remains responsible for image derivation; otherwise shared build tooling | high | P1 |
| `tools/otbm_atlas/overview.py` | deterministic lower-resolution overview generation | generated detail imagery/Pillow | none | none | high | **Oteryn-Atlas** | medium | P2 |
| `tools/otbm_atlas/spatial.py` | partitions overlay records by world chunk and builds compact search navigation data | generated factual records | indirect | none | **high** | **Oteryn-Atlas** | high | P1 |
| `tools/otbm_atlas/viewer.py` | emits static viewer shell/assets | viewer JS/CSS/generated Atlas paths | none | none | **very high** | **Oteryn-Atlas** | high | P1 |
| `tools/otbm_atlas/viewer_app.js` | map canvas, pan/zoom/floors, marker rendering, details, search, overlays, deep-link state | `manifest.json`, `data/chunks/**`, `data/search-index.json`, viewer runtime | none except names/schema produced from legacy content | none | **very high** | **Oteryn-Atlas** | **very high** | P1 |
| `tools/otbm_atlas/viewer_runtime.js` | URL state, render modes, visible chunk selection, bounded LRUs, environment-animation runtime | browser APIs and exported schemas | none | none | **very high** | **Oteryn-Atlas** | **very high** | P1 |
| `tools/otbm_atlas/viewer-runtime.js` | tiny compatibility/runtime entry | viewer runtime | none | none | high | Oteryn-Atlas; consolidate/drop alias after migration | low | P3 |
| `tools/otbm_atlas/creature_animation_runtime.js` | browser animation behavior for creature sprites | generated sprite animation records | indirect via historical appearance definitions | none | **very high** | **Oteryn-Atlas** | high | P2 |
| `tools/otbm_atlas/environment_animation.py` | derives safe environment-animation frames/patches from map instances and appearance assets | current semantic tiles, renderer/assets, spool | low Crystal; historical asset-coupled | medium/high through legacy tile instances | high | **Rewrite** around canonical World export, then Atlas publication | high | P1 |
| `tools/otbm_atlas/environment_spool.py` | environment animation spool helper | current Atlas spool/records | low | medium | low | Rewrite / temporary Legacy | low | P2 |
| `tools/otbm_atlas/creature_sprites.py` | shared NPC/monster appearance lookup and sprite generation | pinned Crystal definitions + Tibia appearances | **high** for definition lookup | none | high | **Split/Rewrite**: canonical creature identity/outfit facts in Game export; derived PNG/frame publication in Atlas | high | P1 |
| `tools/otbm_atlas/npc_sprites.py` | enriches NPC spawn records with deduplicated sprite paths/status | Crystal NPC definitions + creature renderer | **high** | none | high | Rewrite: identity/appearance resolution Game, publication Atlas | medium | P1 |
| `tools/otbm_atlas/monster_sprites.py` | same for monsters | Crystal monster definitions + creature renderer | **high** | none | high | Rewrite: identity/appearance resolution Game, publication Atlas | medium | P1 |
| `tools/otbm_atlas/spawns.py` | parses Canary/Crystal `*-monster.xml` / `*-npc.xml`, including relative X/Y and absolute Z semantics and origin classes | Crystal world XML layout | **very high** | low; map-associated legacy content | low | **Oteryn-Game / Rewrite** | very high | **P0** |
| `tools/otbm_atlas/houses.py` | parses legacy house metadata | legacy world XML/content | high | associated with OTBM world | low | **Oteryn-Game** | medium | P1 |
| `tools/otbm_atlas/mechanics.py` and `tools/otbm_atlas_facts/mechanics.py` | map AID/UID resolution against scripts/registrations | Crystal Lua/server content | **very high** | medium: consumes AID/UID facts emitted from OTBM | low | **Oteryn-Game / Rewrite** | very high | **P0** |
| `tools/otbm_atlas_facts/lua_static.py` | static analysis of legacy Lua mechanics | Crystal Lua tree/registration idioms | **very high** | none | none | **Oteryn-Game / Legacy importer tooling** | high | P1 |
| `tools/otbm_atlas_facts/npc_services.py`, `npclib_semantics.py` | derives NPC service semantics from legacy definitions/scripts | Crystal NPC/Lua conventions | **very high** | none | low | **Oteryn-Game / Rewrite** | high | P1 |
| `tools/otbm_atlas_facts/monster_metadata.py` | resolves monster metadata including explicit boss evidence | Crystal monster definitions | **very high** | none | low | **Oteryn-Game / Rewrite** | high | P1 |
| `tools/otbm_atlas_facts/raids.py` | derives factual raid/event positions/areas and evidence | Crystal raid/event/server content | **very high** | none | low | **Oteryn-Game / Rewrite** | high | P1 |
| `tools/otbm_atlas_facts/build.py` | orchestrates legacy factual extraction | all `otbm_atlas_facts` modules | **very high** | indirect | none | **Oteryn-Game / Rewrite** | high | P1 |
| `tools/otbm_atlas/factual_layers.py` | converts Crystal-derived reports into browser shard/search records | `tools.otbm_atlas_facts`, Atlas output tree | **high** at input side | medium | **high** at output side | **Split/Rewrite**: factual truth in Game export; Atlas-specific spatial/search projection in Atlas | very high | **P0** boundary hotspot |
| `tools/otbm_atlas/composition.py` | classifies base/supplemental OTBM sources and runtime-loading evidence | Crystal world tree/repository evidence | **high** | high | none | **Oteryn-Game / Legacy only** | high historical value | P1 |
| `tools/otbm_atlas/verify.py` | checks Atlas manifest, PNG dimensions/checksums and generated-release integrity | Atlas output schema/images | low | none | high publication coupling | **Oteryn-Atlas**, rewritten against new export contract | high | P1 |
| `tools/otbm_atlas/codec_benchmark.py` | storage/decode benchmark of generated detail chunks | generated Atlas images, Pillow | none | none | publication/storage | Oteryn-Atlas research/tooling or Legacy | medium | P3 |
| `tools/otbm_atlas/tests/**` | parser, renderer, chunking, viewer runtime, factual, creature/environment regressions | modules above; some pinned integration corpus | mixed | mixed | mixed | **Split by production owner**; preserve fixtures and behavior assertions | **very high** | P0 if copied wholesale |
| `tools/otbm_atlas_facts/tests/**` | legacy Crystal semantics tests | Crystal conventions/fixtures | **very high** | low | none | **Oteryn-Game** | very high | P1 |
| `.github/workflows/otbm-atlas-full-world-release.yml` | builds/verifies Z0..Z15 against pinned Crystal/Tibia vendor roots and asserts 3494 chunks/current hashes | current monorepo, Atlas Python modules, vendored corpus | **very high** | high | medium | **Rewrite** into separate Game export certification + Atlas consumer/publication validation | high evidence value | P1 |
| `.github/workflows/otbm-atlas-facts-tests.yml`, `otbm-atlas-factual-layers-*.yml` and other `otbm-atlas-*` workflows | dedicated tests/audits for legacy factual extraction and Atlas output | current repo paths | high/mixed | mixed | mixed | **Split/Rewrite** by owner; do not copy monorepo workflow assumptions | medium/high | P1 |
| `vendor/map-analysis/crystalserver/**` | pinned migration/reference corpus: world, NPC/monster/scripts and source manifest | historical CrystalServer | **absolute** | source includes OTBM and legacy content | none | **Legacy source/reference; bounded importer fixtures in Game only** | **very high provenance** | P0 if moved to public Atlas |
| `vendor/map-analysis/tibia-client/**` | pinned historical client appearance/sprite corpus | Tibia client assets | none server-side | none | image-generation input | **Legacy/reference**; redistribution decision separate | high provenance | P0 legal/size |
| `build/full-map-atlas/**` and other `build/**` | generated release/cache/spool/tiles/data; ignored by `.gitignore` | pipeline outputs | derived | derived | high | **Do not history-extract**; regenerate from immutable Game export | none as Git history; release evidence separately | P1 |
| `docs/maps/otbm-atlas-*`, `docs/research/otbm-atlas-*` | architecture, completion, product and benchmark evidence | repository history | historical context | some | some | **Legacy docs**, selectively copy architectural decisions to destination docs rather than treating as runtime source | high | P2 |

# Target Ownership Matrix

| path/module | Oteryn-Atlas | Oteryn-Game | Legacy | Rewrite | Drop |
|---|---:|---:|---:|---:|---:|
| `tools/otbm_atlas/nodefile.py` |  | **X** |  | optional port |  |
| `tools/otbm_atlas/semantic.py` |  | **X** |  | **X** into bounded legacy importer/IR |  |
| `tools/otbm_atlas/atlas.py` | partial concepts | partial concepts |  | **X** | current monolithic orchestrator after replacement |
| `tools/otbm_atlas/render.py` | **X** for publication renderer if retained | canonical render inputs only |  | **X** boundary |  |
| `assets.py`, `overview.py` | **X** |  | possible provenance-only | partial |  |
| `viewer.py`, `viewer_app.js`, `viewer_runtime.js`, `creature_animation_runtime.js` | **X** |  |  | evolve | compatibility alias after consolidation |
| `spatial.py`, Atlas side of `factual_layers.py` | **X** |  |  | **X** to consume export |  |
| `spawns.py`, `houses.py` |  | **X** |  | **X** into legacy import/content compiler |  |
| `tools/otbm_atlas_facts/**` |  | **X** | historical source-analysis tooling | **X** into canonical content conversion |  |
| Game-side truth portion of `factual_layers.py` |  | **X** |  | **X** |  |
| `composition.py` |  | **X** | **X** | bounded rewrite if supplemental maps still matter |  |
| `verify.py` | **X** | Game needs independent export validator |  | **X** schema contract |  |
| `codec_benchmark.py` | optional **X** |  | **X** |  | optional after decision |
| `tools/otbm_atlas/tests/**` | split **X** | split **X** | fixtures/evidence | **X** paths/contracts | obsolete monolithic assumptions |
| `tools/otbm_atlas_facts/tests/**` |  | **X** |  | partial |  |
| `.github/workflows/otbm-atlas-*` | split **X** | split **X** |  | **X** | monorepo-only workflow copies |
| `vendor/map-analysis/crystalserver/**` |  | bounded fixtures/reference only | **X** |  | never Atlas runtime input |
| `vendor/map-analysis/tibia-client/**` | publication input only if legally/architecturally retained |  | **X** |  | never blindly publish/move |
| generated `build/**` | regenerate/publish | produces source export, not Atlas build tree | local historical evidence only |  | **X** from history extraction |

# Canary/Crystal Coupling

**FACT.** Current coupling is structural, not incidental. `tools/otbm_atlas/README.md` defines canonical roots under `vendor/map-analysis/crystalserver/data-global/{world,npc,monster}` and the Atlas builder rejects alternative roots. `atlas.py` hard-codes those canonical paths. `spawns.py` explicitly parses Canary/Crystal spawn XML semantics. `tools/otbm_atlas_facts/**` analyzes Crystal Lua, NPC, monster and raid conventions. `factual_layers.py` invokes that analysis and even gates enrichment on the pinned world SHA and Crystal supplemental-source manifest.

**FACT.** This means current generated `data/spawns.json`, mechanics resolutions, NPC services, raids/events and boss classifications are not generic Atlas truths; they are outputs of a legacy Crystal content adapter.

**RECOMMENDATION.** None of the Crystal/Canary source-tree traversal or Lua/XML semantic resolution may become a required dependency of `Oteryn-Atlas`. Those adapters belong behind `Oteryn-Game`'s legacy-import/compiler boundary. Atlas receives normalized canonical facts only.

# OTBM Ownership Findings

**FACT.** OTBM framing (`nodefile.py`), semantic decoding (`semantic.py`), map scanning, `spool_map`, AID/UID extraction, towns, waypoints, house tiles/doors and raw Z handling are currently inside `tools/otbm_atlas`.

**FINDING.** In the proposed architecture this ownership is wrong. OTBM is a legacy ingest format. Browser Atlas must not know OTBM node types, attributes, escaped framing, Canary item IDs, spawn XML offsets or supplemental OTBM composition semantics.

**RECOMMENDATION.** `Oteryn-Game` should expose a bounded importer pipeline:

`OTBM bytes -> LegacyOtbmIR -> canonical Oteryn World Model -> validated/versioned World snapshot`.

The current `Position`, `Item`, `Tile`, `Town` and `Waypoint` dataclasses are useful behavioral evidence but must not automatically become the canonical World Model. They are legacy-format-shaped and should be treated as candidate Legacy IR only.

The current disk spool is an implementation optimization, not a domain contract. Preserve the bounded-memory/chunked principle and test history; do not freeze `SPOOL_VERSION=1` as an inter-repository interface.

# Viewer Ownership Findings

**FACT.** The viewer already has a clean browser-side core: viewport chunk selection, raw floor state, pan/zoom, render modes, bounded image and overlay LRUs, spatial shard fetches, search navigation, details, overlay toggles, URL/deep-link serialization, selected marker state, and creature/environment presentation.

**FINDING.** These are strong `Oteryn-Atlas` candidates because they operate on generated files rather than server runtime state. `viewer_app.js` consumes `manifest.json`, `data/search-index.json` and viewport-bounded `data/chunks/z*/x_y.json`. It does not parse OTBM.

**RECOMMENDATION.** Preserve behavior/history for viewer modules, but change their data source from schemas generated directly from Crystal/OTBM to a documented immutable Atlas export version. The UI may retain raw world Z values if that is also the canonical World Model convention; otherwise floor semantics must be carried explicitly in the export rather than inferred.

# Generated Data / Artifact Findings

**FACT.** The current builder emits, among other things, detailed chunk images, 4x/8x overview images, `manifest.json`, `data/chunks/**`, `data/search-index.json`, `data/mechanics.json`, `data/spawns.json`, factual-layer reports, creature sprite assets, environment-animation shards and verification metadata. `.gitignore` excludes `build/`, so the full generated Atlas is not a source-history extraction candidate.

**FACT.** `.github/workflows/otbm-atlas-full-world-release.yml` regenerates individual Z0..Z15 floors directly from pinned Crystal `world.otbm` and pinned Tibia assets, then asserts the legacy/current release identity including 3494 chunks and a specific map SHA. This is valuable certification evidence but is not the future architecture.

**RECOMMENDATION.** Future artifacts should have two stages:

1. **Game-owned immutable World/Atlas source export**: canonical world/content facts plus stable asset references and provenance, signed/fingerprinted/versioned.
2. **Atlas-owned derived publication**: raster/vector chunks as selected, spatial shards, search index, thumbnails/animation frames, cache metadata, manifest and browser bundle.

Derived Atlas data must be reproducible and disposable. Do not use Git history extraction to migrate `build/**`, `.spool/**`, generated PNGs or generated JSON caches. Release evidence may be retained in docs/releases/object storage as appropriate.

# Git History Extraction Feasibility

**FACT.** Path-scoped history exists for `tools/otbm_atlas`; recent commits include dedicated Atlas work such as `feat(atlas): animate canonical creature overlays (#399)` and `docs(atlas): record lossless WebP benchmark (#404)`. The implementation is therefore not history-less or entirely buried inside generic server paths.

**INFERENCE.** A history-preserving extraction is technically realistic, but the present path boundary is semantically too broad. `tools/otbm_atlas/` contains both future Atlas-owned viewer/publication code and future Game-owned OTBM/legacy-content code. `tools/otbm_atlas_facts/` is more consistently Game/legacy-content oriented. Dedicated workflows are also mixed between factual extraction and publication verification.

**Verdict on `git filter-repo`:** feasible only as a later controlled operation after an ownership refactor or with a carefully enumerated path set plus post-extraction cleanup. A single `--path tools/otbm_atlas` is explicitly rejected.

History preservation priority:

- **High:** viewer/runtime, spatial/search/publication behavior, parser/importer tests, factual-analysis provenance, release verification history.
- **Medium:** rendering/asset pipeline and research utilities.
- **Low/none:** generated caches/artifacts and transient spool formats.

# Proposed Extraction Path Set

Do not execute this now. The following is a **future candidate**, after Game-owned modules have been relocated or replaced so the paths are semantically clean.

Candidate history set for `Oteryn-Atlas`:

```text
tools/otbm_atlas/viewer.py
tools/otbm_atlas/viewer_app.js
tools/otbm_atlas/viewer_runtime.js
tools/otbm_atlas/viewer-runtime.js
tools/otbm_atlas/creature_animation_runtime.js
tools/otbm_atlas/overview.py
tools/otbm_atlas/spatial.py
tools/otbm_atlas/verify.py
tools/otbm_atlas/assets.py                  # only if image publication remains Atlas-owned
tools/otbm_atlas/render.py                  # after decoupling from legacy Tile IR
tools/otbm_atlas/environment_animation.py   # after canonical-export adaptation
tools/otbm_atlas/creature_sprites.py        # publication half only after split
tools/otbm_atlas/tests/<Atlas-owned tests>
docs/maps/<selected Atlas viewer/product/history docs>
docs/research/otbm-atlas-*/<selected publication research>
```

Candidate history set to preserve for future `Oteryn-Game` migration work, not Atlas extraction:

```text
tools/otbm_atlas/nodefile.py
tools/otbm_atlas/semantic.py
tools/otbm_atlas/scan.py
tools/otbm_atlas/spawns.py
tools/otbm_atlas/houses.py
tools/otbm_atlas/mechanics.py
tools/otbm_atlas/composition.py
tools/otbm_atlas_facts/**
tools/otbm_atlas/tests/<import/content-semantic tests>
vendor/map-analysis/crystalserver/<bounded fixtures/provenance only>
```

`atlas.py`, `factual_layers.py`, creature sprite enrichment and environment generation should not be selected wholesale until they are split because they straddle the contract.

# Files That Must NOT Move To Atlas

- `tools/otbm_atlas/nodefile.py` and OTBM structural framing implementation.
- `tools/otbm_atlas/semantic.py` and legacy OTBM semantic model as a required runtime/build dependency.
- `tools/otbm_atlas/spawns.py` Crystal spawn XML parser.
- legacy house parsing and supplemental OTBM composition logic.
- `tools/otbm_atlas_facts/**` Crystal Lua/NPC/monster/raid interpretation as Atlas dependencies.
- Game/server source trees: `src/**`, `data/**`, `data-canary/**`, `data-otservbr-global/**`, database/runtime configuration and server schemas unless a future explicit neutral schema package is designed.
- `vendor/map-analysis/crystalserver/**` as an Atlas production dependency.
- generated `build/**`, spools, temporary caches and full generated image corpus as Git source history.
- generic Canary/Crystal CI, deployment and server workflows.
- credentials, database snapshots and runtime state.

# Files That Must Move/Be Reimplemented In Game

`Oteryn-Game` must implement and own equivalents for:

1. bounded legacy OTBM framing and decoding (`nodefile.py`, `semantic.py` behavior);
2. explicit Legacy OTBM IR distinct from the canonical World Model;
3. conversion from Legacy IR to canonical Oteryn World Model;
4. validation for coordinates/floors/items/houses/towns/waypoints/teleports/AID/UID and unsupported legacy records;
5. Crystal/Canary spawn XML adapter where needed for migration input;
6. legacy NPC/monster/raid/mechanics/Lua semantic adapters currently under `tools/otbm_atlas_facts/**`;
7. supplemental/world-change source classification if it remains needed for migration;
8. canonical creature/NPC/monster identities and appearance/outfit facts, rather than Atlas guessing from legacy definitions;
9. immutable versioned Atlas-export producer from the canonical World Model;
10. compatibility fixtures and regression tests proving parity with known legacy OTBM/Crystal inputs.

These should be reimplemented around native Game concepts rather than copied as a permanent `tools.otbm_atlas` package.

# Contract Needed Between Game And Atlas

A formal versioned contract is a P0 prerequisite. Minimum proposed surface:

```text
AtlasExportManifest
  schemaVersion
  exportId / worldVersion
  createdFromWorldModelVersion
  sourceProvenance[]
  coordinateSystem
  floorSemantics
  chunkGrid { size, origin }
  assetSetVersion / appearanceCatalogVersion
  contentHashes
  capabilities[]

WorldChunk
  chunkId / x / y / z
  tile/map-position presentation inputs OR canonical render primitives
  deterministic ordering / stack information needed for rendering
  factual IDs exposed for inspection

Entity/Overlay records
  NPC spawns
  monster spawns
  POIs
  houses/towns/waypoints
  teleports/transitions
  raids/events/areas
  mechanics evidence where deliberately public
  provenance/evidence/status: RESOLVED | AMBIGUOUS | UNRESOLVED | UNKNOWN

SearchSource
  stable entity IDs
  labels/categories
  canonical position/bounds
  details reference

Asset references
  stable appearance/outfit IDs
  animation/frame metadata if public
  content-addressed assets or deterministic derivation references
```

Contract rules:

- Atlas must never inspect OTBM, Canary XML or Crystal Lua to fill missing fields.
- Game export is immutable and content-addressed/versioned; Atlas publication declares exactly which export it consumes.
- Unknown/ambiguous legacy evidence remains explicit; publication cannot promote it through naming heuristics.
- Stable entity IDs must replace viewer-generated identity strings where entities have canonical identity.
- Coordinate, floor, stack and sprite displacement semantics must be explicit and testable.
- Atlas-derived indexes/caches are disposable and rebuildable from one export version.
- Compatibility is negotiated by `schemaVersion` and capability flags, not repository layout.

# Migration Sequence

1. Freeze this audit as the migration-source decision record. Do not change repository identity.
2. In `Oteryn-Game`, define canonical World Model boundaries and a dedicated Legacy OTBM IR.
3. Port/reimplement `nodefile.py` + `semantic.py` behavior behind a bounded legacy importer; prove parity with retained fixtures/regressions.
4. Port/reimplement Crystal/Canary content adapters (`spawns`, houses, mechanics, NPC/monster/raid facts) as migration-only compiler inputs. Remove their necessity from Atlas.
5. Define and version the Game -> Atlas immutable export contract, including floor/coordinates, stable IDs, evidence status and asset references.
6. Build a Game exporter and independent schema/semantic validator. Compare export facts against the current certified legacy Atlas on representative regions and all required aggregate counters.
7. Refactor legacy `tools/otbm_atlas` conceptually or in a temporary migration branch so browser/publication code consumes a test export rather than OTBM/Crystal roots. This is the point at which ownership paths become clean.
8. Separate creature/environment rendering: Game supplies canonical identity/animation facts; Atlas publication derives browser assets where allowed.
9. Split tests: importer/content tests to Game; viewer/search/cache/deep-link/publication tests to Atlas; keep cross-repo contract fixtures in both or a neutral schema artifact.
10. Recreate CI by responsibility: Game importer/export certification; Atlas contract-consumer, publication and browser E2E. Do not copy monorepo path assumptions verbatim.
11. Only after steps 2-10, perform a dry-run history extraction in a disposable local clone and inspect commit graph, rewritten paths, licenses, large blobs and unwanted server/vendor content.
12. If dry-run is clean, perform the separately authorized destination extraction/create-repo operation. That operation is explicitly outside this task.
13. Regenerate Atlas publication from an immutable Game export; do not migrate `build/**` as source.
14. Keep `blakinio/Otheryn` readable as legacy provenance until migration acceptance and retention policy are separately approved.

# Risks

## P0

- **Boundary inversion:** copying `tools/otbm_atlas/**` wholesale would make `Oteryn-Atlas` own OTBM/Crystal ingestion, contradicting the target architecture.
- **Dual truth models:** retaining OTBM-shaped `Tile`/`Item` structures as Atlas truth in parallel with a future canonical World Model would create drift and reconciliation bugs.
- **Server-content leakage:** `tools/otbm_atlas_facts/**` and `factual_layers.py` currently infer/resolve facts from Crystal scripts/content; Atlas must not become a hidden second game compiler.
- **Contract ambiguity:** without explicit floor/stack/coordinate/evidence/asset semantics, the new Game export can silently change what the browser displays.
- **Redistribution/provenance:** pinned Tibia-derived appearance/sprite inputs must not be moved or publicly published by repository extraction without the separate legal/redistribution decision already identified by product-readiness work.

## P1

- rendering currently accepts legacy `Tile` objects and must be adapted to canonical export primitives;
- creature/environment asset generation mixes canonical-content resolution with presentation derivation;
- CI currently proves legacy pinned hashes/chunk counts, not future Game->Atlas schema compatibility;
- search/spatial schemas have no separately versioned inter-repository contract today;
- historical commits may touch both future-owner files in one commit, so selective filtering preserves commit ancestry but cannot make each historical commit semantically single-purpose.

## P2

- compatibility aliases such as `viewer-runtime.js` vs `viewer_runtime.js` should be normalized later;
- benchmark/research tooling may not merit destination history if the codec decision is superseded;
- current static HTML/JS implementation may later be replaced by a framework, but behavior tests and UX history remain useful.

## P3

- exact destination folder names/package language/build system are not decided here;
- legacy documentation can remain in this source repo and be linked rather than copied wholesale.

# Open Decisions

1. Exact canonical Oteryn World Model representation and stable IDs.
2. Whether Atlas export contains tile-level render primitives, pre-rendered canonical imagery, or both capabilities.
3. Whether appearance/sprite decoding and rasterization are Atlas-owned build tasks or a neutral asset compiler consumed by Game and Atlas.
4. Which Game facts are safe/public in Atlas details versus intentionally omitted from the public export.
5. Stable schema format: JSON/JSONL, protobuf/FlatBuffers/other binary chunks, or hybrid manifest + binary chunks.
6. Versioning and retention policy for immutable Atlas exports and publications.
7. Destination licenses and redistribution policy for any Tibia-derived generated imagery/assets.
8. Whether current static JS viewer is evolved directly or used as behavior/reference during a web-stack rewrite.
9. Final curated list of historical docs/research to carry to `Oteryn-Atlas` versus leave linked in legacy.
10. Exact history-extraction method after refactor: path-filtered history, subtree split, or clean repository with provenance tags/links. `git filter-repo` is feasible but not yet authorized.

# Final Recommendation

**RECOMMENDATION: EXTRACTABLE_WITH_REFACTOR.** Preserve the current Atlas as a valuable, technically proven migration source, but do not equate its folder boundary with the future repository boundary.

The highest-value direct history candidate for `Oteryn-Atlas` is the browser/publication side: viewer runtime, deep links, floor/navigation behavior, bounded caches, search/spatial projection, details/overlays, overview generation, publication verification, and Atlas-specific animation presentation. The highest-value code that must instead move or be reimplemented in `Oteryn-Game` is the OTBM node/semantic parser, legacy map/content adapters, spawn/house/mechanics/NPC/monster/raid interpretation, Legacy IR and world validation/compiler responsibilities.

Do not run `git filter-repo` until the Game->Atlas export contract exists and the current mixed modules (`atlas.py`, `factual_layers.py`, creature/environment generation) have been split or replaced. At that point a selective history-preserving extraction is realistic and preferable to a full rewrite of the viewer, while a native rewrite is preferred for the future Game importer/compiler boundary.
