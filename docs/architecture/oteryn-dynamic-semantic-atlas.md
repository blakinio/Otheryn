# Oteryn Dynamic Semantic Atlas — target architecture

```yaml
architecture_status: PROPOSED
architecture_revision: 1
project: Oteryn Dynamic Semantic Atlas
repository_record: blakinio/Otheryn
project_lane: otheryn-content
trusted_base: e382f93b7b1b12e39edfe14afe08ccb639c4fe2a
created: 2026-08-17
```

## 1. Decision summary

The current raster OTBM Atlas remains the canonical pixel-perfect reference, private-preview fallback and regression oracle. It is **not** the intended long-term world representation for an interactive Atlas.

The target architecture is:

```text
legacy OTBM / canonical Oteryn World Model
                  |
                  v
        versioned semantic world export
                  |
        +---------+--------------------+
        |                              |
        v                              v
 immutable semantic chunks      appearance/sprite package
        |                              |
        +---------------+--------------+
                        v
                browser Atlas runtime
              WebGL2 baseline renderer
                        |
        +---------------+------------------+
        |               |                  |
        v               v                  v
 static world       state overlay     factual/UX overlays
 ground/items       doors/NPC/etc.    search/spawns/zones
        |               |
        +-------+-------+
                v
        interaction/simulation layer
```

The browser must render the visible map from semantic tile/entity data and deduplicated sprite resources. Dynamic state is an overlay over immutable world data, not something baked into PNG pixels.

This enables a progression from **viewer -> inspector -> read-only simulator -> connected live-state viewer -> editor foundation** without replacing the world representation at every step.

## 2. Architectural context and constraints

This proposal preserves the current verified Atlas instead of invalidating it.

Verified repository context on the trusted base:

- the current technical Atlas uses schema version 3, 128-tile chunks and a certified 3494 populated-detail-chunk world;
- current detail and overview outputs are raster PNG derivatives;
- factual map data already exists separately from pixels for several inspection/search features;
- `docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md` already concludes that future ownership should separate Game-owned OTBM/canonical-world interpretation from Atlas-owned browser presentation and publication;
- `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md` already requires viewport-bounded factual inspection and explicitly treats lazy rendering/storage format changes as separate measured decisions;
- current private Synology deployment and the currently running production raster generation are independent from this proposal and must not be changed by this architecture task;
- open PR #446 optimizes legacy/local raster overview production but does not change the target semantic architecture.

This document therefore defines a **migration target**, not an authorization to replace the current production viewer or deployment.

## 3. Architectural principles

### 3.1 World truth is semantic, not visual

A coordinate is represented by structured world data, for example:

```text
position: 32369,32241,7
ground: <appearance/content ref>
stack:
  - <item/entity ref>
  - <item/entity ref>
attributes:
  actionId: optional
  uniqueId: optional
flags:
  walkable: true/false
  blocksProjectile: true/false
```

A pixel has no authority. Tile, item, action, spawn, NPC, zone and interaction identity always come from semantic data.

### 3.2 Immutable world and mutable state are separate

The static world export contains canonical immutable definitions and placement. Runtime state contains only values that can change, for example:

- door open/closed;
- lever left/right;
- moving NPC position/direction;
- creature animation phase;
- temporary field/effect state;
- selected simulation actor position;
- future live server snapshot/delta state.

The renderer composes the two layers. It does not regenerate the world chunk because a door changed state.

### 3.3 Browser is never authoritative for game state

The semantic Atlas may simulate safe interactions locally, but it must not become an authority for rewards, inventory, quests, economy, persistence or live game state.

Any future connected mode treats the Game Server as authoritative and consumes versioned snapshots/deltas or interaction responses.

### 3.4 Raster remains an oracle and rollback path

The existing raster Atlas is retained as:

- canonical visual reference during migration;
- pixel-parity/regression oracle;
- fallback viewer mode;
- coarse/far-zoom fallback while semantic LOD matures;
- operational rollback path.

The project does not delete the raster pipeline before semantic parity and deployment evidence exist.

### 3.5 No arbitrary legacy script execution in the browser

Legacy Lua or server scripts are never shipped to or executed by the browser as interaction logic.

Interactions that can be simulated are converted by a trusted producer into a normalized allowlisted Interaction IR. Unsupported or ambiguous legacy mechanics remain explicitly unsupported/unknown.

