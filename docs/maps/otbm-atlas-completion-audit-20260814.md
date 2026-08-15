# Full OTBM Atlas completion audit — final technical closeout 2026-08-15

This document records the verified completion state of the canonical OTBM Atlas after full-world certification, factual layers, environment animation, canonical creature sprites and canonical creature phase animation.

It remains separate from the product/UX direction in `docs/maps/otbm-atlas-conversation-handover-20260813.md`: automated evidence can prove implementation and runtime behavior, but not a human's subjective visual preference.

## Audit baseline

Repository: `blakinio/Otheryn`

Verified merged `main` after creature-animation delivery:

`ffc839a02921caf52077c87d91247d92466afae3`

Canonical CrystalServer revision:

`zimbadev/crystalserver@5e89bf8329ea406cb4ea8f4a18f32954f13e5418`

Canonical map:

`vendor/map-analysis/crystalserver/data-global/world/world.otbm`

Canonical Tibia assets:

`vendor/map-analysis/tibia-client/15.25.bd5a04/assets/`

Relevant merged atlas delivery PRs include #371-#375, #378-#381, #383-#385, #387, #389-#391, #393-#399.

## Overall conclusion

### Original full-atlas contract

**DONE / VERIFIED.**

The canonical full-world atlas contract is implemented: full-world preprocessing, bounded chunked browser loading, multi-resolution navigation, exact canonical detail rendering, persistent/shareable map state, factual overlays, conservative mechanics resolution and full-world release certification.

### Canonical environment/item animation

**DONE / VERIFIED.**

The production environment animation pipeline supports bounded cyclic canonical animation, including displaced/larger supported geometry, with conservative static fallback and without inferring unknown server-driven state.

### Canonical creature static sprite parity

**DONE / VERIFIED.**

NPC and monster overlays use the shared bounded canonical creature renderer against pinned CrystalServer definitions plus pinned Tibia appearances/sprite sheets. Static unresolved/unsupported cases retain conservative fallback.

### Canonical creature time-based animation

**DONE / VERIFIED.**

PR #399 (`feat(atlas): animate canonical creature overlays`) was squash-merged as:

`ffc839a02921caf52077c87d91247d92466afae3`

The implementation preserves canonical creature frame-group identity, supports canonical cardinal direction patterns for supported outfits, exports all renderable phases while preserving recolouring/addons, honors canonical timing metadata conservatively, stays viewport/cache bounded, and never simulates creature path movement.

Real pinned-data Chromium E2E proves phase changes over time for both an NPC and a monster in the production viewer.

### Subjective visual/product parity

**OWNER/HUMAN REVIEW PENDING.**

Real production browser evidence exists. Whether the final visual/interaction result matches the desired Oteryn Thais / TibiaMaps / TibiaRoute direction closely enough is a subjective product-acceptance decision and is intentionally not inferred from automation.

This is not a missing technical atlas runtime capability.

## Requirement-by-requirement audit

