# Full OTBM Atlas completion audit — 2026-08-14

This document records the verified completion state of the canonical OTBM Atlas after the full-world, animation and factual-layer work completed on 2026-08-14.

It is a state audit, not a replacement for the earlier product/UX handover in `docs/maps/otbm-atlas-conversation-handover-20260813.md`.

## Audit baseline

Repository: `blakinio/Otheryn`

Audited `main`:

`5013ca2ca7533b011d6a647f5869df22d42d6046`

Canonical CrystalServer revision:

`zimbadev/crystalserver@5e89bf8329ea406cb4ea8f4a18f32954f13e5418`

Canonical map:

`vendor/map-analysis/crystalserver/data-global/world/world.otbm`

Canonical Tibia assets:

`vendor/map-analysis/tibia-client/15.25.bd5a04/assets/`

Relevant merged delivery PRs include #371-#375, #378-#381, #383-#385, #387, #389-#391 and #393.

## Overall conclusion

### Original full-atlas contract

**DONE / VERIFIED.**

The original product contract for a complete canonical OTBM atlas is implemented: full-world preprocessing, bounded chunked browser loading, multi-resolution navigation, exact canonical detail rendering, persistent/shareable map state, factual overlays, conservative mechanics resolution and full-world release certification.

### Expanded later visual ambitions

**PARTIAL.**

Two later ambitions remain outside the completed original core contract:

1. human-viewable visual/showcase certification of the production viewer against the Oteryn Thais/TibiaMaps/TibiaRoute UX direction;
2. full canonical animated creature overlays for NPCs and monsters, including creature animation phases/directions rather than static canonical outfit markers.

Neither item invalidates the completed full-world atlas core.

## Requirement-by-requirement audit

| Requirement | Status | Verified state |
|---|---|---|
| Canonical CrystalServer `world.otbm` | DONE | Exact pinned map is vendored and used as the atlas source of truth. |
| Canonical client assets | DONE | Owner-selected Tibia 15.25 assets are vendored and fingerprinted. |
| Complete world support | DONE | All populated `Z=0..15` are supported. |
| No whole-world browser load | DONE | Viewer uses spatial chunks, viewport loading/prefetch and bounded caches. |
| Full-world release certification | DONE | Canonical release run completed all 16 floors and exactly 3494 chunks. |
| Full-world source consistency | DONE | Aggregate release validation records one canonical source fingerprint/map SHA. |
| Missing sprites | DONE | Full-world release certification records `missingSprites == {}` for every floor. |
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
| NPC canonical outfit sprites | DONE | Canonical outfit markers are rendered when a definition is resolvable; uncertain cases retain conservative fallback behavior. |
| Monster spawn layer | DONE | Canonical CrystalServer spawn positions are available as factual overlay data. |
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
| Full animated NPC walking/idle overlays | MISSING / LATER AMBITION | Current verified NPC renderer is a canonical outfit-marker renderer; no evidence proves a complete creature movement/idle animation pipeline in the atlas. |
| Full animated monster overlays | MISSING / LATER AMBITION | Spawn data is complete, but a complete canonical creature animation overlay renderer is not verified. |
| Human-viewable production showcase | PARTIAL | Real browser E2E exists; a dedicated canonical Thais showcase/evidence PR remains open. |

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

The former full-world-final-gate exception is therefore closed and must not be reported as outstanding.

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

## Animation completion boundary

The production environment/item animation pipeline is complete for its documented conservative contract.

Merged PR #387 generalizes runtime cyclic object animation while preserving:

- canonical shift/height displacement;
- safe underlay/phase/overlay composition;
- bounded per-instance browser behavior;
- deterministic static fallback for unsafe/unsupported cases;
- no inferred server-driven appearance state.

This must not be conflated with full animated creature overlays. NPC canonical outfit markers were delivered separately by PR #378. A static/canonical outfit marker does not prove a complete creature walk/idle animation implementation.

## Remaining work outside the original core contract

### P1 — canonical animated creature overlays

Recommended next feature slice:

**Animated Creature Overlays — NPC + Monsters**

Required properties:

- resolve creature appearances from the already pinned/vendored canonical sources;
- use canonical creature animation phases and direction semantics rather than generated/mock animation;
- preserve conservative fallback when a creature appearance or phase cannot be proven;
- remain viewport/chunk bounded;
- keep bounded image/animation caches;
- avoid world-wide creature payloads at browser startup;
- retain spawn/source provenance;
- add real Chromium E2E for at least one canonical NPC and one canonical monster;
- add a human-viewable browser capture generated from the real production viewer.

### P2 — visual UX/showcase certification

Open PR #392 is evidence-only and generates a real canonical Thais NPC showcase from the production viewer.

This is not a missing atlas rendering feature, but it is useful to close the visual evidence gap and assess the production UI against the Oteryn Thais prototype and TibiaMaps/TibiaRoute browsing direction.

Do not call subjective visual parity proven until the actual artifact has been inspected.

## Repository hygiene noted by this audit

The following open PRs are not missing core atlas functionality but should be reconciled/closed deliberately:

- PR #386: older runtime-animation work, functionally superseded by merged PR #387;
- PR #388: lifecycle closeout for the already merged factual-source producer #385;
- PR #392: current real Thais NPC showcase/evidence work.

Do not merge #386 merely because it remains open; compare it to current `main` and close it as superseded if no unique required work remains.

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

expanded_visual_ambition:
  status: PARTIAL
  canonical_animated_npc_overlays: MISSING
  canonical_animated_monster_overlays: MISSING
  human_viewable_showcase_certification: PARTIAL

next_feature:
  name: Animated Creature Overlays — NPC + Monsters
  priority: P1
```

## Source-of-truth rule

Future agents must still inspect current live `main`, active task records, open PRs and CI before acting. This document is a verified 2026-08-14 snapshot, not authority over newer repository state.

When evidence is incomplete, preserve `UNKNOWN` rather than filling the gap by inference.
