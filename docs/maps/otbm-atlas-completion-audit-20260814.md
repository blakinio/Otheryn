# Full OTBM Atlas completion audit — updated 2026-08-15

This document records the verified completion state of the canonical OTBM Atlas after the full-world, factual-layer, environment-animation and canonical creature-sprite work.

It is a state audit, not a replacement for the earlier product/UX handover in `docs/maps/otbm-atlas-conversation-handover-20260813.md`.

## Audit baseline

Repository: `blakinio/Otheryn`

Audited `main`:

`16e740adbf73757523795873c1106517e86dbe35`

Canonical CrystalServer revision:

`zimbadev/crystalserver@5e89bf8329ea406cb4ea8f4a18f32954f13e5418`

Canonical map:

`vendor/map-analysis/crystalserver/data-global/world/world.otbm`

Canonical Tibia assets:

`vendor/map-analysis/tibia-client/15.25.bd5a04/assets/`

Relevant merged delivery PRs include #371-#375, #378-#381, #383-#385, #387, #389-#391, #393-#397.

## Overall conclusion

### Original full-atlas contract

**DONE / VERIFIED.**

The original product contract for a complete canonical OTBM atlas is implemented: full-world preprocessing, bounded chunked browser loading, multi-resolution navigation, exact canonical detail rendering, persistent/shareable map state, factual overlays, conservative mechanics resolution and full-world release certification.

### Canonical creature sprite parity

**DONE / VERIFIED.**

PR #395 added one shared bounded `CreatureSpriteRenderer` for NPC and monster overlays using only the pinned vendored CrystalServer definitions and Tibia client appearances/sprite sheets. PR #396 archived the completed task and PR #397 revalidated the archived lifecycle plus the real Chromium creature showcase.

This closes the former audit gap for canonical NPC + monster sprite overlays.

### Expanded animation ambition

**PARTIAL / NOT YET VERIFIED AS COMPLETE.**

The current verified creature feature proves canonical close-zoom NPC and monster sprite rendering. It does **not** by itself prove a complete time-based creature walk/idle animation system with all canonical direction/phase semantics.

Do not describe creature walk/idle animation as DONE until direct code/tests/E2E prove that behavior.

## Requirement-by-requirement audit

| Requirement | Status | Verified state |
|---|---|---|
| Canonical CrystalServer `world.otbm` | DONE | Exact pinned map is vendored and used as the atlas source of truth. |
| Canonical client assets | DONE | Owner-selected Tibia 15.25 assets are vendored and fingerprinted. |
| Complete world support | DONE | All populated `Z=0..15` are supported. |
| No whole-world browser load | DONE | Viewer uses spatial chunks, viewport loading/prefetch and bounded caches. |
| Full-world release certification | DONE | Canonical release run completed all 16 floors and exactly 3494 chunks. |
| Full-world source consistency | DONE | Aggregate release validation records one canonical source fingerprint/map SHA. |
| Missing sprites in certified world render | DONE | Full-world release certification records `missingSprites == {}` for every floor. |
| Low/medium-zoom overview | DONE | Lightweight derived overview imagery is available for navigation. |
| Maximum/detail canonical sprite render | DONE | Detail mode uses pinned canonical OTBM + client assets. |
| `Auto` render mode | DONE | Supported as a first-class mode. |
| `Detailed` render mode | DONE | Supported without removing viewport/chunk bounded loading. |
| `Performance` render mode | DONE | Supported as lightweight overview-only behavior. |
| X/Y/Z state | DONE | Raw OTBM coordinates are first-class viewer state. |
| Zoom state | DONE | Preserved by viewer state. |
| Render-mode persistence | DONE | Persisted and represented in URL state. |
| Layer persistence | DONE | Enabled layers participate in persisted/shareable state. |
| URL/shareable state | DONE | Coordinates, zoom, render mode and layer state are restorable/shareable. |
| NPC spawn layer | DONE | Canonical spawn positions and source provenance are available. |
| NPC canonical sprites | DONE | Shared canonical creature renderer resolves NPC definitions from vendored CrystalServer data and renders close-zoom sprite overlays with conservative fallback. |
| Monster spawn layer | DONE | Canonical CrystalServer spawn positions are available as factual overlay data. |
| Monster canonical sprites | DONE | PR #395 added canonical monster sprite parity through the shared bounded creature renderer. |
| Creature source contract | DONE | Map/spawns, scripts, NPC definitions, monster definitions and appearance/sprite data are all pinned to `vendor/map-analysis/**`; no canonical creature fallback to `data-otservbr-global` or network data is permitted. |
| Creature low-zoom boundedness | DONE | Monster sprites retain low-zoom suppression and bounded image loading; unresolved records fall back conservatively. |
| Verified boss layer | DONE | Boss markers require explicit resolved `rewardBoss=true`; names/paths/categories alone never promote a creature to boss truth. |
| Direct OTBM teleports | DONE | Kept distinct from scripted transition evidence. |
| Scripted teleport/mechanics layer | DONE | Only `RESOLVED` + `PROVEN_STATIC` transitions are promoted to navigable truth; conditionality/provenance are preserved. |
| AID | DONE | Indexed and exposed with conservative resolution states. |
| UID | DONE | Indexed and exposed with conservative resolution states. |
| Houses | DONE | OTBM spatial data and world-house metadata are available. |
| House doors | DONE | Indexed as factual spatial records. |
| Towns | DONE | Parsed directly from canonical OTBM. |
| Waypoints | DONE | Parsed directly from canonical OTBM. |
| Raids/events | DONE | Point spawns and exact rectangular areas are exposed. |
| Raid rectangle sharding | DONE | A rectangle is present in every spatial chunk it intersects. |
| NPC shop services | DONE | Resolved from pinned NPC definitions/helper semantics. |
| NPC bank/guild-bank services | DONE | Resolved conservatively from pinned definitions/helper semantics. |
| NPC travel services | DONE | Proven destinations/costs can be exposed with source evidence. |
| Search/details integration | DONE | Factual layers participate in viewer search/details behavior. |
| Unknown/ambiguous behavior | DONE | `UNKNOWN`, `UNRESOLVED` and `AMBIGUOUS` are not silently promoted to certain spatial truth. |
| Environment/item cyclic animations | DONE | Runtime animation pipeline is wired into production and supports safe bounded animated object geometry. |
| Large/displaced animated item geometry | DONE | Merged implementation supports canonical 32x32, 32x64, 64x32 and 64x64 cyclic object geometry with conservative fallback. |
| Real NPC + monster browser showcase | DONE | PR #395 and #397 produced/validated real Chromium `otbm-creature-showcase` artifacts with both selected NPC and monster sprites loaded at 64x64. |
| Full animated NPC walk/idle cycles | NOT VERIFIED | Canonical NPC sprites are proven; complete time-based walk/idle phase playback has not been proven by the evidence reviewed here. |
| Full animated monster walk/idle cycles | NOT VERIFIED | Canonical monster sprites are proven; complete time-based walk/idle phase playback has not been proven by the evidence reviewed here. |
| Subjective visual parity with Oteryn Thais/TibiaMaps/TibiaRoute direction | NOT VERIFIED | Real production browser evidence exists, but subjective UX parity requires human visual review rather than inference from automated tests. |

