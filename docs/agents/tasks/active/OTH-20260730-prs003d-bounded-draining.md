---
task_id: OTH-20260730-prs003d-bounded-draining
status: active
branch: dudantas/prs-003d-c
base_branch: main
start_sha: b66241361d2cd1d97ee9c5a3fc28ee0677f39b8b
issue: "253"
feature_pr: "254"
created: 2026-07-30
updated: 2026-07-30
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-bounded-draining.md
  - docs/architecture/prs-003d-bounded-draining.md
  - src/database/database_failure_classification.hpp
  - src/database/database.cpp
  - src/game/database_outage_drain_orchestrator.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/game/database_outage_drain_orchestrator_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/architecture/prs-003d-mutation-admission-policy.md
  - docs/architecture/prs-003d-runtime-bank-mutation-gate.md
  - docs/agents/tasks/archive/OTH-20260729-prs002j-final-player-save.md
  - docs/agents/tasks/archive/OTH-20260730-prs003d-runtime-bank-mutation-gate.md
---

# PRS-003D-C bounded draining and final checkpoints

## Implemented contract

- `DatabaseOutageEventPublisher` serializes degraded-deadline, drain-completion and drain-deadline control events with monotonic sequences and clamped monotonic time.
- One finite dispatcher chain starts after a classified database failure; at most one drain event is scheduled at a time.
- A new drain generation captures, sorts and deduplicates one fixed online-player ID vector.
- The attempt limit equals the unique vector size; one exact pending ID prevents duplicate attempts and mismatched results fail closed.
- Before the deadline, each dispatcher event attempts at most one captured player.
- Completion publishes `DrainCompleted`; timeout publishes `DrainDeadlineExpired` before finite cleanup continues.
- Completion, timeout and malformed runtime state enter outage `Maintenance` and `GAME_STATE_MAINTAIN`.
- `SaveManager::removePlayerForDatabaseOutageDrain` calls the existing forced removal once and observes only the existing bounded final save invoked by the synchronous removal callback.
- Missing player, removal failure, missing save observation and save failure use explicit fixed low-cardinality evidence.

## Ownership correction

A repeated live audit found only open PRs #238 and #239. Their workflow/integration-test and coordinator-record paths remain disjoint. Terminal PRS-002J released `save_manager.hpp/.cpp`. The earlier candidate `game.cpp` and `player.hpp/.cpp` paths were released before modification; SaveManager is the smaller accepted observation seam.

## Safety boundaries

- no recovery probe, operator resume or automatic maintenance exit;
- no reconnect, ping, SQL retry or replay;
- no schema, migration, durable fencing or idempotency/ledger;
- no new mutation domains or broad economy gating;
- no production deployment or production operation;
- no coordinator or PRS-003E-A path changes;
- no duplicate final save, unbounded wait, unbounded loop or repeating cycle event.

## Failure-injection evidence

Deterministic tests cover sorted/deduplicated finite generations, completion, deadline expiry before cleanup, missing players, removal/save failure accounting, invalid snapshots, mismatched attempt results, serialized control sequences, distinct completion/timeout reasons and source wiring that proves one existing save without retry or replay.

## Rollback plan

Revert the feature merge. The slice creates no schema, durable authority, recovery behavior, credentials or deployment state.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T12:42:00+02:00
head: 824312278f927f27751d91b843ac9286261decc8
head_scope: implementation-complete feature head before this governance-only checkpoint commit
branch: dudantas/prs-003d-c
pr: 254
status: active
context_routes:
  - production-resilience
  - database-outage
  - draining
  - final-checkpoint
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-bounded-draining.md
  - docs/architecture/prs-003d-bounded-draining.md
  - src/database/database_failure_classification.hpp
  - src/database/database.cpp
  - src/game/database_outage_drain_orchestrator.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/game/database_outage_drain_orchestrator_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - PRS-003D-B is terminal with complete feature, lifecycle and finalizer evidence.
  - Issue 253, branch dudantas/prs-003d-c and feature PR 254 are the only discovered D-C records.
  - Coordinator PR 239 owns only its coordinator record.
  - PRS-003E-A PR 238 owns four disjoint workflow and integration-test paths.
  - Existing state owner validates degraded expiry, drain completion and drain deadline expiry.
  - Existing forced player removal is synchronous and invokes the accepted bounded final-save seam.
  - Re-audit found terminal PRS-002J SaveManager paths unowned and released the earlier game/player candidates before modification.
  - Feature scope contains exactly ten owned paths and was behind main by zero before PR creation.
  - Pure tests and source-wiring evidence cover all finite-attempt and no-duplicate-save invariants.
derived:
  - one fixed player-ID generation and one-attempt-per-ID plan is a finite orchestration boundary
  - a scoped SaveManager observer exposes the existing synchronous removal save result without adding a duplicate save
unknown:
  - exact final governance-complete head CI, Required and autofix results
conflicts: []
first_failure: null
rejected_hypotheses:
  - unbounded drain retries
  - broad mutation gating in D-C
  - recovery/resume in D-C
  - duplicate final-save before or after normal logout cleanup
  - large game.cpp or player.cpp edits when the released SaveManager seam is sufficient
changed_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-bounded-draining.md
  - docs/architecture/prs-003d-bounded-draining.md
  - src/database/database_failure_classification.hpp
  - src/database/database.cpp
  - src/game/database_outage_drain_orchestrator.hpp
  - src/game/scheduling/save_manager.hpp
  - src/game/scheduling/save_manager.cpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/game/database_outage_drain_orchestrator_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: live dependency and ownership audit
    result: PASS
    evidence: terminal D-B; no D-C duplicate; coordinator and E-A ownership is disjoint; SaveManager paths are released
  - command: implementation scope audit before PR
    result: PASS
    evidence: exactly ten owned paths, behind_by zero and no released candidate path changed
  - command: focused tests and exact-head repository CI
    result: PENDING
    evidence: PR 254 opened; governance checkpoint commit requires replacement exact-head validation
blockers: []
next_action: validate the final exact PR head, fix any first failure, then perform final audit and expected-head squash merge
```
