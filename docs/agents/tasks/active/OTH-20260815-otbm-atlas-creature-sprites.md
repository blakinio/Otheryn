---
task_id: OTH-20260815-otbm-atlas-creature-sprites
status: validating
agent: ChatGPT
project_lane: otheryn-content
task_kind: implementation
phase: validate
branch: feat/otbm-atlas-creature-sprites
base_branch: main
start_sha: eba09b461fdf7024704b602a5c6383ba447c4f72
created: 2026-08-15T00:16:59+02:00
updated: 2026-08-15T01:03:11+02:00
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
heavy_validation_runs: 1
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
- [x] Real pinned-data NPC, monster and item integration tests pass on validated implementation head `2b495896d96944d77d7085cae663d79f690c9f96`.
- [x] Real Chromium creature showcase passes on validated implementation head and uploads PNG + JSON evidence.
- [x] Required, CI, OTBM Atlas Tests, factual-layer workflows and environment-animation E2E pass on validated implementation head.
- [ ] New checkpoint-contract regression and all affected checks pass on the exact final head that contains this checkpoint update.
- [ ] Final review-thread/mergeability audit passes and PR #395 is marked ready for review.

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

Exact implementation head `2b495896d96944d77d7085cae663d79f690c9f96` passed:

- `node --check tools/otbm_atlas/viewer_app.js` plus `OTBM_ATLAS_CANONICAL_INTEGRATION=1 python3 -m unittest discover -s tools/otbm_atlas/tests -p 'test_*.py' -v`: 74 tests, PASS.
- Real pinned NPC, monster and item integration tests: PASS.
- Real Chromium resource/decode check and screenshot at zoom `0.8`: PASS; both selected creature sprites decoded as `64x64`.
- Showcase run `31848054084`, artifact `otbm-creature-showcase` ID `9236796551`, ZIP digest `sha256:594d4ace32c74797c3a341e234d65a253ea50d571f273e59e75507e6c58740e5`.
- Artifact inspection confirms PNG + JSON evidence and visibly rendered creature sprites over the canonical map fragment.
- Required run `31848054092`: PASS.
- CI run `31848054254`: PASS.
- OTBM Atlas Tests run `31848054142`: PASS.
- OTBM Environment Animation E2E run `31848054100`: PASS.
- Factual-layer tests/audit runs `31848054089` / `31848054098`: PASS.

Pinned full-corpus creature statistics on that head:

- NPC sprites: 752 unique; 974 resolved spawns; 94 unresolved spawns; 8 ambiguous definitions.
- Monster sprites: 718 unique; 87097 resolved spawns; 468 unresolved spawns; 0 ambiguous definitions.
- Showcase NPC: `A Ghostly Knight`, lookType 134, source `vendor/map-analysis/crystalserver/data-global/npc/a_ghostly_knight.lua`, position `(32854,32327,11)`.
- Showcase monster: `Blightwalker`, lookType 246, source `vendor/map-analysis/crystalserver/data-global/monster/undeads/blightwalker.lua`, position `(32853,32328,11)`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T01:03:11+02:00
head: 2b495896d96944d77d7085cae663d79f690c9f96
branch: feat/otbm-atlas-creature-sprites
pr: 395
status: validating
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
  - Shared CreatureSpriteRenderer owns static NPC and monster sprite extraction, mask recoloring, addon selection, cache bounds and deduplication.
  - Exact implementation head 2b495896d96944d77d7085cae663d79f690c9f96 passed 74 atlas/unit/pinned-data tests.
  - Real Chromium run 31848054084 passed and decoded both NPC and monster sprite assets as 64x64 before screenshot capture.
  - Artifact 9236796551 contains evidence.json and otbm-creature-showcase.png and was directly inspected after download.
  - NPC corpus result is 752 unique sprites, 974 resolved spawns, 94 unresolved spawns, 8 ambiguous definitions.
  - Monster corpus result is 718 unique sprites, 87097 resolved spawns, 468 unresolved spawns, 0 ambiguous definitions.
  - Required, CI, Atlas Tests, environment-animation E2E and factual-layer checks all passed on implementation head 2b495896d96944d77d7085cae663d79f690c9f96.
derived:
  - One shared creature renderer plus thin NPC/monster parsers is the smallest implementation preserving the accepted NPC compatibility API without duplicate renderers.
  - Keeping unresolved records factual and sprite-free preserves the viewer dot fallback without inventing cross-datapack appearance data.
  - A same-shard pair one tile apart gives real browser evidence for both creature classes without loading the full world into Chromium.
unknown:
  - Exact final-head validation result after adding the checkpoint-contract regression and this checkpoint update.
  - Final PR ready/mergeability state after exact-head checks and review-thread audit.
conflicts: []
first_failure:
  marker: resolved-canonical-source-leak
  evidence: Preflight found non-vendored atlas defaults/runtime-map evidence; atlas.py and composition.py now use only vendor/map-analysis roots and test_atlas.py rejects runtime source regressions.
rejected_hypotheses:
  - Duplicate npc_sprites.py into a monster-only renderer; rejected because it duplicates mask/cache semantics and violates the shared-renderer contract.
  - Resolve missing creature data from data-otservbr-global or the network; rejected because unresolved must remain factual and source-isolated.
  - Treat a resource-timing entry alone as browser sprite proof; rejected because failed image requests can still create timing entries, so the showcase now requires successful image decode and non-zero natural dimensions.
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
    evidence: Run 31848054084 on head 2b495896d96944d77d7085cae663d79f690c9f96 ran 74 tests in 298.920s and completed OK.
  - command: real Chromium canonical creature showcase
    result: PASS
    evidence: Run 31848054084 loaded and decoded both selected 64x64 creature sprites, captured PNG, and uploaded artifact 9236796551.
  - command: Required
    result: PASS
    evidence: Run 31848054092 on implementation head.
  - command: CI
    result: PASS
    evidence: Run 31848054254 on implementation head.
  - command: OTBM Atlas Tests
    result: PASS
    evidence: Run 31848054142 on implementation head.
  - command: checkpoint contract regression on the new exact head
    result: NOT_RUN
    evidence: Validator is introduced by the next durable commit and must be exercised by that commit's workflow run.
blockers: []
next_action: Run all affected workflows on the exact checkpoint-validator head, remediate any failure, perform a fresh final diff/review/mergeability audit, then mark PR 395 ready for review.
```

## Recovery checkpoint

```yaml
last_durable_head: 2b495896d96944d77d7085cae663d79f690c9f96
branch: feat/otbm-atlas-creature-sprites
phase: validate
first_unmet_invariant: exact final-head checkpoint-validator and PR-ready gates have not yet been exercised
next_action: validate the checkpoint/validator commit, repair any failure, audit final PR state and mark PR 395 ready
```