## Full-world certification evidence

PR #389 archives the successful full-world release validation for implementation SHA:

`1021d08978f078ff845e6f3f82fbbbc482cbf543`

Recorded evidence:

- canonical release run `31813869825`: SUCCESS;
- all `Z0..Z15` floor jobs: SUCCESS;
- aggregate job `94839712570`: SUCCESS;
- exactly `3494` chunks;
- one common source fingerprint;
- canonical map SHA agreement;
- `verification.ok == true`;
- `missingSprites == {}` on every floor.

The former full-world-final-gate exception is closed and must not be reported as outstanding.

## Factual-layer completion evidence

PR #390 consumes the pinned `tools/otbm_atlas_facts` producer inside the production chunked atlas.

The archived task record is:

`docs/agents/tasks/archive/OTH-20260814-atlas-factual-layers.md`

Verified behavior includes:

- direct OTBM teleports remain separate from scripted transitions;
- only proven static scripted transitions become navigable spatial records;
- raid/event point spawns and exact areas are rendered;
- only explicit resolved `rewardBoss=true` evidence creates verified boss markers;
- NPC shop/bank/guild-bank/travel services enrich base-map NPC spawns;
- unknown, unresolved and ambiguous evidence remains non-authoritative;
- all added records remain spatially chunked and viewport bounded;
- search/details and URL-preserved layer controls cover the factual layers.

Final implementation head:

`06b467a33f267c31b1ac85fbe768f2b3b71aa1ef`

Squash merge:

`2bfacdd8349003aaa9675604269b8ae8004c19a6`

Recorded final validation includes CI, Required, autofix, independent factual audit, real Chromium factual-layer E2E, environment-animation E2E and OTBM Atlas Tests including canonical Thais render/browser validation.

## Canonical creature sprite completion evidence

PR #395 (`feat(atlas): add canonical monster sprite parity`) was squash-merged as:

`ea1810ed0a878230d1e68ad45e455c01ef7fc99d`

Final implementation head:

`bc2050cb604524cfc1699374a3e3dc691023a70d`

Canonical source contract used by that feature:

- map/spawns: `vendor/map-analysis/crystalserver/data-global/world/**`;
- runtime map-composition evidence: `vendor/map-analysis/crystalserver/data-global/scripts/**`;
- NPC definitions: `vendor/map-analysis/crystalserver/data-global/npc/**`;
- monster definitions: `vendor/map-analysis/crystalserver/data-global/monster/**`;
- appearances/sprite sheets: `vendor/map-analysis/tibia-client/15.25.bd5a04/assets/**`.