## 4. Target ownership boundary

This proposal follows the existing extraction review.

### Oteryn-Game / canonical world producer

Target ownership:

- OTBM import and legacy parsing;
- canonical World Model;
- tile stacks and authoritative item/content identifiers;
- houses, towns, waypoints and map facts;
- collision/navigation facts;
- canonical NPC/monster/spawn identity;
- normalized interaction definitions derived from trusted game/content logic;
- future export of simulation-safe NPC/dialogue facts;
- source provenance and world revision identity.

The browser Atlas must not traverse Crystal/Canary source trees or interpret OTBM/Lua/XML directly in the long-term architecture.

### Oteryn-Atlas / semantic consumer and presentation runtime

Target ownership:

- semantic export consumption and validation;
- browser-visible spatial indexes;
- deduplicated sprite/appearance publication package;
- WebGL rendering;
- viewport streaming/cache;
- far-zoom LOD publication;
- search and inspector UX;
- safe local simulation presentation;
- browser performance/observability;
- raster fallback/oracle integration;
- private/public distribution policy specific to Atlas.

### `protocol-oteryn` / future connected state bridge

If Atlas later displays real live state, the transport contract belongs in the shared protocol/domain boundary rather than an Atlas-only ad-hoc API.

Potential future capabilities include:

```text
atlas.world.snapshot
atlas.world.delta
atlas.entity.state
atlas.interaction.request
atlas.interaction.result
atlas.npc.dialogue
```

These are future capabilities only. The first semantic Atlas proof is static/read-only and requires no live Game Server connection.

## 5. Semantic world export contract

### 5.1 Logical contract before wire-format selection

The project standardizes the **logical schema first**. Physical encoding is benchmark-gated.

Initial candidates for physical encoding may include a schema-driven binary format, a compact sectioned custom binary, or a structured binary codec. The project must not select one solely from preference; the PoC measures browser decode cost, payload size, schema evolution, deterministic encoding and Rust/JS/WASM tooling.

### 5.2 World manifest

A semantic release has one immutable manifest containing at least:

```yaml
schemaVersion: <integer>
worldRevision: <content-addressed identity>
producerRevision: <exact producer version/SHA>
source:
  worldModelRevision: <identity>
  legacyMapSha256: <when applicable>
appearanceRevision: <identity>
chunkSize: 128
floors: [0..15]
capabilities:
  - semantic.tiles
  - semantic.stacks
  - semantic.attributes
  - semantic.navigation
  - optional.interactions
  - optional.npcs
chunkIndex: <path/hash>
appearanceManifest: <path/hash>
minimumViewerVersion: <version>
```

The initial PoC keeps the current 128-tile chunk boundary to simplify parity, coordinates, regression and migration. A different chunk size requires measured evidence and a separate decision.

### 5.3 Content-addressed chunks

Chunks are immutable and identified by digest. Coordinate lookup resolves to the digest currently associated with `(z, chunkX, chunkY)`.

Benefits:

- unchanged chunks are reused across releases;
- browser caches do not need destructive invalidation;
- CDN/private cache behavior can become immutable by hash later;
- producer and consumer can independently verify bytes;
- incremental world updates naturally publish only changed chunks.

### 5.4 Chunk logical layout

A semantic chunk should be columnar/sectioned rather than one large object graph. Recommended logical sections:

```text
header
  schema/capabilities
  z, chunkX, chunkY
  logical bounds
  worldRevision
  chunkDigest

tiles
  occupancy/index bitmap
  ground refs
  flattened stack refs + per-tile offsets/counts
  optional tile flags
  optional AID/UID attributes

entities
  stable entity/content refs
  position/direction
  static appearance state
  entity kind

navigation
  walkability/cost flags
  floor-change links
  teleport/navigation edges when safe to expose

interactions
  references to normalized interaction definitions

factual refs
  zone/house/town/spawn/quest/search identifiers as capabilities permit
```

Sparse optional sections should be omitted when absent.

### 5.5 Stable identifiers

The export distinguishes:

- **world position** — X/Y/Z;
- **content definition ID** — stable Oteryn content identity;
- **appearance/sprite ID** — presentation identity;
- **instance/entity ID** — stable within a world revision when needed;
- **legacy server/item ID** — retained only when it is canonical evidence and useful for inspection/migration.

