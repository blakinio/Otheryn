# Oteryn Dynamic Semantic Atlas — programme and roadmap

```yaml
programme_status: PROPOSED
programme_revision: 1
project_lane: otheryn-content
architecture: docs/architecture/oteryn-dynamic-semantic-atlas.md
created: 2026-08-17
```

## Mission

Evolve Oteryn Atlas from a raster-first world viewer into a semantic, GPU-rendered, interaction-capable world runtime while preserving the current raster Atlas as the canonical visual baseline, fallback and rollback path until the new architecture is independently proven.

The programme is intentionally incremental. It must not block the current raster product-readiness work, current Synology deployment, or the production 32-shard run.

## Outcome

Long-term user capability:

```text
browse map
-> inspect authoritative tile/item/entity data
-> see animation/state changes without rerendering world PNGs
-> simulate safe doors/levers/teleports/floor transitions
-> talk to NPCs in a read-only simulation
-> inspect spawns/zones/quests/pathing
-> optionally observe authoritative live Game Server state
-> reuse the same semantic foundation for a future map editor
```

The browser should fetch only visible semantic chunks plus reusable sprite resources rather than a pre-rendered image copy of every world state.

## Delivery classification

The programme contains multiple future user-facing phases, but this initial repository record is architecture/planning only.

```yaml
current_delivery:
  type: documentation
  user_facing: false
  backend_required: false
  frontend_required: false
  integration_required: false
  e2e_required: false
  completion_claim: internal_only
future_programme:
  type: full_stack
  user_facing: true
  backend_required: true
  frontend_required: true
  integration_required: true
  e2e_required: true
```

## Canonical invariants

All implementation phases inherit these invariants unless the owner explicitly changes them through a reviewed architecture decision:

1. Current raster Atlas remains available until semantic parity and rollback are proven.
2. World truth is semantic and producer-authored; pixels are presentation only.
3. Long-term OTBM/legacy-content interpretation belongs to Oteryn-Game, not the Atlas browser.
4. Atlas consumes a versioned immutable semantic export.
5. Dynamic state is separate from immutable world chunks.
6. Browser simulation is non-authoritative and read-only with respect to game persistence/economy/quest state.
7. Arbitrary legacy Lua/server scripts never execute in the browser.
8. Exact format/codec/chunk-budget decisions are benchmark-gated.
9. Private/public redistribution restrictions remain unchanged.
10. Every migration phase has a raster rollback path.

## Workstream map

```text
A. Semantic contract/export
        |
        +--> B. Sprite package
        |
        +--> C. WebGL renderer
                 |
                 +--> D. streaming/cache/LOD
                 |
                 +--> E. inspector
                 |
                 +--> F. interaction IR + local simulation
                              |
                              +--> G. NPC dialogue simulation
                              |
                              +--> H. optional live-state protocol bridge

All above ---------------------------------> I. editor foundation (future)
```

## Phase 0 — baseline freeze and evidence inventory

### Goal

Turn the existing raster Atlas into an explicit migration oracle rather than treating it as disposable legacy output.

### Required work

- identify exact canonical raster release/world revision used for parity;
- record baseline viewer scripted journeys;
- record cold/warm bytes, requests, frame timing and memory on the real private preview when available;
- define deterministic reference viewports/chunks for pixel comparisons;
- inventory current factual/search/spawn/animation schemas that semantic export must preserve or supersede;
- inventory which data is Game truth versus Atlas-derived presentation/indexing;
- keep PR #446/local overview optimization separate from semantic architecture.

### Exit gate

A bounded evidence index exists and semantic PoC acceptance can be evaluated against fixed raster inputs.

## Phase 1 — semantic export contract + bounded Thais Z7 corpus

### Goal

Produce a small immutable semantic world package for a real canonical Thais Z7 area without changing production Atlas.

### Deliverables

- logical schema v1;
- world manifest with revision/capabilities;
- content-addressed chunk index;
- semantic chunks with ground/stacks/attributes/navigation facts;
- appearance manifest;
- deduplicated sprite subset/pages;
- independent export validator;
- malformed/version mismatch negative tests.

### Format policy

Do not lock the final wire format before measuring at least two viable encodings on the same real PoC chunks.

### Exit gate

The exported positions/items/attributes exactly match canonical producer truth for the selected area and the export is deterministic byte-for-byte for identical input.

## Phase 2 — WebGL2 static renderer parity

### Goal

Render the PoC area directly from semantic chunks and sprite pages.

### Deliverables

