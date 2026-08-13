---
task_id: OTH-20260813-atlas-npc-sprites
status: validating
branch: codex/atlas-npc-sprites
base_branch: main
created: 2026-08-13
updated: 2026-08-13
related_pr: ""
owned_paths:
  - tools/otbm_atlas/**
  - docs/agents/tasks/active/OTH-20260813-atlas-npc-sprites.md
required_reads:
  - AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
search_first: []
optional_reads: []
---

# Canonical NPC sprites in the OTBM atlas

## Goal

Replace NPC overlay dots with lazy-loaded canonical creature outfit sprites at
useful zoom levels, retaining dots when an authoritative sprite cannot be made.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-13T17:50:00+02:00
head: pending
branch: codex/atlas-npc-sprites
pr: none
status: validating
context_routes:
  - tools/otbm_atlas/README.md
  - data-otservbr-global/npc
  - vendor/map-analysis/tibia-client/15.25.bd5a04/assets
owned_paths:
  - tools/otbm_atlas/**
  - docs/agents/tasks/active/OTH-20260813-atlas-npc-sprites.md
proven:
  - 919 NPC spawns resolve to 717 deduplicated canonical outfit PNGs
  - 149 unresolvable or conflicting definitions deliberately remain dots
  - Thais spatial shards contain canonical sprite references for 32 NPC spawns
derived: []
unknown:
  - visual performance on owner hardware
conflicts: []
first_failure:
  marker: duplicate NPC name with conflicting outfit definitions
  evidence: A Dead Bureaucrat appears with multiple explicit definitions; ambiguous names are left unresolved
rejected_hypotheses:
  - choose an arbitrary script for duplicate NPC names
changed_paths:
  - tools/otbm_atlas/**
validation:
  - command: node --check tools/otbm_atlas/viewer_app.js; python -m unittest discover -s tools/otbm_atlas/tests -v
    result: PASS
    evidence: 37 tests pass
  - command: python -m tools.otbm_atlas.verify build/full-map-atlas
    result: PASS
    evidence: 3494 chunks verified with no errors
blockers: []
next_action: commit, open PR, and run exact-head CI
```