A browser must never infer content identity from sprite pixels.

## 6. Appearance and sprite package

The largest structural storage advantage over raster-only rendering comes from storing sprite pixels once and referencing them many times.

Target package:

```text
appearance-manifest
  content/appearance mapping
  dimensions/layers/patterns
  animation metadata
  sprite page coordinates

sprite pages
  deduplicated source sprite/frame pixels
  immutable page hashes
  nearest-neighbor sampling
```

Initial constraints:

- preserve pixel-art RGBA semantics;
- use nearest-neighbor sampling and pixel snapping;
- avoid lossy texture compression until A/B and pixel-diff evidence authorizes it;
- keep animation frames as metadata + sprite references instead of baking repeated world rasters;
- permit separate publication policy for proprietary source-derived appearance bytes.

Packing/page size and PNG/WebP/KTX2 selection remain benchmark decisions. The architecture requires deduplication and immutable identity, not a specific codec.

## 7. Browser renderer

### 7.1 Baseline technology

Use WebGL2 as the initial compatibility baseline. WebGPU may become an optional accelerated backend later, but it must not be required for the first semantic viewer.

### 7.2 Rendering model

For each visible chunk:

1. decode/cached semantic arrays;
2. resolve appearance references;
3. upload or reuse sprite texture pages;
4. build ordered instance batches;
5. draw instanced quads with canonical stack/layer ordering;
6. apply mutable state substitutions/overlays;
7. draw factual overlays independently.

The browser should not create one DOM node per tile/item.

### 7.3 Pixel parity

Static semantic rendering must preserve canonical raster ordering and appearance semantics.

Two different tests are required:

- **reference composition parity** — deterministic semantic composition against the existing canonical raster generator for the same chunk/viewport;
- **browser visual parity** — headless/real browser screenshot comparison with a separately documented browser-render tolerance where exact framebuffer equivalence is not technically portable.

Known animated/dynamic regions are tested with controlled phase/state rather than masked indiscriminately.

## 8. Streaming, cache and memory model

The browser loads only the visible world plus a bounded prefetch ring.

Required runtime invariants:

- visible-chunk calculation is deterministic for camera/floor;
- requests are deduplicated;
- rapid pan does not create unbounded in-flight requests;
- stale requests may complete but cannot overwrite current-view state incorrectly;
- decoded semantic chunks use bounded LRU memory;
- GPU sprite pages use a separate bounded cache/refcount policy;
- floor switches release or age irrelevant chunk state;
- deep links do not require downloading the whole world;
- inspector lookup uses the same loaded semantic chunk, not a second per-hover endpoint.

Exact byte/RAM/cache limits are deliberately **not invented here**. Phase 1/2 records raster baseline measurements and sets budgets from evidence, consistent with ATLAS-PR-004.

## 9. LOD and far zoom

Do not reproduce the current storage pattern merely by creating semantic equivalents of every `DETAIL + 4x + 8x` PNG.

Target policy:

### Near/detail zoom

Semantic GPU rendering with exact tile/item identity and interactions enabled.

### Medium zoom

Semantic rendering may simplify/cull nonessential stacks and labels, subject to measured quality and performance. Exact tile inspection remains available only when one visual pointer location maps unambiguously to a world tile.

### Far zoom

Use a small coarse representation optimized for geography/navigation, for example floor-level/supertile raster or another measured LOD representation generated from the canonical semantic world.

The current raster overview can remain the fallback until the replacement is proven.

The far-zoom representation should have **substantially fewer logical resources than one derivative per detail chunk**. The exact tiling strategy is a PoC/benchmark decision.

## 10. Interaction model

### 10.1 Interaction IR

Simulation-safe interactions are normalized by the trusted producer into a finite allowlisted model.

Logical shape:

```yaml
interactionId: <stable id>
kind: door | lever | teleport | stairs | rope | container | npc | inspect | custom_safe
trigger: use | step | talk | inspect
guards:
  - <normalized condition>
states:
  - <named state>
transition:
  from: <state>
  to: <state>
effects:
  - visual_state
  - move_simulation_actor
  - open_dialogue
  - reveal_information
  - navigation_edge
serverOnlyEffects:
  - <opaque/non-simulatable effect refs>
```