- WebGL2 renderer;
- canonical stack/layer ordering;
- nearest-neighbor/pixel snapping;
- camera/deep-link/floor support;
- semantic chunk loader;
- sprite page manager;
- raster/semantic mode switch in development only;
- reference composition test and browser screenshot parity suite.

### Exit gate

For fixed static states, the semantic renderer matches the canonical raster oracle under the approved parity method and no authoritative identity is inferred from pixels.

## Phase 3 — viewport streaming, cache and LOD

### Goal

Prove that semantic rendering scales as a map application rather than loading the entire world.

### Deliverables

- visible-chunk resolver;
- bounded prefetch ring;
- request deduplication/cancellation/stale-result protection;
- decoded-chunk LRU;
- sprite-page/GPU cache policy;
- floor-switch cleanup;
- instrumentation for bytes/requests/decode/upload/frame timing;
- far-zoom prototype using coarse resources, with current raster overview retained as fallback.

### Exit gate

A scripted pan/zoom/floor/deep-link journey stays within evidence-derived network/memory budgets and does not create unbounded requests or cache growth.

## Phase 4 — first-class semantic Tile Inspector

### Goal

Use the semantic chunk already in memory to expose authoritative world data under the pointer/tap.

### Deliverables

- exact X/Y/Z tile resolution;
- ground/content/legacy IDs where canonical;
- ordered stack list;
- AID/UID only when present;
- tile flags/navigation facts;
- entity/interaction references;
- explicit empty/unknown/unsupported states;
- desktop hover and deliberate touch inspect behavior.

### Relationship to existing backlog

This phase is the natural target implementation of `ATLAS-PR-013` after the semantic foundation is ready. It must not misreport exact tile identity at far-zoom aggregation levels.

### Exit gate

Inspector values come directly from loaded semantic truth and remain identical across pan/zoom/render mode for the same logical position.

## Phase 5 — normalized Interaction IR + local actor simulation

### Goal

Make the map stateful without connecting it to the live Game Server.

### Initial interaction set

Prioritize mechanics with small deterministic state machines:

- doors;
- levers/switches;
- teleports;
- stairs/floor transitions;
- rope/hole navigation where normalized safely;
- inspect actions.

### Deliverables

- allowlisted Interaction IR;
- producer validator;
- ephemeral browser state store;
- local actor position/pathfinding;
- visual state substitutions;
- reset/replay deterministic simulation;
- explicit unsupported/server-only effect representation.

### Exit gate

At least one real canonical interaction from each accepted initial class is simulated end-to-end without browser execution of arbitrary server logic and without persistent game mutation.

## Phase 6 — NPC dialogue simulation

### Goal

Allow clicking/talking to canonical NPCs using exported simulation-safe dialogue semantics.

### Deliverables

- normalized NPC dialogue graph/state machine;
- intent/phrase matching or explicit response choices;
- ephemeral conversation context;
- guard evaluation for safe read-only facts;
- classification of server-only outcomes;
- UI transcript/choices/reset;
- unsupported-path handling.

### Safety boundary

No real money, items, bank state, inventory, quest progression, rewards, persistence or account mutation.

### Exit gate

At least one simple and one branching real canonical NPC dialogue flow can be reproduced in a resettable local simulation, with server-only effects clearly non-executed.

## Phase 7 — world intelligence overlays

### Goal

Exploit semantic world structure beyond rendering.

Candidate capabilities:

- spawn areas and routes;
- NPC patrol/navigation;
- quest/mechanics references;
- houses/zones/towns;
- teleport graph;
- pathfinding between points/floors;
- interaction graph visualization;
- semantic search by content/entity/property.

Each overlay consumes producer truth or an Atlas-derived index with explicit provenance.

## Phase 8 — optional authoritative live-state bridge

### Goal

Overlay real server state on the same immutable semantic world.

### Prerequisites

- explicit owner authorization for connected live-state work;
- shared `protocol-oteryn` contract;
- world revision/capability negotiation;
- authentication/authorization design;
- snapshot/delta sequencing and reconnect semantics;
- privacy/security review.

### Candidate capabilities

- live NPC/creature positions;
- door/lever state;
- environmental effects;
- selected non-sensitive world events;
- authoritative NPC interaction responses in a dedicated simulation or live context.

### Exit gate

Static world revision and dynamic state stream are proven compatible and fail closed on revision/sequence mismatch.

## Phase 9 — semantic-first default and raster retirement decision

### Goal

Make semantic rendering the primary detail experience only after real evidence.

### Gates

