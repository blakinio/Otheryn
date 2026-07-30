---
task_id: OTH-20260730-prs003d-bounded-draining
status: active
branch: dudantas/prs-003d-c
base_branch: main
start_sha: b66241361d2cd1d97ee9c5a3fc28ee0677f39b8b
issue: "253"
feature_pr: pending
created: 2026-07-30
updated: 2026-07-30
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-bounded-draining.md
  - docs/architecture/prs-003d-bounded-draining.md
  - src/database/database_failure_classification.hpp
  - src/database/database.cpp
  - src/game/database_outage_drain_orchestrator.hpp
  - src/game/game.cpp
  - src/creatures/players/player.hpp
  - src/creatures/players/player.cpp
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

## Current behavior inventory

- The PRS-003 state owner already has finite degraded and drain deadlines and validated control transitions.
- Runtime publication currently exposes database-failure events and immutable snapshots, but no serialized deadline/control-event bridge.
- Terminal PRS-003D-A/D-B reject unsafe admissions and the live critical-durable bank mutation seam in `Draining` and `Maintenance`.
- `Player::removePlayer()` synchronously converges on `Player::onRemoveCreature(..., true)`; that callback invokes `SaveManager::savePlayer()` after logout state is finalized.
- Terminal PRS-002J bounds final save to at most two attempts and finite ownership waits, but the boolean result is not exposed to the drain caller.
- No runtime scheduler currently advances expired outage deadlines, removes a fixed player set or transitions game lifecycle to maintenance.

## Accepted target contract

Add one serialized control-event bridge, one deterministic finite player-attempt plan and one periodic runtime tick. Drain entry captures a sorted, fixed list of online player IDs. Each ID is attempted at most once through existing forced logout/removal. Final-save and removal results remain explicit. Completion or deadline expiry transitions the outage state to maintenance and the game lifecycle to `GAME_STATE_MAINTAIN`. After deadline expiry, only the already-captured finite set may receive one cleanup attempt each.

## Explicit non-goals

- no recovery probe, operator resume or automatic maintenance exit;
- no reconnect, ping, SQL retry or replay;
- no schema, migration, durable fencing or idempotency/ledger;
- no new mutation domains or broad economy gating;
- no production deployment or production operation;
- no coordinator or PRS-003E-A path changes.

## Failure-injection plan

Deterministic unit tests inject completed drains, deadline expiry, missing players, removal failure and final-save failure. Tests prove one attempt per captured ID, no queue growth, finite cleanup, serialized control sequences, state-machine reasons, source wiring and absence of retry/replay loops.

## Rollback plan

Revert the feature merge. The slice creates no schema, durable authority, recovery behavior, credentials or deployment state.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T12:10:00+02:00
head: b66241361d2cd1d97ee9c5a3fc28ee0677f39b8b
head_scope: task-start main before first task-record commit
branch: dudantas/prs-003d-c
pr: null
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
  - src/game/game.cpp
  - src/creatures/players/player.hpp
  - src/creatures/players/player.cpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/game/database_outage_drain_orchestrator_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - PRS-003D-B is terminal with complete feature, lifecycle and finalizer evidence.
  - Issue 253 and branch dudantas/prs-003d-c are the only discovered D-C records.
  - Coordinator PR 239 owns only its coordinator record.
  - PRS-003E-A PR 238 owns four disjoint workflow and integration-test paths.
  - Existing state owner validates degraded expiry, drain completion and drain deadline expiry.
  - Existing forced player removal is synchronous and invokes the accepted bounded final-save seam.
derived:
  - one fixed player-ID generation and one-attempt-per-ID plan is a finite orchestration boundary
unknown:
  - exact final implementation head and repository CI evidence
conflicts: []
first_failure: null
rejected_hypotheses:
  - unbounded drain retries
  - broad mutation gating in D-C
  - recovery/resume in D-C
  - duplicate final-save before normal logout cleanup
changed_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-bounded-draining.md
validation:
  - command: live dependency and ownership audit
    result: PASS
    evidence: terminal D-B; no D-C duplicate; coordinator and E-A ownership is disjoint
  - command: runtime seam inventory
    result: PASS
    evidence: state owner control transitions, synchronous removal and bounded final save were located
  - command: focused tests and exact-head repository CI
    result: NOT_RUN
    evidence: implementation not yet committed
blockers: []
next_action: implement the eleven-path bounded draining package and run focused validation
```