The browser executes only recognized safe effects. Unknown, arbitrary-script or server-only effects are not executed and are shown as unsupported/partial where relevant.

### 10.2 Local simulation actor

A later phase can add an ephemeral local actor for:

- movement/pathfinding;
- floor transitions;
- teleport preview;
- opening/closing simulated doors;
- lever state previews;
- NPC interaction context.

Local simulation state is resettable and does not mutate the world export or Game Server.

### 10.3 Pathfinding

Pathfinding consumes producer-authored navigation flags and explicit floor-change/teleport edges.

It does not infer collision from rendered pixels.

## 11. NPC conversation architecture

NPC conversation is a first-class future capability, but the initial design is explicitly safe/read-only.

Producer responsibilities:

- canonical NPC identity;
- position/outfit/appearance;
- normalized dialogue intents/phrases/state-machine facts when derivable;
- explicit requirements/guards safe to expose;
- classification of server-only side effects such as purchases, rewards, quest mutation, banking or inventory changes.

Atlas simulation responsibilities:

- render/click/select NPC;
- maintain ephemeral dialogue context;
- traverse only exported safe dialogue transitions;
- show available responses/actions;
- clearly label unsupported/server-only outcomes;
- never grant items, currency, quest state or persistent changes.

Future connected mode may send the conversation through an authoritative Game Server simulation/live endpoint, but that is a later protocol/security task and is not required for local Atlas simulation.

## 12. Dynamic/live mode

Dynamic mode is an overlay, not a second world format.

Potential flow:

```text
immutable semantic world revision
          +
authoritative server snapshot
          +
ordered state deltas
          v
browser state store
          v
same renderer
```

Requirements before implementation:

- version/capability negotiation;
- world revision match between static world and state stream;
- monotonic sequence or snapshot/delta recovery;
- bounded reconnect/replay behavior;
- authentication/authorization design;
- explicit privacy/publication policy;
- fail closed when revisions do not match.

## 13. Inspector and future editor

### Viewer -> Inspector

Because each screen position maps to semantic tile data, Tile Inspector becomes a direct read of loaded world data. It can expose ground ID, stack IDs, AID/UID, flags, entities, interactions and provenance without pixel inference.

### Inspector -> Editor foundation

The same logical World Model can later support editing, but editing is a separate product/security architecture.

The future editor should operate on authoring patches/transactions over canonical semantic data, not mutate published immutable browser chunks in place.

Editor concerns intentionally deferred:

- authentication and authorization;
- collaborative locking/conflicts;
- validation and server/content compiler feedback;
- undo/redo/history;
- persistence and review workflows;
- live publish/rollback.

## 14. Compression and packaging strategy

The semantic design reduces duplication before codec optimization:

- repeated world sprite pixels are stored once in sprite pages;
- tile chunks store compact references and sparse attributes;
- unchanged chunks are content-addressed and reused;
- animations reference frame data rather than repeated rendered maps.

Compression selection is measured separately for:

1. semantic chunk bytes;
2. metadata/indexes;
3. sprite pages;
4. coarse raster LOD.

Candidate techniques may include HTTP compression, precompressed binary sections and lossless image codecs. A custom WASM decompressor is justified only if network savings exceed added startup/CPU/cache complexity.

The current `PNG zlib level 9` raster baseline remains a measurement reference, not a constraint on semantic packaging.

## 15. Security, trust and publication boundaries

- Semantic data received by the browser is non-authoritative client data.
- Atlas must not execute arbitrary Lua/server scripts.
- Do not include server secrets, credentials, protected configuration or hidden runtime-only data in exports.
- The producer decides which interaction/factual capabilities are safe to export.
- Private/public redistribution review remains required for Tibia-derived appearance/map data; semantic conversion does not remove that boundary.
- No Internet-facing route is authorized by this architecture.
- No live Game Server mutation is authorized by this architecture.
- Future editor/write paths require separate authentication, authorization, audit and deployment decisions.

## 16. Migration strategy

### Stage A — preserve current production

Keep raster Atlas production, Synology deployment and current viewer unchanged.

### Stage B — bounded semantic PoC

Generate only a bounded Thais Z7-area semantic package plus required sprite subset. Run it as a separate development viewer route/build output.

### Stage C — dual renderer

Add `Raster` and `Semantic` render modes against the same coordinates/deep links. Raster remains default until acceptance gates pass.