- owner visual acceptance;
- real browser E2E;
- performance/storage/network comparison;
- mobile/touch/accessibility acceptance;
- operational Synology deployment/rollback proof;
- no material audit findings;
- public redistribution policy if Internet access is considered.

Raster may continue as far-zoom LOD and permanent regression oracle even after semantic detail becomes default.

## Phase 10 — editor foundation (separate future programme)

The viewer/runtime project stops before production authoring.

A later editor programme may reuse:

- semantic world schema concepts;
- sprite/appearance renderer;
- selection/picking;
- inspector;
- navigation/interaction visualization.

It must add separately reviewed authoring transactions, validation, authentication/authorization, persistence, conflict handling, history/undo, publication and rollback.

## Data contract maturity levels

```text
L0 Experimental
  PoC only; no compatibility promise.

L1 Versioned preview
  schemaVersion + capabilities + deterministic validator; backwards compatibility within preview rules.

L2 Stable Atlas export
  Game producer and Atlas consumer compatibility matrix; migration tooling/tests.

L3 Shared ecosystem world contract
  used by Atlas plus other consumers such as editor/tooling/client; changes require formal compatibility governance.
```

Do not prematurely call the PoC schema L3.

## Benchmark plan

### Same-input A/B

Raster and semantic modes must execute the same scripted journey and selected viewports.

Collect:

```yaml
network:
  cold_bytes:
  warm_bytes:
  request_count:
  largest_resource:
  visible_chunk_count:
latency:
  first_manifest_ms:
  first_map_ms:
  chunk_decode_p50_ms:
  chunk_decode_p95_ms:
  texture_upload_ms:
runtime:
  pan_frame_p50_ms:
  pan_frame_p95_ms:
  long_task_count:
  js_heap_peak:
  gpu_texture_estimate:
storage:
  semantic_chunks_bytes:
  appearance_metadata_bytes:
  sprite_pages_bytes:
  coarse_lod_bytes:
  raster_baseline_bytes:
```

Exact budgets are set from measured baseline and product goals rather than invented before Phase 0/1 evidence.

## Compression/encoding benchmark matrix

The first format decision should compare at least:

- raw logical representation size;
- compressed transfer size;
- browser decode CPU/time;
- implementation complexity;
- random/partial section access;
- deterministic output;
- Rust producer ergonomics;
- JS/WASM consumer ergonomics;
- schema evolution/unknown-field behavior;
- debugging/tooling quality.

Sprite package benchmark separately compares only formats that preserve the accepted pixel semantics.

## Validation ladder

Every implementation phase uses:

```text
focused schema/module tests
-> component producer/consumer tests
-> deterministic outcome verification
-> fresh audit
-> real browser/system E2E where applicable
-> exact-head required CI
```

Generated proprietary full-world corpora are not committed to Git. Public GitHub artifacts must remain bounded to repository-approved fixtures/evidence; real full-world private evidence stays under the established private deployment boundary.

## Related current work

- `docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md` — target ownership split and migration source review;
- `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md` — current raster product-readiness gates;
- `docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md` — current private-preview/browser readiness;
- `docs/agents/tasks/active/OTH-20260817-atlas-production-4-deployment.md` — current raster production deployment execution;
- PR #446 — independent raster/local overview generation performance work.

The semantic project does not supersede those tasks automatically.

## Programme-level acceptance

The semantic programme is ready to become the primary Atlas architecture only when all are proven:

1. Versioned producer/consumer semantic contract exists.
2. Real canonical world slice exports deterministically.
3. WebGL semantic rendering matches the raster oracle at detail zoom.
4. Visible-world streaming is bounded and measured.
5. Tile Inspector is authoritative without pixel inference.
6. At least one safe stateful interaction works locally.
7. NPC dialogue simulation proves the interaction architecture without persistent mutation.
8. Real browser performance and UX are acceptable.
9. Synology deployment and rollback are proven for the new runtime.
10. Raster fallback/oracle remains usable until an explicit retirement decision.
11. No material security/trust/publication finding is open.
12. Any connected live-state mode has a separately reviewed protocol/security contract.

## Immediate next implementation package

Do **not** start a full semantic rewrite.

The next package after this architecture project is accepted should be one bounded PoC task:

**DYN-ATLAS-001 — Semantic Thais Z7 Proof**

Objective:

> Export one real canonical Thais Z7 area into a versioned semantic package, render it with a minimal WebGL2 viewer beside the raster oracle, and collect deterministic identity/parity/network/decode evidence without changing the production viewer or deployment.

That task should discover the exact bounding box and sample interactions/entities from canonical data instead of guessing them in advance.