| Requirement | Status | Verified state |
|---|---|---|
| Canonical CrystalServer `world.otbm` | DONE | Exact pinned map is vendored and used as source of truth. |
| Canonical client assets | DONE | Owner-selected Tibia 15.25 assets are vendored and fingerprinted. |
| Complete world support | DONE | All populated `Z=0..15` are supported. |
| No whole-world browser load | DONE | Viewer uses spatial chunks, viewport loading/prefetch and bounded caches. |
| Full-world release certification | DONE | All 16 floors and exactly 3494 chunks passed canonical release validation. |
| Missing sprites in certified world render | DONE | `missingSprites == {}` for every certified floor. |
| Low/medium-zoom overview | DONE | Lightweight derived overview imagery is available. |
| Maximum/detail canonical sprite render | DONE | Detail mode uses pinned canonical OTBM + client assets. |
| Auto / Detailed / Performance modes | DONE | All three modes are first-class and preserve bounded loading. |
| X/Y/Z, zoom and URL state | DONE | Coordinates, zoom, render mode and layers are restorable/shareable. |
| NPC spawn layer | DONE | Canonical spawn positions and provenance are available. |
| Monster spawn layer | DONE | Canonical spawn positions and provenance are available. |
| Canonical NPC sprites | DONE | Pinned canonical appearance/sprite data with conservative fallback. |
| Canonical monster sprites | DONE | Pinned canonical appearance/sprite data with conservative fallback. |
| Canonical NPC animation phases | DONE | Time-based canonical phase playback proven in production Chromium E2E. |
| Canonical monster animation phases | DONE | Time-based canonical phase playback proven in production Chromium E2E. |
| Creature frame-group semantics | DONE | Idle/moving frame-group identity is preserved instead of flattened. |
| Creature cardinal direction semantics | DONE | Supported N/E/S/W canonical patterns are exported; unsupported geometry is not guessed. |
| Creature animation timing | DONE | Default start, synchronization, random-start and loop metadata are handled conservatively. |
| Creature animation boundedness | DONE | Visible-chunk runtime, bounded LRUs, no whole-world creature animation preload. |
| Creature spatial truth | DONE | Animation never mutates factual spawn positions or simulates pathing. |
| Creature source contract | DONE | Canonical creature inputs remain restricted to `vendor/map-analysis/**`; no network or `data-otservbr-global` visual fallback. |
| Verified boss layer | DONE | Requires explicit resolved `rewardBoss=true`. |
| Direct OTBM teleports | DONE | Kept distinct from scripted transition evidence. |
| Scripted mechanics/teleports | DONE | Only proven static resolved transitions become navigable truth. |
| AID / UID | DONE | Indexed with conservative resolution states. |
| Houses / house doors / towns / waypoints | DONE | Available as factual map/world records. |
| Raids/events | DONE | Point spawns and exact rectangular areas are exposed. |
| NPC shop/bank/guild-bank/travel services | DONE | Resolved from pinned definitions/helper semantics. |
| Search/details factual integration | DONE | Factual layers participate in viewer search/details and URL-preserved layers. |
| UNKNOWN/UNRESOLVED/AMBIGUOUS handling | DONE | Uncertain evidence is never silently promoted to certain spatial truth. |
| Environment/item cyclic animation | DONE | Production runtime animation with bounded conservative contract. |
| Real NPC + monster static browser showcase | DONE | Real production Chromium evidence exists. |
| Real NPC + monster time-based browser E2E | DONE | Exact-head creature-animation workflow proves distinct phases over time. |
| Subjective visual parity | OWNER REVIEW | Requires human visual/product acceptance. |

## Full-world certification evidence

PR #389 archives successful full-world release validation for implementation SHA:

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

The former full-world-final-gate exception is closed.

## Factual-layer evidence

PR #385 merged the deterministic conservative factual-source producer as:

`2cf8035401a05873c307af7388872141a76309ef`

PR #390 then consumed the producer in the canonical production atlas and was squash-merged as:

`2bfacdd8349003aaa9675604269b8ae8004c19a6`

Verified behavior includes proven static scripted transitions, raid/event geometry, explicit reward-boss truth, NPC services, conservative uncertainty states, spatial chunking, search/details integration and URL-preserved factual layers.

The formerly stale task `OTH-20260814-atlas-factual-source-index` is now archived. Historical closeout PR #388 was closed as superseded because the production consumer has long since merged and the terminal archive is consolidated with this final closeout.

## Supplemental-source evidence

PR #383 was merged as:

`80e07b9afece08506c1fe401f20df073c93833f1`

Pinned source trees:

- scripts: `0e3b0102c7d841345dc5b9d4a3b81631930dc362`;
- raids: `95da7008cf26e5b41ad9f6ef6b5666707feb295c`;
- NPC system: `8c95fc6faf1dc2c6c573cb57973838897a458a28`.

The deterministic manifest records 2054 files, 3,285,973 bytes and fingerprint:

`c599e44454b3cd2ec0378f2b1ba296f0858db2f9c683d60ec1da19ffdc672f92`

