---
task_id: OTH-20260815-otbm-atlas-creature-sprites
status: implementing
agent: ChatGPT
project_lane: otheryn-content
task_kind: implementation
phase: implement
branch: feat/otbm-atlas-creature-sprites
base_branch: main
start_sha: eba09b461fdf7024704b602a5c6383ba447c4f72
created: 2026-08-15T00:16:59+02:00
updated: 2026-08-15T00:16:59+02:00
risk: high
related_pr: null
policy_version: 2
execution_mode: chat-github
execution_reason: GitHub-only repository execution is required because no local checkout/network is available; owner-funded Codex/API use is not authorized.
context_pressure: high
context_growth: stable
context_score: 11
estimate_confidence: high
decomposition_decision: phased
decomposition_reason: One cohesive atlas provenance/creature-sprite vertical slice spans parser, renderer, viewer, tests and E2E but shares one source contract and one PR.
validation_level: focused
heavy_validation_runs: 0
session_rotation_count: 0
stale_takeover_count: 0
human_interruptions: 0
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-creature-showcase.yml
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-creature-sprites.md
  - tools/otbm_atlas/README.md
  - tools/otbm_atlas/ANIMATION.md
---

# Canonical OTBM Atlas creature sprites

## Goal

Make the canonical OTBM Atlas use only `vendor/map-analysis/**` for map/item/creature provenance, migrate NPC outfit definitions to the vendored CrystalServer NPC corpus, add static canonical monster sprite parity through one shared creature renderer, preserve conservative unresolved dot fallbacks, and prove the vertical slice with real pinned-data and real Chromium evidence.

## Scope contract

- Map/spawns: `vendor/map-analysis/crystalserver/data-global/world/**`.
- NPC definitions: `vendor/map-analysis/crystalserver/data-global/npc/**`.
- Monster definitions: `vendor/map-analysis/crystalserver/data-global/monster/**`.
- Object/creature appearances and sprite sheets: `vendor/map-analysis/tibia-client/15.25.bd5a04/assets/**`.
- No canonical fallback to `data-otservbr-global/**` and no internet data import.
- Item renderer architecture is preserved; provenance is frozen by regression coverage.
- Creature animation/movement is outside this slice; output is static canonical outfit parity.
- Existing explicit `verifiedBossSpawns` evidence remains independent; no name/path heuristics.

## Acceptance inventory

- [ ] Canonical item pipeline provenance is vendor-only and regression-tested.
- [ ] NPC definitions are resolved from the vendored CrystalServer NPC tree with no non-vendor fallback.
- [ ] Monster definitions are parsed from the real vendored Lua corpus with deterministic case-insensitive indexing and ambiguity handling.
- [ ] NPC and monster sprites share one creature renderer/outfit model and deduplicate by outfit.
- [ ] Both spawn kinds are enriched before `spawns.json` and spatial sharding.
- [ ] `data/spawns.json` and spatial shards retain monster sprite fields.
- [ ] Viewer renders NPC and monster sprites at close zoom, keeps low-zoom monster suppression and dot fallbacks.
- [ ] Real pinned-data NPC, monster and item integration tests pass.
- [ ] Real Chromium creature showcase passes and uploads PNG + JSON evidence.
- [ ] Focused/unit/component tests, Required/CI, review threads and checkpoint validation pass on the exact final head.

## Preflight evidence

- Live `main` at task start: `eba09b461fdf7024704b602a5c6383ba447c4f72` (merged PR #394 completion audit).
- PR #381 merged canonical chunked atlas as `1021d08978f078ff845e6f3f82fbbbc482cbf543`.
- PR #387 merged generalized item runtime animation as `da553b1f2f157526e69e26d051ca3297db7abcf6`.
- PR #391 merged the real-browser showcase handoff as `bbb5fceaf2c270c51f98ee50610c1fafceae5ecf`.
- PR #392 remains open and owns only `.github/workflows/otbm-thais-npc-showcase.yml`; this task will not edit that path and will provide broader NPC+monster evidence under a distinct workflow.
- PR #386 is the older item-animation alternative already superseded by merged #387; this task does not reuse it.
- The prompt's `CREATURE_SOURCE_MANIFEST.json` spelling is not present on live `main`; repository truth is `vendor/map-analysis/crystalserver/creature-sources-manifest.json`.
- `tools/otbm_atlas/atlas.py` currently defaults creature scripts to `data-otservbr-global`; `tools/otbm_atlas/README.md` still documents that NPC source. These are the canonical source leaks owned by this task.
- Existing item rendering takes only the supplied OTBM and Tibia asset roots; production docs/commands already point map/assets at the vendored corpus.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-14T22:16:59Z
head: eba09b461fdf7024704b602a5c6383ba447c4f72
branch: feat/otbm-atlas-creature-sprites
pr: none
status: implementing
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
  - Live main is eba09b461fdf7024704b602a5c6383ba447c4f72.
  - Current atlas build defaults NPC definitions to data-otservbr-global and has no monster sprite enrichment.
  - Current item renderer and environment animation consume caller-supplied canonical map/assets and the documented production commands use vendor/map-analysis roots.
  - Real vendored Demon definition uses Game.createMonsterType("Demon") and monster.outfit with lookType 35 and explicit colour/addon fields.
  - Real vendored Benjamin definition uses internalNpcName "Benjamin" and npcConfig.outfit lookType 128 with colour fields.
derived:
  - A shared creature renderer plus thin NPC/monster definition layers is the smallest architecture that preserves compatibility without duplicate renderers.
unknown:
  - Final pinned-corpus resolution counts until exact-head integration runs.
  - Final showcase NPC/monster pair until the workflow selects a real co-located region.
conflicts: []
first_failure:
  marker: canonical NPC definition root points outside vendor/map-analysis
  evidence: tools/otbm_atlas/atlas.py build_atlas scripts_dir default is data-otservbr-global
rejected_hypotheses:
  - duplicate npc_sprites.py into a monster-only renderer: violates the shared creature renderer requirement and duplicates mask/cache semantics.
changed_paths:
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-creature-sprites.md
validation:
  - command: preflight live main/governance/PR/source audit
    result: PASS
    evidence: GitHub connector reads on eba09b461fdf7024704b602a5c6383ba447c4f72; PR #392 overlap isolated to its showcase workflow.
blockers: []
next_action: Implement the shared creature renderer and vendored NPC/monster definition indexes, then wire both enrichments before spatial sharding.
```

## Recovery checkpoint

```yaml
last_durable_head: eba09b461fdf7024704b602a5c6383ba447c4f72
branch: feat/otbm-atlas-creature-sprites
phase: implement
first_unmet_invariant: canonical NPC definitions still default to data-otservbr-global
next_action: add shared creature_sprites.py, thin NPC/monster parsers, and atlas vendor-root wiring before running focused tests
```
