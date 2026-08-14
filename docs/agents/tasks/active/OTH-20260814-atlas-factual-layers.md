---
task_id: OTH-20260814-atlas-factual-layers
status: implementing
owner: openai
branch: agent/oth-20260814-atlas-factual-layers
base_branch: main
created: 2026-08-14
updated: 2026-08-14T21:34:00+02:00
project_lane: otheryn-content
execution_budget_minutes: 120
execution_budget_reason: full-stack atlas consumer integration requires pinned source compilation, real Chromium E2E, audit and exact-head CI
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
- real Chromium E2E must prove scripted teleport details, raid area rendering, NPC service details and URL/navigation behavior.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-14T21:34:00+02:00
status: implementing
phase: consumer-integration
branch: agent/oth-20260814-atlas-factual-layers
base_main: da553b1f2f157526e69e26d051ca3297db7abcf6
producer_pr: 385
producer_status: merged
producer_merge: 2cf8035401a05873c307af7388872141a76309ef
runtime_animation_prs: "386 superseded; 387 merged"
context_pressure: medium
context_growth: stable
decomposition_decision: phased
proven:
  - factual producer is merged and exact pinned CrystalServer sources are on main
  - consumer branch is reconciled with current main after runtime animation merge
  - conservative transformation promotes only proven scripted transitions and explicit rewardBoss=true bosses
  - raid rectangles are now sharded into every intersecting viewport chunk
  - viewer has separate OTBM/scripted teleport, raid, NPC-service and verified-boss controls
  - dedicated real Chromium factual-layer E2E workflow is committed on the task branch
blockers: []
next_action: finish atlas.py wiring from the queued branch-only patch run, remove the temporary patch workflow, open the integration PR and execute focused/E2E/audit/exact-head closeout
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 1
  session_id: chat-github-20260814-factual-layers
  session_started_at: 2026-08-14T21:24:00+02:00
  checkpointed_at: 2026-08-14T21:34:00+02:00
  last_progress_at: 2026-08-14T21:34:00+02:00
  phase: consumer-integration
  exact_head: bf5c73935eccf49f86b009324d351a29396bc3e8
  pull_request: none
  active_operation: branch-only atlas.py patch workflow
  external_run_ids: [31833498321]
  operation_started_at: 2026-08-14T21:29:45+02:00
  wait_deadline_at: 2026-08-14T21:44:45+02:00
  check_generation: atlas-build-wiring-1
  checks_used: 1
  status: active
  safe_to_resume: true
  resume_condition: patch run reaches a terminal state and no conflicting writer has moved the task branch unexpectedly
  next_action: inspect patch run 31833498321 once, verify atlas.py diff, then delete the temporary patch workflow before opening the PR
```
