---
task_id: OTH-20260804-prs004d-protected-player-save
status: blocked
project_lane: otheryn-runtime
policy_version: 2
task_kind: implementation
implementation_authorized: true
decomposition_decision: atomic
decomposition_reason: initial acquisition, exact Player ownership, selected save transaction and exact-next revision form one inseparable fail-closed persistence seam
context_pressure: high
context_growth: stable
context_score: 12
estimate_confidence: medium
phase: implement
session_id: chat-github-20260804-prs004d
session_role: implementer
execution_mode: chat-github
branch: dudantas/prs-004d-protected-player-save
base_branch: main
start_sha: b489c1dd713fbcc2e4046d3173138138f1ba1e05
issue: "337"
feature_pr: "339"
created: 2026-08-04
updated: 2026-08-04T09:05:00+02:00
lease_expires_at: 2026-08-04T09:05:00+02:00
invocation_started_at: 2026-08-04T08:05:00+02:00
last_progress_at: 2026-08-04T09:05:00+02:00
ci_checks_for_current_head: 0
unchanged_state_checks: 2
identical_failure_retries: 0
repair_cycles_for_current_gate: 2
context_reconstruction_attempts: 0
stall_warnings: 1
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
temporary_paths:
  - .github/workflows/prs-004d-materialize.yml
  - .github/workflows/prs-004d-run-materializer.yml
---

# PRS-004D protected player-save integration

## Scope

Bind initial world login and the selected `IOLoginData` player persistence transaction to the durable MariaDB writer fence delivered by terminal PRS-004C. Missing or stale context fails closed; protected mutations and exact-next revision commit atomically; final release follows only a successful protected save. Channel-handoff transfer remains PRS-004E.

## Durable continuation checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-04T09:05:00+02:00
status: blocked
phase: implement
branch: dudantas/prs-004d-protected-player-save
pr: 339
issue: 337
last_known_head: 16220fabdb8fabd8d519bf03c28ca50993c214e4
proven:
  - PRS-004C is terminal through feature PR 285, lifecycle PR 329, finalizer PR 334 and terminal-evidence PR 336
  - issue 337 is the unique authorized PRS-004D execution issue
  - branch dudantas/prs-004d-protected-player-save and feature PR 339 are canonical
  - exact thirteen final owned paths are frozen in issue 337
  - the deterministic implementation payload exists in .github/workflows/prs-004d-materialize.yml
  - materializer Git blob is d63370e028ee2d5d5d4546ce12038c8a0582c2d0
  - trusted bootstrap PR 338 passed CI, Required and autofix and merged as 54e1e389a5d2cf5d524ce0778d74847b12674ef9
  - temporary exact-blob bootstrap and branch-runner workflows expose no secrets and restrict writes to the authorized branch/scope
unknown:
  - whether an Actions run was created for the trusted pull_request_target or branch push runners
  - exact generated implementation head
  - focused compile and integration findings
  - feature merge and lifecycle metadata
conflicts: []
blockers:
  - connector-created commits did not produce an observable execution of either materializer trigger during this invocation
  - generated production and test paths remain absent from the canonical branch
  - the connected GitHub tool exposes no workflow_dispatch action and no global workflow-run listing for these non-PR-triggered runs
first_failure:
  marker: branch_workflow_not_activated_on_initial_creation
  containment:
    - merged exact-blob pull_request_target bootstrap PR 338
    - reopened PR 339 and pushed a checkpoint commit
    - added and activated a verified branch runner by a second commit
  result: no generated path observed before execution-budget expiry
rejected_hypotheses:
  - bypass durable MariaDB authority
  - hand-edit only part of the protected save seam
  - merge temporary workflows as product scope
  - start PRS-004E before terminal PRS-004D
next_action:
  - inspect GitHub Actions for PRS-004D Materializer Bootstrap or PRS-004D Run Verified Materializer
  - if a run failed, read its exact job log and repair only the first failing marker
  - if no run exists, execute the verified materializer through an environment with workflow_dispatch or a repository checkout, then commit exactly the thirteen frozen paths
  - remove both temporary branch workflows before exact-head feature validation
  - audit no-PCH includes in save_manager.cpp, especially array, limits and optional
  - run focused disposable-MariaDB validation, full applicable exact-head CI and complete PRS-004D lifecycle
```
