---
task_id: OTH-20260815-otbm-atlas-creature-sprites
status: ready
agent: ChatGPT
project_lane: otheryn-content
task_kind: implementation
phase: closeout
branch: feat/otbm-atlas-creature-sprites
base_branch: main
start_sha: eba09b461fdf7024704b602a5c6383ba447c4f72
created: 2026-08-15T00:16:59+02:00
updated: 2026-08-15T01:17:41+02:00
risk: high
related_pr: "395"
policy_version: 2
execution_mode: chat-github
execution_reason: GitHub-only repository execution is required because no local checkout/network is available; owner-funded Codex/API use is not authorized.
context_pressure: high
context_growth: stable
context_score: 11
estimate_confidence: high
decomposition_decision: phased
decomposition_reason: One cohesive atlas provenance/creature-sprite vertical slice spans parser, renderer, viewer, tests and E2E but shares one source contract and one PR.
validation_level: integrated
heavy_validation_runs: 2
session_rotation_count: 0
stale_takeover_count: 0
human_interruptions: 0
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-creature-showcase.yml
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-creature-sprites.md
---

# Canonical OTBM Atlas creature sprites

## Goal

Make the canonical OTBM Atlas use only `vendor/map-analysis/**` for map/item/creature provenance, migrate NPC outfit definitions to the vendored CrystalServer NPC corpus, add static canonical monster sprite parity through one shared creature renderer, preserve conservative unresolved dot fallbacks, and prove the vertical slice with real pinned-data and real Chromium evidence.

## Scope contract

- Map/spawns: `vendor/map-analysis/crystalserver/data-global/world/**`.
- Runtime map-composition evidence: `vendor/map-analysis/crystalserver/data-global/scripts/**`.
- NPC definitions: `vendor/map-analysis/crystalserver/data-global/npc/**`.
- Monster definitions: `vendor/map-analysis/crystalserver/data-global/monster/**`.
- Object/creature appearances and sprite sheets: `vendor/map-analysis/tibia-client/15.25.bd5a04/assets/**`.
- No canonical fallback to `data-otservbr-global/**` and no internet data import.
- Item renderer architecture is preserved; provenance is frozen by regression coverage.
- Creature animation/movement is outside this slice; output is static canonical outfit parity.
- Existing explicit `verifiedBossSpawns` evidence remains independent; no name/path heuristics.

## Acceptance inventory

- [x] Canonical item pipeline provenance is vendor-only and regression-tested.
- [x] NPC definitions are resolved from the vendored CrystalServer NPC tree with no non-vendor fallback.
- [x] Monster definitions are parsed from the real vendored Lua corpus with deterministic case-insensitive indexing and ambiguity handling.
- [x] NPC and monster sprites share one creature renderer/outfit model and deduplicate by outfit.
- [x] Both spawn kinds are enriched before `spawns.json` and spatial sharding.
- [x] `data/spawns.json` and spatial shards retain monster sprite fields.
- [x] Viewer renders NPC and monster sprites at close zoom, keeps low-zoom monster suppression and dot fallbacks.
- [x] Real pinned-data NPC, monster and item integration tests pass on validated head `a50f8450cc3c1f0a7cb487b289df488c2f13506c`.
- [x] Real Chromium creature showcase passes on validated head and uploads PNG + JSON evidence.
- [x] Required, CI, OTBM Atlas Tests, factual-layer workflows and environment-animation E2E pass on validated head.
- [x] Checkpoint-contract regression passes on the validated head containing the validator and checkpoint.
- [x] Final review-thread/mergeability audit passes and PR #395 is marked ready for review.

## Preflight evidence

