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
updated: 2026-08-15T01:39:00+02:00
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
heavy_validation_runs: 3
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
- [x] Apostrophes inside canonical double-quoted monster names are preserved and covered by synthetic plus pinned-data regressions.
- [x] NPC and monster sprites share one creature renderer/outfit model and deduplicate by outfit.
- [x] Both spawn kinds are enriched before `spawns.json` and spatial sharding.
- [x] `data/spawns.json` and spatial shards retain monster sprite fields.
- [x] Viewer renders NPC and monster sprites at close zoom, keeps low-zoom monster suppression and dot fallbacks.
- [x] Real pinned-data NPC, monster and item integration tests pass on validated implementation head `65b09091b3b819be54b4451869ae0fc4e86d0726`.
- [x] Real Chromium creature showcase passes and uploads PNG + JSON evidence.
- [x] Vendor-only canonical input changes trigger the pinned-data/Chromium showcase workflow.
- [x] Required, CI, OTBM Atlas Tests, factual-layer workflows and environment-animation E2E pass on the validated implementation head.
- [x] Checkpoint-contract regression passes on the validated implementation head.
- [x] Both review findings were fixed with regressions and their review threads were resolved after green exact-head validation.

## Preflight evidence

- Live `main` at task start: `eba09b461fdf7024704b602a5c6383ba447c4f72` (merged PR #394 completion audit).
- PR #381 merged the canonical chunked atlas; recorded implementation head `1021d08978f078ff845e6f3f82fbbbc482cbf543`.
- PR #387 merged generalized item runtime animation; recorded implementation head `da553b1f2f157526e69e26d051ca3297db7abcf6`.
- PR #391 merged the real-browser showcase handoff; recorded implementation head `bbb5fceaf2c270c51f98ee50610c1fafceae5ecf`.
- PR #392 is closed unmerged. Its NPC-only evidence workflow is superseded by this PR's broader real NPC+monster showcase; no code from the closed branch is treated as canonical.
- PR #386 is an older item-animation alternative. This task does not reuse or modify that lane; merged PR #387 remains the canonical item-animation implementation.
- Repository truth is `vendor/map-analysis/crystalserver/creature-sources-manifest.json`; the differently-cased path from the task prompt does not exist on live `main`.
- Preflight found canonical leaks in prior atlas defaults/runtime-map evidence. `atlas.py` and `composition.py` now use only `vendor/map-analysis` roots and the regression suite rejects canonical runtime references to `data-otservbr-global`.

## Final validated implementation evidence

Exact implementation head `65b09091b3b819be54b4451869ae0fc4e86d0726` passed:

- `node --check tools/otbm_atlas/viewer_app.js` plus `OTBM_ATLAS_CANONICAL_INTEGRATION=1 python3 -m unittest discover -s tools/otbm_atlas/tests -p 'test_*.py' -v`: 77 tests in 297.942 seconds, PASS.
- Real pinned NPC, monster, apostrophe-name monster, and item integration tests: PASS.
- Real Chromium resource/decode check and screenshot at zoom `0.8`: PASS; selected NPC and monster sprites both decoded as `64x64` before capture.
- Showcase run `31850386979`, artifact `otbm-creature-showcase` ID `9237507859`, ZIP digest `sha256:71c2bba900f24ee24b8f258d7bde632d2d9045684195ed299edc52bf86bf3ad1`.
- Downloaded artifact inspection confirms exactly `evidence.json` plus `otbm-creature-showcase.png`; the PNG was visually inspected and is a real Chromium atlas frame over the canonical map region.
- Required `31850386749`: PASS.
- CI `31850387014`: PASS.
- OTBM Atlas Tests `31850386888`: PASS.
- OTBM Environment Animation E2E `31850386791`: PASS.
- Factual-layer tests/audit `31850386925` / `31850386819`: PASS.
- Review finding for apostrophes recovered exactly 96 monster spawns compared with the pre-fix corpus result; regression covers real `Mooh'Tah Warrior`.
- Review finding for workflow coverage is fixed by including the consumed vendored world, NPC, monster, scripts, manifest and Tibia asset roots in the showcase trigger.
- Both review threads are resolved after the implementation head passed all relevant checks.

Pinned full-corpus creature statistics:

- NPC sprites: 752 unique; 974 resolved spawns; 94 unresolved spawns; 8 ambiguous definitions.
- Monster sprites: 719 unique; 87193 resolved spawns; 372 unresolved spawns; 0 ambiguous definitions.
- Showcase NPC: `A Ghostly Knight`, lookType 134, source `vendor/map-analysis/crystalserver/data-global/npc/a_ghostly_knight.lua`, position `(32854,32327,11)`.
- Showcase monster: `Blightwalker`, lookType 246, source `vendor/map-analysis/crystalserver/data-global/monster/undeads/blightwalker.lua`, position `(32853,32328,11)`.
- Showcase bounds: `(32847..32860, 32321..32334, z=11)`; selected creatures are one tile apart and share one spatial shard.
- Source fingerprints: map `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`, appearances `aa44a154f30c7ed59acc25f246286396e4043851ef0b54ef3cf3951e46d1ce50`, catalog `93ea5888174ef44b352d7c2b1f8061573a4a260bfaba4b7ec32ea836b9e411ab`, creature source manifest `210b45eacf43ccee174c6bc4d025938889b8c92acb2d4d385c7235608bcc6268`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T01:39:00+02:00
head: 65b09091b3b819be54b4451869ae0fc4e86d0726
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
  - Canonical map/spawn root is vendor/map-analysis/crystalserver/data-global/world.
  - Canonical NPC definition root is vendor/map-analysis/crystalserver/data-global/npc.
  - Canonical monster definition root is vendor/map-analysis/crystalserver/data-global/monster.
  - Canonical object/creature appearance and sprite root is vendor/map-analysis/tibia-client/15.25.bd5a04/assets.
  - Shared CreatureSpriteRenderer owns static NPC and monster sprite extraction, mask recoloring, addon selection, bounded caches and outfit deduplication.
  - Exact implementation head 65b09091b3b819be54b4451869ae0fc4e86d0726 passed 77 atlas/unit/pinned-data tests including the real apostrophe-name regression and checkpoint contract.
  - Real Chromium run 31850386979 passed and decoded both NPC and monster sprite assets as 64x64 before screenshot capture.
  - Artifact 9237507859 contains evidence.json and otbm-creature-showcase.png and was directly inspected after download.
  - NPC corpus result is 752 unique sprites, 974 resolved spawns, 94 unresolved spawns, 8 ambiguous definitions.
  - Monster corpus result is 719 unique sprites, 87193 resolved spawns, 372 unresolved spawns, 0 ambiguous definitions.
  - Required, CI, Atlas Tests, environment-animation E2E and factual-layer checks all passed on implementation head 65b09091b3b819be54b4451869ae0fc4e86d0726.
  - Both review findings were fixed with regressions and both review threads were resolved after exact-head validation.
derived:
  - One shared creature renderer plus thin NPC/monster parsers preserves the accepted NPC compatibility API without duplicate renderers.
  - Keeping unresolved records factual and sprite-free preserves the viewer dot fallback without inventing cross-datapack appearance data.
  - A same-shard pair one tile apart gives real browser evidence for both creature classes without loading the full world into Chromium.
unknown: []
conflicts: []
first_failure:
  marker: resolved-review-apostrophe-parser
  evidence: Review found apostrophes inside double-quoted canonical monster names were truncated; delimiter-aware parsing plus synthetic and real pinned-data tests recovered 96 spawns.
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
    evidence: Run 31850386979 on implementation head ran 77 tests in 297.942s and completed OK.
  - command: real Chromium canonical creature showcase
    result: PASS
    evidence: Run 31850386979 decoded both selected 64x64 creature sprites, captured PNG, and uploaded artifact 9237507859.
  - command: Required
    result: PASS
    evidence: Run 31850386749 on implementation head.
  - command: CI
    result: PASS
    evidence: Run 31850387014 on implementation head.
  - command: OTBM Atlas Tests
    result: PASS
    evidence: Run 31850386888 on implementation head.
  - command: OTBM Environment Animation E2E
    result: PASS
    evidence: Run 31850386791 on implementation head.
  - command: checkpoint contract regression
    result: PASS
    evidence: test_active_creature_task_checkpoint_matches_governance_contract passed on implementation head.
  - command: review remediation audit
    result: PASS
    evidence: Both P2 review threads were fixed, covered by regression evidence, and resolved only after implementation-head workflows were green.
blockers: []
next_action: Verify the final metadata-only closeout commit retains green PR checks and zero unresolved review threads, then leave PR 395 merge-ready.
```

## Recovery checkpoint

```yaml
last_durable_head: 65b09091b3b819be54b4451869ae0fc4e86d0726
branch: feat/otbm-atlas-creature-sprites
phase: closeout
first_unmet_invariant: none in implementation; only final metadata-only check freshness remains
next_action: verify final PR checks and review hygiene, then leave PR 395 merge-ready
```