The stale supplemental-source task is now archived; its historical review findings concerned checkpoint/lifecycle metadata rather than source integrity.

## Canonical static creature sprite evidence

PR #395 was squash-merged as:

`ea1810ed0a878230d1e68ad45e455c01ef7fc99d`

Pinned corpus results recorded by #395:

- NPC: 752 unique sprites, 974 resolved spawns, 94 unresolved, 8 ambiguous definitions;
- monsters: 719 unique sprites, 87,193 resolved spawns, 372 unresolved, 0 ambiguous definitions.

These unresolved records remain explicit fallback/evidence states; they are not silently guessed.

PR #397 later revalidated the archived static-creature lifecycle and showcase and was merged as:

`16e740adbf73757523795873c1106517e86dbe35`

## Canonical creature animation evidence

PR #399 final implementation head:

`c6b1bc6acafcf52c376bd2095ab8e7dd938c2d35`

Squash merge:

`ffc839a02921caf52077c87d91247d92466afae3`

All final-head pull-request workflows completed SUCCESS:

- Required `31878003609`;
- CI `31878003676`;
- autofix.ci `31878003610`;
- OTBM Atlas Tests `31878003687`;
- OTBM Canonical Creature Showcase `31878003689`;
- OTBM Environment Animation E2E `31878003600`;
- OTBM Creature Animation E2E `31878003617`;
- OTBM Creature Animation Audit `31878003672`;
- OTBM Atlas Factual Layer Audit `31878003660`;
- OTBM Atlas Factual Layers `31878003597`.

Independent creature-animation audit result: **PASS, material findings = 0**.

Pinned audit examples:

- NPC `Tanyt`, lookType `1199`: 8 canonical phases, 300 ms each, N/E/S/W;
- monster `Silver Rabbit`, lookType `262`: 8 canonical phases, 300 ms each, N/E/S/W.

The browser runtime uses bounded image, shard, descriptor and per-spawn start-clock caches. For asynchronous animations with `randomStartPhase=false`, playback begins from the canonical default start using a bounded first-seen clock; deterministic per-spawn offset is applied only when canonical metadata permits random start.

The implementation explicitly does **not** change `record.position` and does not present animation as actual server movement.

## Historical Thais counting note

The earlier product handover records a historical counting difference of 15,037 child items versus 14,993 in a newer semantic parser for a Thais slice.

No later repository evidence proves that those two values use an identical counting definition. Therefore this audit does not force them to equality or invent a correction. The certified full-world render, canonical source fingerprints and zero-missing-sprite release gates are independent of that historical counter-definition discrepancy.

Treat it as a documented historical measurement-definition difference unless a future task explicitly proves otherwise.

## Repository hygiene after final closeout

Final-closeout intent:

- PR #399: merged and canonical;
- PR #388: closed superseded;
- `OTH-20260815-otbm-atlas-creature-animation`: archived;
- `OTH-20260814-atlas-factual-source-index`: archived;
- `OTH-20260814-atlas-supplemental-sources`: archived;
- no atlas runtime implementation task above remains falsely active.

## Completion classification

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
  canonical_npc_phase_animation: DONE
  canonical_monster_phase_animation: DONE
  creature_direction_phase_semantics: VERIFIED
  creature_runtime_boundedness: VERIFIED
  real_creature_animation_chromium_e2e: PASS

technical_completion:
  status: DONE
  known_material_findings: 0
  stale_atlas_runtime_tasks: 0
  stale_atlas_closeout_prs: 0

visual_product_review:
  real_browser_evidence: DONE
  subjective_ux_parity_review: OWNER_REVIEW_PENDING
```

## Source-of-truth rule

Future agents must inspect live `main`, active task records, open PRs and CI before acting. This document is the final technical closeout snapshot for the atlas state reached on 2026-08-15.

When evidence is incomplete, preserve `UNKNOWN` / `NOT VERIFIED`; do not fill gaps by inference.
