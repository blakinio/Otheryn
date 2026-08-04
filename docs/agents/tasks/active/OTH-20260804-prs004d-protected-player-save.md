---
task_id: OTH-20260804-prs004d-protected-player-save
status: implementing
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
phase: implement
session_id: chat-github-20260804-prs004d
session_role: implementer
execution_mode: chat-github
branch: dudantas/prs-004d-protected-player-save
base_branch: main
start_sha: b489c1dd713fbcc2e4046d3173138138f1ba1e05
issue: "337"
feature_pr: pending
created: 2026-08-04
updated: 2026-08-04T08:35:00+02:00
lease_expires_at: 2026-08-04T10:35:00+02:00
invocation_started_at: 2026-08-04T08:05:00+02:00
last_progress_at: 2026-08-04T08:35:00+02:00
ci_checks_for_current_head: 0
unchanged_state_checks: 0
identical_failure_retries: 0
repair_cycles_for_current_gate: 0
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

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-04T08:35:00+02:00
status: implementing
phase: implement
head: pending_materializer
branch: dudantas/prs-004d-protected-player-save
issue: 337
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
proven:
  - PRS-004C terminal through PRs 285, 329, 334 and 336
  - issue 337 is the unique authorized PRS-004D execution issue
  - no open PR or branch named PRS-004D existed before ownership freeze
  - reconnect path remains read-only for PRS-004E transfer
unknown:
  - deterministic materializer outcome
  - exact-head focused and full CI
  - feature merge and lifecycle metadata
conflicts: []
blockers: []
next_action: materialize exact thirteen-path implementation, remove temporary workflow, open feature PR and validate exact head
```