### Stage D — semantic detail default

After parity, streaming/performance, inspector and browser E2E evidence, semantic rendering becomes default at detail/medium zoom. Raster remains fallback and far-zoom LOD/oracle.

### Stage E — interaction simulation

Add safe stateful interactions and NPC dialogue simulation without live mutations.

### Stage F — connected dynamic state

Optionally connect to authoritative Oteryn Game Server state using shared protocol contracts.

### Stage G — editor foundation

Reuse the semantic model for inspection/authoring only after separate editor architecture and authorization.

Every stage has an explicit rollback to the previous renderer/runtime. No migration stage deletes the canonical raster baseline before independent evidence says it is safe.

## 17. Proof-of-concept scope

The first implementation proof should be deliberately bounded:

```yaml
area: selected Thais bounding box
floor: 7
world_source: current canonical world revision
chunk_boundary: current 128-tile grid
renderer: WebGL2
state: static plus optional local-only demo state
server_connection: none
public_deployment: none
```

The selected area must contain enough real canonical content to prove:

- ground + multi-item stacks;
- transparency/stack ordering;
- at least one floor/navigation transition;
- at least one inspectable entity/NPC if present in the selected canonical area;
- factual Tile Inspector data;
- repeated sprites proving deduplication value.

The exact bounding box and entity examples are discovered from canonical data rather than guessed in this document.

## 18. PoC evidence and acceptance

### Functional

- semantic coordinates map exactly to canonical X/Y/Z;
- ground/stack IDs match producer truth;
- static rendering matches canonical raster reference according to the approved parity test;
- pan/zoom/floor/deep-link behavior remains deterministic;
- inspector reads semantic data and performs no pixel inference;
- cache/request counts remain bounded during rapid navigation.

### Performance

Measure the same scripted viewport journey for raster and semantic modes:

- cold bytes transferred;
- warm bytes transferred;
- request count;
- time to first meaningful map;
- semantic chunk decode P50/P95;
- texture upload time;
- steady pan/zoom frame timing;
- JS heap and estimated GPU texture footprint;
- large navigation jump latency.

Budgets are set **after baseline measurement**, not invented beforehand. The semantic design must demonstrate a material reason to proceed: storage/network reduction, interaction capability, runtime responsiveness, or a combination.

### Regression

- producer-side deterministic chunk digest tests;
- logical schema compatibility tests;
- reference-render pixel comparison;
- browser screenshot/interaction E2E;
- malformed/truncated chunk fail-closed tests;
- unknown schema/capability rejection tests;
- cache/revision mismatch tests.

## 19. Explicit non-goals for the first programme

The initial semantic programme does **not** include:

- replacing the currently running production raster build;
- deleting PNG Atlas support;
- public Internet distribution;
- live combat simulation;
- real trading/banking/economy mutation;
- persistent quest progression;
- player inventory persistence;
- executing arbitrary NPC/server Lua in the browser;
- full Game Server emulation in JavaScript;
- WebGPU as a hard requirement;
- a production map editor;
- automatic write-back to OTBM;
- changing the Game Server protocol before a connected-state phase is approved.

## 20. Deferred decisions and required evidence

These are intentionally not fixed by this proposal:

| Decision | Required evidence |
|---|---|
| Physical semantic chunk encoding | PoC size/decode/schema-evolution benchmark across real chunks. |
| Chunk size different from 128 | Viewport request/decode/cache benchmark proving benefit. |
| Sprite page format/size | RGBA exactness, decode/upload, storage and cache benchmark. |
| Far-zoom LOD format | Full-floor navigation quality, request count and storage measurements. |
| WebGPU backend | Browser support and measured benefit over WebGL2. |
| Live state transport | Oteryn protocol/domain architecture and security review. |
| NPC interaction coverage | Canonical content compiler ability to normalize real dialogue/mechanics safely. |
| Editor writes | Separate editor product/security architecture. |

## 21. Architecture success condition

The architecture is proven only when a bounded semantic vertical slice can display real canonical world content, match the raster oracle at detail zoom, inspect authoritative tile/entity data, stream within measured browser budgets and support at least one safe stateful interaction without mutating authoritative game state.

Until then, the semantic Atlas remains a proposed migration programme and the current raster Atlas remains canonical production.