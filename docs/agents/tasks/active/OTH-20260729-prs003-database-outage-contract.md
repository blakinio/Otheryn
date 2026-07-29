---
task_id: OTH-20260729-prs003-database-outage-contract
status: validating
branch: dudantas/prs-003-database-outage-contract
base_branch: main
start_sha: d09b4f04887a74e31f9e47a82c1c96ab91d33325
created: 2026-07-29
updated: 2026-07-29
related_issue: "195"
related_pr: "196"
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003-database-outage-contract.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/oam-004a-database-transaction-integrity.md
  - docs/architecture/oam-004d-player-save-failure-propagation.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
search_first:
  - src/database/database.hpp
  - src/database/database.cpp
  - src/database/databasetasks.hpp
  - src/database/databasetasks.cpp
  - src/canary_server.cpp
  - src/game/game_definitions.hpp
  - src/game/game.hpp
  - src/game/game.cpp
  - src/server/network/protocol/protocollogin.cpp
  - src/server/network/protocol/protocolgame.cpp
---

# PRS-003 database-outage state-machine discovery

## Goal

Record the proven startup and runtime database-failure behavior and accept one bounded, deterministic fail-closed outage-state contract before changing runtime admission, gameplay or persistence behavior.

## Current behavior inventory

- startup calls `Database::connect()` and aborts normal startup when connection or migration validation fails;
- the process uses one serialized MySQL handle with implicit reconnect disabled and no arbitrary statement replay;
- runtime query failure is logged and returned as `false` or `nullptr`, but no process-level database-health or outage state is changed;
- `DatabaseTasks::execute` exposes a success boolean only to an optional callback, while `DatabaseTasks::store` currently invokes its callback with `true` even when the result is null;
- `GameState_t` contains startup, init, normal, closing, closed, shutdown and maintain states, but no degraded or draining state;
- login protocols gate startup, maintain and shutdown; game login additionally gates closing and closed, but none of those gates are driven by database health;
- PRS-002 provides bounded final player saves, but no outage controller decides when to stop admitting new work or begin draining.

## Accepted target contract

- introduce a database-independent state machine with `HEALTHY`, `DEGRADED`, `DRAINING` and `MAINTENANCE` states;
- transition only from explicit classified events, never from free-form log text;
- the first qualifying runtime persistence failure enters `DEGRADED`, records the first-failure time and blocks new logins, channel switches and critical economy mutations;
- `DEGRADED` permits only explicitly classified safe work for one finite grace period while health probes run on a bounded cadence;
- grace expiry, repeated qualifying failures or an unknown commit outcome enter `DRAINING`;
- `DRAINING` rejects new durable mutations, requests bounded PRS-002 final saves, and moves to `MAINTENANCE` after players are removed or the drain deadline expires;
- `MAINTENANCE` admits only operator-authorized diagnostic/recovery work and never resumes normal gameplay automatically;
- return to `HEALTHY` requires an explicit successful recovery decision after consecutive read and write probes; a successful single query is insufficient;
- arbitrary SQL replay, automatic whole-world rollback and automatic database promotion remain forbidden;
- state, reason, transition count, first-failure timestamp, degraded age and drain deadline are observable with low-cardinality labels.

## Failure-injection plan

- startup connection failure and migration failure remain fail closed;
- one classified runtime connection loss enters degraded exactly once;
- repeated failures do not reset the original degraded deadline;
- unknown commit outcome enters draining without replay;
- bounded recovery probes can prove eligibility but cannot auto-resume from maintenance;
- degraded grace expiry enters draining;
- drain completion and drain timeout both enter maintenance with different fixed reasons;
- failed PRS-002 final save is observable and does not extend the drain deadline indefinitely.

## Rollback plan

Revert this discovery-contract merge. It changes only documentation, one source-contract test and test registration; no runtime, schema, database data, credentials or deployment state are changed.

## Explicit non-goals

- no runtime outage-state implementation in this milestone;
- no database connection pool, reconnect, statement replay or generic retry framework;
- no schema, migration, production database, credential or deployment change;
- no PRS-004 fencing, PRS-005 idempotency, PRS-006 reconciliation, PRS-007 failover or PRS-008 Compose work;
- no production RPO/RTO claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T17:12:00+02:00
head: eacd6b609fedd3572626a25e26b084c5d21a76e9
head_scope: implementation head before this checkpoint-only update; all four owned paths are present in PR 196
branch: dudantas/prs-003-database-outage-contract
pr: 196
status: validating
context_routes:
  - production-resilience
  - database
  - outage-handling
  - game-lifecycle
  - authentication
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003-database-outage-contract.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - PRS-001 and PRS-002 are complete; PRS-002J is terminally archived on main d09b4f04887a74e31f9e47a82c1c96ab91d33325.
  - Startup database connection and migration failure abort normal startup.
  - Runtime Database operations log and return failure without publishing a central outage transition.
  - Implicit reconnect and arbitrary statement replay are disabled.
  - Current GameState_t has no degraded or draining state.
  - Existing login gates are based on game lifecycle state, not database health.
  - Issue 195 and PR 196 own exactly the bounded PRS-003 discovery milestone.
  - The architecture contract defines classified events, finite deadlines, fail-closed admission, bounded draining, explicit recovery and low-cardinality observability.
  - The focused source-contract test covers startup, runtime Database, DatabaseTasks, lifecycle states, login gates and the accepted target sequence.
derived:
  - Runtime persistence failure can leave the server accepting additional work because no central database-health admission policy exists.
  - The first implementation should be a pure database-independent state machine before wiring Database, protocols or gameplay call sites.
unknown:
  - Exact-head repository CI, Required and autofix results for the live PR head after this checkpoint update.
conflicts: []
first_failure:
  marker: null
  evidence: No implementation or validation failure has occurred.
rejected_hypotheses:
  - reconnect and replay arbitrary SQL after connection loss
  - reuse GAME_STATE_CLOSED as an undocumented database-health state
  - disconnect all players immediately on the first failed statement
  - auto-resume gameplay after one successful query
  - combine PRS-003 with fencing, idempotency, reconciliation or failover
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003-database-outage-contract.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - tests/unit/game/CMakeLists.txt
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
validation:
  - command: governance and ownership preflight
    result: PASS
    evidence: Fresh issue 195 and branch start from exact main d09b4f04887a74e31f9e47a82c1c96ab91d33325 with four declared paths.
  - command: live startup, database, game-state and login source audit
    result: PASS
    evidence: Startup is fail closed; runtime failures have no central outage transition; current states and login gates are lifecycle-only.
  - command: focused source-contract and CMake registration audit
    result: PASS
    evidence: One PRS003 source-root definition and one registered test source cover the four intended source boundaries and accepted contract.
  - command: checkpoint validator and exact-head repository CI
    result: NOT_RUN
    evidence: PR 196 is open and checks are expected on the checkpoint-updated head.
blockers: []
next_action: Verify the live PR 196 head and exact-head CI, Required and autofix; fix only bounded contract/test failures, then perform the final path, discussion and main-drift audit before merge.
```