Final exact-head workflows recorded by PR #395 were green, including Required, CI, OTBM Atlas Tests, Environment Animation E2E, factual-layer audit/tests and the canonical creature showcase.

Pinned corpus results recorded by #395:

- NPC: 752 unique sprites, 974 resolved spawns, 94 unresolved, 8 ambiguous definitions;
- monsters: 719 unique sprites, 87,193 resolved spawns, 372 unresolved, 0 ambiguous definitions.

The real Chromium `otbm-creature-showcase` from #395 contained both a PNG screenshot and JSON source/statistics evidence; both selected NPC and monster sprites decoded as 64x64 before capture.

PR #396 archived `OTH-20260815-otbm-atlas-creature-sprites` after merge. PR #397 then fixed the post-closeout lifecycle regression and re-ran the relevant atlas/showcase validation on exact head `48f6be02191c5b9c5e4454c731d292eed943eeb8`, producing another PASS creature showcase artifact. PR #397 was merged as:

`16e740adbf73757523795873c1106517e86dbe35`

The creature-sprite task is therefore completed and archived, not resumable under `docs/agents/tasks/active/`.

## Animation completion boundary

The production environment/item animation pipeline is complete for its documented conservative contract.

Merged PR #387 generalizes runtime cyclic object animation while preserving:

- canonical shift/height displacement;
- safe underlay/phase/overlay composition;
- bounded per-instance browser behavior;
- deterministic static fallback for unsafe/unsupported cases;
- no inferred server-driven appearance state.

PR #395 additionally closes canonical static sprite parity for both NPCs and monsters. That is a stronger state than the 2026-08-14 audit originally recorded.

However, **static canonical creature sprite parity is not equivalent to verified time-based creature walk/idle animation**. Future work must inspect the actual renderer/runtime and prove phase/direction playback before changing that classification.

## Remaining work outside the completed atlas core

### P1 — verify and, if absent, implement full creature walk/idle animation

Before implementing anything, inspect current `main` to determine whether canonical time-based creature direction/phase playback already exists under a different name or path.

If absent, the next feature slice should be:

**Canonical Creature Animation — NPC + Monsters**

Required properties:

- use canonical creature appearance animation phases and direction semantics from pinned assets;
- no generated/mock animation;
- preserve conservative fallback when a phase/direction cannot be proven;
- remain viewport/chunk bounded;
- keep bounded image/animation caches;
- avoid world-wide creature payloads at browser startup;
- retain spawn/source provenance;
- real Chromium E2E must prove time changes between canonical animation phases for at least one NPC and one monster;
- human-viewable browser capture must come from the real production viewer.

### P2 — human visual UX review

PR #392 was closed unmerged because its NPC-only evidence scope was superseded by the broader canonical NPC+monster showcase in #395.

The evidence gap is no longer "no showcase exists". Real browser screenshots now exist. The remaining question is subjective/product-facing: whether the current production viewer matches the desired Oteryn Thais / TibiaMaps / TibiaRoute visual and interaction direction closely enough.

Do not call subjective visual parity proven until a human has inspected the actual production artifact.

## Repository hygiene noted by this audit

State after the creature-sprite work:

- PR #386 is closed unmerged; merged PR #387 remains the canonical item-animation implementation;
- PR #392 is closed unmerged and superseded by the broader canonical creature showcase in #395;
- PR #388 remains an old factual-source lifecycle closeout and should be reconciled/closed separately if still open.

These are repository-hygiene items, not missing atlas runtime functionality.

## Completion classification

Use the following classification in future continuation work:

```yaml
original_full_otbm_atlas:
  status: DONE
  full_world_certified: true
  floors: Z0..Z15
  chunks: 3494
  missing_sprites: 0
  bounded_browser_loading: true
  factual_layers: DONE
  canonical_environment_item_animation: DONE
  canonical_npc_sprite_overlays: DONE
  canonical_monster_sprite_overlays: DONE
  real_npc_monster_browser_showcase: DONE

expanded_animation_ambition:
  status: NOT_VERIFIED
  canonical_npc_walk_idle_animation: NOT_VERIFIED
  canonical_monster_walk_idle_animation: NOT_VERIFIED

visual_product_review:
  real_browser_evidence: DONE
  subjective_ux_parity_review: NOT_VERIFIED

next_action:
  name: Verify creature animation phases/directions on current main
  priority: P1
```

## Source-of-truth rule

Future agents must inspect current live `main`, active task records, open PRs and CI before acting. This document is a verified snapshot updated on 2026-08-15, not authority over newer repository state.

When evidence is incomplete, preserve `UNKNOWN` / `NOT VERIFIED` rather than filling the gap by inference.
