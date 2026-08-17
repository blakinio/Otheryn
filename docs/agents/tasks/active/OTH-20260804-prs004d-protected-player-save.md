---
task_id: OTH-20260804-prs004d-protected-player-save
status: validating
project_lane: otheryn-runtime
policy_version: 2
task_kind: implementation
implementation_authorized: true
decomposition_decision: atomic
decomposition_reason: initial acquisition, exact Player ownership, selected player persistence and exact-next fence revision form one inseparable fail-closed persistence seam
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
updated: 2026-08-04T15:48:00+02:00
lease_expires_at: 2026-08-04T17:48:00+02:00
invocation_started_at: 2026-08-04T15:17:00+02:00
last_progress_at: 2026-08-04T15:48:00+02:00
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 3
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

## Materialization and repair evidence

- exact materializer blob: `d63370e028ee2d5d5d4546ce12038c8a0582c2d0`;
- observable executor run `30894986101` proved deterministic generation and failed only because the Actions token could not update a workflow path;
- observable executor run `30895193058` successfully pushed the twelve non-workflow paths;
- both temporary branch materializers were removed from the feature diff;
- auxiliary executor PR #341 was closed without merge;
- branch synchronization PR #342 merged the then-current `main` without rewriting history;
- trusted repair PR #353 passed full exact-head CI `30911532148`, Required `30911531350` and autofix `30911529773`, then squash-merged as `a5784e723bdcbee55c5590938ddb9d3922294096`;
- synchronization PR #354 merged that exact trusted helper into the feature branch without force-push;
- helper job `92010413368` completed every gate, checkout, transform and commit step successfully;
- bot commit `7ccc9c12d7281c62f1df5e85c816ffc14213693d` changed only `src/game/scheduling/save_manager.cpp`;
- the bounded final checkpoint now retains its writer fence across follow-up attempts and releases it once only after the state is clean;
- cleanup PR #355 removes all five temporary helper paths and is awaiting exact-head validation.

## Context checkpoint

```yaml
checkpoint_version: 2
updated_at: 2026-08-04T15:48:00+02:00
status: validating
phase: validate
checkpoint_parent_sha: 7ccc9c12d7281c62f1df5e85c816ffc14213693d
branch: dudantas/prs-004d-protected-player-save
issue: 337
feature_pr: 339
changed_path_count: 13
proven:
  - PRS-004C terminal through PRs 285, 329, 334 and 336
  - exact thirteen-path PRS-004D implementation scope materialized
  - initial acquisition occurs before player placement
  - protected player SQL mutation and exact-next revision CAS share one transaction
  - malformed, missing and stale contexts fail closed without replay
  - final-save follow-up attempts retain the exact writer fence
  - final exact release occurs once only after the protected state is clean
  - repair commit changed exactly one implementation file
  - reconnect path remains unchanged for later PRS-004E transfer
in_progress:
  - cleanup PR 355 exact-head validation
  - exact-head focused integration and applicable CI for this checkpoint
unknown:
  - cleanup merge and synchronization result
  - clean final exact-head CI after helper removal
  - feature merge and lifecycle evidence
conflicts: []
blockers: []
next_action: validate and merge cleanup PR 355, integrate current main without rewriting history, update the final checkpoint, then require clean exact-head dedicated integration, CI, Required, Repository Audit and autofix before expected-head squash merge
```
