---
task_id: OTH-20260814-atlas-factual-layers
status: in_progress
owner: openai
branch: agent/oth-20260814-atlas-factual-layers
base_branch: main
created: 2026-08-14
updated: 2026-08-14T19:25:00+02:00
project_lane: otheryn-content
execution_budget_minutes: 120
modules_touched:
  - otbm-atlas
owned_paths:
  - tools/otbm_atlas/atlas.py
  - tools/otbm_atlas/factual_layers.py
  - tools/otbm_atlas/viewer.py
  - tools/otbm_atlas/viewer_app.js
  - tools/otbm_atlas/tests/test_factual_layers.py
  - tools/otbm_atlas/tests/test_viewer_factual_layers.py
  - .github/workflows/otbm-atlas-factual-layers-tests.yml
  - docs/maps/atlas-factual-layers.md
  - docs/agents/tasks/active/OTH-20260814-atlas-factual-layers.md
required_reads:
  - AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
---

# Atlas factual mechanics, raids/events, boss evidence and NPC services

## Delivery classification

```yaml
feature_scope:
  type: full_stack
  user_facing: true
  backend_required: true
  frontend_required: true
  integration_required: true
  e2e_required: true
```

## Goal

Consume the merged `tools/otbm_atlas_facts` producer inside the canonical chunked OTBM Atlas so users can inspect factual scripted mechanics, raid/event regions, verified boss evidence and NPC services without losing source provenance or promoting uncertain behavior to truth.

## Acceptance

- replace the legacy `data-otservbr-global` mechanics provenance path with the exact pinned CrystalServer facts producer;
- keep direct OTBM teleports separate from scripted teleport evidence;
- expose only `RESOLVED` + `PROVEN_STATIC` scripted transitions as navigable scripted-teleport records and preserve `conditional=true`;
- expose raid single-spawn points and exact raid/event rectangles; derived centers may be used only for navigation/sharding and must remain labelled as derived;
- expose verified boss evidence only when `rewardBoss=true` is explicitly resolved; path/name/category alone may never create a boss marker;
- enrich base-map NPC spawns with resolved/ambiguous service evidence; show shop/bank/guild-bank/travel details and exact proven travel destinations/costs;
- preserve `UNKNOWN`, `UNRESOLVED` and `AMBIGUOUS` evidence in reports/details without rendering it as a falsely certain map link;
- keep all new spatial data chunked and bounded; do not load full-world factual records into the browser at startup;
- add viewer controls, search/details and exact raid-area visualization;
- real Chromium E2E must prove scripted teleport details, raid area rendering, NPC service details and URL/navigation behavior;
- no changes to `tools/otbm_atlas/viewer_runtime.js`, `environment_animation.py`, `test_environment_animation.py` or `test_viewer_runtime.py` while PR #387 owns runtime-animation paths.

## Checkpoint

```yaml
checkpoint_version: 1
base_main: 2cf8035401a05873c307af7388872141a76309ef
producer_pr: 385
producer_status: merged
producer_merge: 2cf8035401a05873c307af7388872141a76309ef
conflicting_active_pr: 387
conflict_strategy: use disjoint atlas.py/factual_layers.py/viewer.py/viewer_app.js paths; reconcile current main before final validation
blockers: []
next_action: inspect current atlas build/spatial/viewer contracts, implement factual-layer transformation and chunked export, then add real browser acceptance
```
