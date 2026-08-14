---
task_id: OTH-20260814-atlas-factual-layers
status: waiting
owner: openai
branch: agent/oth-20260814-atlas-factual-layers
base_branch: main
created: 2026-08-14
updated: 2026-08-14T21:38:00+02:00
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
  - .github/workflows/otbm-atlas-factual-layers-audit.yml
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
updated_at: 2026-08-14T21:38:00+02:00
status: waiting
phase: exact-head-validation
branch: agent/oth-20260814-atlas-factual-layers
base_main: da553b1f2f157526e69e26d051ca3297db7abcf6
implementation_head: 442f3bb95c19da55ac0670f8853f5029cfb29b55
pull_request: 390
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
  - canonical atlas.py now resolves mechanics from the pinned CrystalServer scripts and invokes factual enrichment explicitly
  - direct OTBM teleports remain separate from proven scripted transitions
  - conservative transformation promotes only proven scripted transitions and explicit rewardBoss=true bosses
  - raid rectangles are sharded into every intersecting viewport chunk
  - viewer has separate OTBM/scripted teleport, raid, NPC-service and verified-boss controls
  - temporary branch-only patch workflow is removed from the final implementation diff
  - PR 390 is open as the integration PR with zero review threads at the first hygiene check
validation:
  code_head: 442f3bb95c19da55ac0670f8853f5029cfb29b55
  runs:
    CI: 31834022293
    atlas: 31834021967
    environment_animation: 31834021999
    factual_contract_e2e: 31834021944
    factual_independent_audit: 31834022151
    required: 31834022025
  observation_count: 2
  observed_state: queued
blockers: []
next_action: observe the existing PR 390 validation generation after the bounded wait; repair only a concrete failed gate, otherwise mark ready and complete exact-head merge closeout
```

## Recovery checkpoint

```yaml
recovery:
  policy_version: 1
  generation: 2
  session_id: chat-github-20260814-factual-layers
  session_started_at: 2026-08-14T21:24:00+02:00
  checkpointed_at: 2026-08-14T21:38:00+02:00
  last_progress_at: 2026-08-14T21:38:00+02:00
  phase: exact-head-validation
  exact_head: 442f3bb95c19da55ac0670f8853f5029cfb29b55
  pull_request: 390
  active_operation: PR validation generation
  external_run_ids: [31834022293, 31834021944, 31834021967, 31834021999, 31834022025, 31834022151]
  operation_started_at: 2026-08-14T21:36:22+02:00
  wait_deadline_at: 2026-08-14T22:06:22+02:00
  check_generation: factual-layers-pr-1
  checks_used: 2
  status: waiting
  safe_to_resume: true
  resume_condition: PR 390 remains open, implementation head 442f3bb95c19da55ac0670f8853f5029cfb29b55 is unchanged except for lifecycle-only documentation, and the recorded workflows reach a terminal state
  next_action: inspect one aggregate validation snapshot for PR 390; on failure inspect only the first actionable failed job, otherwise finish ready/merge/archive closeout
```
