---
task_id: OTH-20260813-atlas-npc-sprites
status: completed
owner: none
branch: main
base_branch: main
created: 2026-08-13
updated: 2026-08-13
completed: 2026-08-13T18:24:12+02:00
related_pr: "378"
ownership_released: true
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
updated_at: 2026-08-13T18:24:12+02:00
head: aae10e8c6f54b4517dfbfcc9e6bf8b70e38715c4
delivery_head: 5ced50ccc3df37b0f06b4c43d68cdece3ddad695
branch: main
pr: 378
status: completed
context_routes:
  - tools/otbm_atlas/README.md
  - data-otservbr-global/npc
  - vendor/map-analysis/tibia-client/15.25.bd5a04/assets
owned_paths: []
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
next_action: no further action; task is archived after merged PR #378
```

## Closeout

```yaml
closeout:
  implementation_complete: true
  vertical_slice_complete: true
  audit:
    result: PASS
    material_findings_open: 0
  e2e:
    result: PASS
    journeys:
      - canonical NPC outfit data resolves to lazy sprite markers
      - unresolved NPC definitions retain factual dot markers
  final_ci:
    head: 5ced50ccc3df37b0f06b4c43d68cdece3ddad695
    result: PASS
    required_checks:
      - Required
      - Detect Build Scope
      - Fast Checks
      - Lua Tests
  pull_requests:
    open_related_prs: 0
    unresolved_review_threads: 0
    terminal_prs:
      - blakinio/Otheryn#378 merged as aae10e8c6f54b4517dfbfcc9e6bf8b70e38715c4
  task_status: completed
  task_archived: true
  ownership_released: true
  stale_branches_reconciled: true
```