- Live `main` at task start: `eba09b461fdf7024704b602a5c6383ba447c4f72` (merged PR #394 completion audit).
- PR #381 merged the canonical chunked atlas; its recorded implementation head is `1021d08978f078ff845e6f3f82fbbbc482cbf543`.
- PR #387 merged generalized item runtime animation; its recorded implementation head is `da553b1f2f157526e69e26d051ca3297db7abcf6`.
- PR #391 merged the real-browser showcase handoff; its recorded implementation head is `bbb5fceaf2c270c51f98ee50610c1fafceae5ecf`.
- PR #392 is closed unmerged. Its NPC-only evidence workflow is superseded by this PR's broader real NPC+monster showcase; no code from the closed branch is treated as canonical.
- PR #386 is an older item-animation alternative. This task does not reuse or modify that lane; merged PR #387 remains the canonical item-animation implementation.
- The prompt's `CREATURE_SOURCE_MANIFEST.json` spelling is not present on live `main`; repository truth is `vendor/map-analysis/crystalserver/creature-sources-manifest.json`.
- At preflight, `tools/otbm_atlas/atlas.py` defaulted creature scripts outside the vendored corpus and `tools/otbm_atlas/composition.py` read non-vendored runtime-map evidence. Both canonical leaks are removed on this branch and covered by regression tests.
- Existing item rendering takes the OTBM and Tibia asset roots supplied by `build_atlas`; production canonical entry points now hard-require the vendored world and Tibia asset roots.

## Validated implementation evidence

Exact validated head `a50f8450cc3c1f0a7cb487b289df488c2f13506c` passed:

- `node --check tools/otbm_atlas/viewer_app.js` plus `OTBM_ATLAS_CANONICAL_INTEGRATION=1 python3 -m unittest discover -s tools/otbm_atlas/tests -p 'test_*.py' -v`: 75 tests in 301.605 seconds, PASS.
- Real pinned NPC, monster and item integration tests: PASS.
- Checkpoint contract regression: PASS.
- Real Chromium resource/decode check and screenshot at zoom `0.8`: PASS; both selected creature sprites decoded as `64x64`.
- Showcase run `31849055061`, artifact `otbm-creature-showcase` ID `9237110993`, ZIP digest `sha256:7a529e4ef55d9fe9483a3f79154746645ff225da8ac3f96cc85391e5d5c346a7`.
- Downloaded artifact inspection confirms `evidence.json` plus `otbm-creature-showcase.png`; the screenshot is a real Chromium atlas frame over the canonical map region.
- Required run `31849055032`: PASS.
- CI run `31849055170`: PASS.
- OTBM Atlas Tests run `31849055019`: PASS.
- OTBM Environment Animation E2E run `31849055049`: PASS.
- Factual-layer audit/tests runs `31849054993` / `31849055037`: PASS.
- PR #395 has zero review threads, zero submitted reviews, is mergeable, is 0 commits behind `main`, and was moved out of draft after the green audit.

Pinned full-corpus creature statistics on that head:

- NPC sprites: 752 unique; 974 resolved spawns; 94 unresolved spawns; 8 ambiguous definitions.
- Monster sprites: 718 unique; 87097 resolved spawns; 468 unresolved spawns; 0 ambiguous definitions.
- Showcase NPC: `A Ghostly Knight`, lookType 134, source `vendor/map-analysis/crystalserver/data-global/npc/a_ghostly_knight.lua`, position `(32854,32327,11)`.
- Showcase monster: `Blightwalker`, lookType 246, source `vendor/map-analysis/crystalserver/data-global/monster/undeads/blightwalker.lua`, position `(32853,32328,11)`.
- Showcase bounds: `(32847..32860, 32321..32334, z=11)`; selected creatures are one tile apart and share one spatial shard.
- Source fingerprints: map `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`, appearances `aa44a154f30c7ed59acc25f246286396e4043851ef0b54ef3cf3951e46d1ce50`, catalog `93ea5888174ef44b352d7c2b1f8061573a4a260bfaba4b7ec32ea836b9e411ab`, creature source manifest `210b45eacf43ccee174c6bc4d025938889b8c92acb2d4d385c7235608bcc6268`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T01:17:41+02:00
head: a50f8450cc3c1f0a7cb487b289df488c2f13506c
branch: feat/otbm-atlas-creature-sprites
pr: 395
status: ready
context_routes:
  - tools/otbm_atlas
  - vendor/map-analysis/crystalserver/data-global/npc
  - vendor/map-analysis/crystalserver/data-global/monster
  - vendor/map-analysis/tibia-client/15.25.bd5a04/assets
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-creature-showcase.yml
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-creature-sprites.md
proven:
  - Live main at task start is eba09b461fdf7024704b602a5c6383ba447c4f72.
  - Canonical map/spawn root is vendor/map-analysis/crystalserver/data-global/world.
  - Canonical NPC definition root is vendor/map-analysis/crystalserver/data-global/npc.
  - Canonical monster definition root is vendor/map-analysis/crystalserver/data-global/monster.
  - Canonical object/creature appearance and sprite root is vendor/map-analysis/tibia-client/15.25.bd5a04/assets.
  - Shared CreatureSpriteRenderer owns static NPC and monster sprite extraction, mask recoloring, addon selection, bounded caches and outfit deduplication.
  - Exact validated head a50f8450cc3c1f0a7cb487b289df488c2f13506c passed 75 atlas/unit/pinned-data tests including the checkpoint contract regression.
  - Real Chromium run 31849055061 passed and decoded both NPC and monster sprite assets as 64x64 before screenshot capture.
  - Artifact 9237110993 contains evidence.json and otbm-creature-showcase.png and was directly inspected after download.
  - NPC corpus result is 752 unique sprites, 974 resolved spawns, 94 unresolved spawns, 8 ambiguous definitions.
  - Monster corpus result is 718 unique sprites, 87097 resolved spawns, 468 unresolved spawns, 0 ambiguous definitions.
  - Required, CI, Atlas Tests, environment-animation E2E and factual-layer checks all passed on head a50f8450cc3c1f0a7cb487b289df488c2f13506c.
  - PR 395 has zero review threads and reviews, is mergeable, is zero commits behind main and is ready for review.
derived:
  - One shared creature renderer plus thin NPC/monster parsers preserves the accepted NPC compatibility API without duplicate renderers.
  - Keeping unresolved records factual and sprite-free preserves the viewer dot fallback without inventing cross-datapack appearance data.
  - A same-shard pair one tile apart gives real browser evidence for both creature classes without loading the full world into Chromium.
unknown: []
conflicts: []
first_failure:
  marker: resolved-canonical-source-leak
  evidence: Preflight found non-vendored atlas defaults/runtime-map evidence; atlas.py and composition.py now use only vendor/map-analysis roots and test_atlas.py rejects runtime source regressions.
rejected_hypotheses:
  - Duplicate npc_sprites.py into a monster-only renderer; rejected because it duplicates mask/cache semantics and violates the shared-renderer contract.
  - Resolve missing creature data from data-otservbr-global or the network; rejected because unresolved must remain factual and source-isolated.
  - Treat a resource-timing entry alone as browser sprite proof; rejected because failed image requests can still create timing entries, so the showcase requires successful image decode and non-zero natural dimensions.
changed_paths:
  - .github/workflows/otbm-creature-showcase.yml
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-creature-sprites.md
  - tools/otbm_atlas/CREATURES.md
  - tools/otbm_atlas/README.md
  - tools/otbm_atlas/atlas.py
  - tools/otbm_atlas/composition.py
  - tools/otbm_atlas/creature_sprites.py
  - tools/otbm_atlas/monster_sprites.py
  - tools/otbm_atlas/npc_sprites.py
  - tools/otbm_atlas/tests/test_atlas.py
  - tools/otbm_atlas/tests/test_canonical_creatures.py
  - tools/otbm_atlas/tests/test_checkpoint_contract.py
  - tools/otbm_atlas/tests/test_composition.py
  - tools/otbm_atlas/tests/test_creature_sprites.py
  - tools/otbm_atlas/tests/test_monster_sprites.py
  - tools/otbm_atlas/tests/test_viewer.py
  - tools/otbm_atlas/viewer_app.js
validation:
  - command: node --check viewer_app.js plus full unittest discovery with OTBM_ATLAS_CANONICAL_INTEGRATION=1
    result: PASS
    evidence: Run 31849055061 on a50f8450cc3c1f0a7cb487b289df488c2f13506c ran 75 tests in 301.605s and completed OK.
  - command: real Chromium canonical creature showcase
    result: PASS
    evidence: Run 31849055061 decoded both selected 64x64 creature sprites, captured PNG, and uploaded artifact 9237110993.
  - command: Required
    result: PASS
    evidence: Run 31849055032 on a50f8450cc3c1f0a7cb487b289df488c2f13506c.
  - command: CI
    result: PASS
    evidence: Run 31849055170 on a50f8450cc3c1f0a7cb487b289df488c2f13506c.
  - command: OTBM Atlas Tests
    result: PASS
    evidence: Run 31849055019 on a50f8450cc3c1f0a7cb487b289df488c2f13506c.
  - command: OTBM Environment Animation E2E
    result: PASS
    evidence: Run 31849055049 built through production build_atlas with the canonical world/assets and passed both environment-animation jobs.
  - command: checkpoint contract regression
    result: PASS
    evidence: test_active_creature_task_checkpoint_matches_governance_contract passed in runs 31849055019 and 31849055061.
  - command: final PR review and mergeability audit
    result: PASS
    evidence: PR 395 has no review threads or submitted reviews, mergeable=true, behind main=0 and draft=false.
blockers: []
next_action: Merge PR 395 when branch-level checks on the closeout-metadata commit remain green; no implementation work remains.
```

## Recovery checkpoint

```yaml
last_durable_head: a50f8450cc3c1f0a7cb487b289df488c2f13506c
branch: feat/otbm-atlas-creature-sprites
phase: closeout
first_unmet_invariant: none in implementation; only the closeout metadata commit must retain green branch checks
next_action: verify final branch checks after this metadata update, then leave PR 395 merge-ready
```
