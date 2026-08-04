---
task_id: OTH-20260804-prs004d-protected-player-save
status: validating
project_lane: otheryn-runtime
policy_version: 2
task_kind: implementation
implementation_authorized: true
decomposition_decision: atomic
decomposition_reason: initial acquisition, exact Player ownership, selected save transaction and exact-next revision form one inseparable fail-closed persistence seam
context_pressure: medium
context_growth: stable
context_score: 10
estimate_confidence: medium
phase: validate
session_id: chat-github-20260804-prs004d
session_role: implementer
execution_mode: chat-github
branch: dudantas/prs-004d-protected-player-save
base_branch: main
start_sha: b489c1dd713fbcc2e4046d3173138138f1ba1e05
issue: "337"
feature_pr: "339"
created: 2026-08-04
updated: 2026-08-04T11:15:00+02:00
lease_expires_at: 2026-08-04T13:15:00+02:00
invocation_started_at: 2026-08-04T10:55:00+02:00
last_progress_at: 2026-08-04T11:15:00+02:00
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 2
context_reconstruction_attempts: 0
stall_warnings: 0
owned_paths:
  - src/database/player_writer_fence_repository.hpp
  - src/database/player_writer_fence_repository.cpp
  - src/database/player_writer_fenced_save_transaction.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - src/io/iologindata.hpp
  - src/io/iologindata.cpp
  - src/server/network/protocol/protocolgame.cpp
  - tests/integration/database/CMakeLists.txt
  - tests/integration/database/player_writer_fenced_save_it.cpp
  - .github/workflows/prs-004d-protected-player-save.yml
  - docs/architecture/prs-004d-protected-player-save.md
  - docs/agents/tasks/active/OTH-20260804-prs004d-protected-player-save.md
---

# PRS-004D protected player-save integration

## Scope

Bind initial world login and the selected `IOLoginData` player persistence transaction to the durable MariaDB writer fence delivered by terminal PRS-004C. Missing or stale context fails closed; protected mutations and exact-next revision commit atomically; final release follows only a successful protected save. No channel-handoff transfer or later-package work.

## Materialization evidence

- exact materializer blob: `d63370e028ee2d5d5d4546ce12038c8a0582c2d0`;
- observable executor run `30894986101` proved deterministic generation and failed only because the Actions token could not update a workflow path;
- observable executor run `30895193058` successfully pushed the twelve non-workflow paths;
- the dedicated workflow was added through the GitHub contents API;
- both temporary branch materializers were removed through the GitHub contents API;
- auxiliary executor PR #341 was closed without merge;
- branch synchronization PR #342 merged current `main` without rewriting history.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-04T11:15:00+02:00
status: validating
phase: validate
checkpoint_parent_sha: c7faadee59d81d5faf58761ca3a9d4c5b0d65341
branch: dudantas/prs-004d-protected-player-save
issue: 337
feature_pr: 339
changed_path_count: 13
proven:
  - PRS-004C terminal through PRs 285, 329, 334 and 336
  - exact thirteen-path PRS-004D scope materialized
  - temporary branch materializers absent from the feature diff
  - current main integrated by non-force merge PR 342
  - reconnect path remains unchanged for later PRS-004E transfer
unknown:
  - exact-head focused integration result
  - exact-head full applicable CI and Required result
  - feature merge and lifecycle metadata
conflicts: []
blockers: []
next_action: run exact-head dedicated integration and applicable CI, repair first concrete failure, then perform final audit and expected-head merge
```
