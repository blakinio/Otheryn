---
task_id: OTH-20260813-full-otbm-atlas
status: validating
owner: chatgpt-github-20260814-environment-animation
created: 2026-08-13
updated: 2026-08-14T00:58:00+02:00
project_lane: otheryn-content
related_pr: "381"
ownership_released: false
execution_budget_minutes: 120
execution_budget_reason: owner-expanded atlas scope adds deterministic animated environment appearances and requires renewed exact-head validation
modules_touched:
  - otbm-atlas
---

# Full OTBM atlas continuation

PR #381 remains the active atlas integration branch. The owner explicitly expanded its scope on 2026-08-14 to add browser-side animation for canonical environment appearances such as flames and lamps, while keeping server-driven state changes distinct from cyclic appearance animation.

The implemented path preserves the chunked/bounded architecture. Cyclic animation metadata comes from pinned object appearances and sprite sheets. Only conservative topmost 32x32 non-displaced appearances with no nearby cross-tile occlusion risk are promoted. Each promoted occurrence gets an underlay rendered from the same tile stack with that top item omitted, while deduplicated phase PNGs are shared by matching appearance/pattern keys. The browser requests only viewport shards at zoom >= 1.5, culls individual records, uses bounded animation image/shard LRUs, and suspends animation work while hidden. Unsupported, displaced, edge-risk or occluded animations remain deterministic static pixels. Stateful variants such as doors, switches, quest objects or on/off state are not inferred as cyclic animation.

A dedicated real Chromium workflow now proves phase changes on the browser animation canvas. Final canonical full-world generation remains the source of truth for the exact number of promoted occurrences and for confirming that the enrichment remains compatible with the 3494-chunk atlas.

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-14T00:58:00+02:00
code_head: 8dabcbf1a0f2bbfce9f6454d6e9b6b0010faa53e
branch: agent/oth-20260813-full-otbm-atlas-current-main
pr: 381
status: validating
phase: environment-animation-final-validation
session_id: chatgpt-github-20260814-environment-animation
session_role: implementer
execution_mode: chat-github
execution_reason: GitHub-only implementation and validation; owner-funded Codex remains forbidden
project_lane: otheryn-content
context_pressure: medium
context_growth: stable
context_score: 7
decomposition_decision: phased
owned_paths:
  - tools/otbm_atlas/**
  - .github/workflows/otbm-atlas-tests.yml
  - .github/workflows/otbm-environment-animation-tests.yml
  - docs/maps/atlas-environment-animation.md
  - docs/agents/tasks/active/OTH-20260813-full-otbm-atlas.md
proven:
  - canonical world SHA-256 is 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034
  - opentibiabr/otclient appearances.proto and animator.cpp define the animation phase metadata and synchronized timing semantics used as the primary reference
  - pinned object assets contain cyclic multi-phase appearances and the atlas decoder now retains phase duration, synchronization and loop metadata
  - dynamic server state remains explicitly separate from cyclic appearance animation
  - browser environment image cache is bounded to 256 entries / 64 MiB and animation shard cache to 64 entries / 8 MiB
  - real-browser environment-animation workflow was added and existing full-world final gate remains applicable
unknown:
  - exact canonical full-world environment animation statistics until the exact-head full-world run completes
  - exact-head CI and browser E2E conclusions for the final validation head
blockers: []
recovery:
  policy_version: 1
  generation: 2
  session_id: chatgpt-github-20260814-environment-animation
  session_started_at: 2026-08-14T00:25:00+02:00
  checkpointed_at: 2026-08-14T00:58:00+02:00
  last_progress_at: 2026-08-14T00:58:00+02:00
  phase: environment-animation-final-validation
  exact_head: 8dabcbf1a0f2bbfce9f6454d6e9b6b0010faa53e
  pull_request: 381
  active_operation: exact-head-ci
  external_run_ids:
    - 31751917749
    - 31751917759
    - 31751917916
    - 31751917799
  operation_started_at: 2026-08-14T00:55:00+02:00
  wait_deadline_at: 2026-08-14T01:40:00+02:00
  check_generation: environment-animation-1
  checks_used: 1
  status: waiting
  safe_to_resume: true
  resume_condition: PR 381 remains open and exact final head is unchanged
  next_action: observe aggregate exact-head CI after this checkpoint commit, inspect any first actionable failure, then complete audit/E2E/merge closeout
next_action: observe aggregate exact-head CI after this checkpoint commit, inspect any first actionable failure, then complete audit/E2E/merge closeout
```
