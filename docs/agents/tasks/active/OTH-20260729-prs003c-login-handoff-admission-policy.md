---
task_id: OTH-20260729-prs003c-login-handoff-admission-policy
status: validating
branch: dudantas/prs-003c-login-handoff-admission-policy
base_branch: main
start_sha: 6a6007667dfd82010b0240342180961cd553466f
rebased_onto_sha: beea2231a0ea66fd783260a3fdbfb71afec5d566
created: 2026-07-29
updated: 2026-07-29
related_issue: "206"
related_pr: pending
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-login-handoff-admission-policy.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_policy.hpp
  - tests/unit/server/network/protocol/database_outage_admission_policy_test.cpp
  - tests/unit/server/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/agents/tasks/archive/OTH-20260729-prs003a-database-outage-state-machine.md
---

# PRS-003C-A pure login and handoff outage admission policy

## Goal

Add one deterministic pure decision component using an immutable database-outage snapshot, an explicit operation class, caller capabilities and `GameState_t`. This package does not change live protocol behavior.

## Proven current behavior

- PRS-003A exposes immutable snapshots for Healthy, Degraded, Draining and Maintenance.
- Account login rejects startup, maintenance and shutdown.
- Game login additionally rejects closing and closed for callers without `CanAlwaysLogin`.
- `CanAlwaysLogin` is not a maintenance or database-outage bypass.
- Protocol-session handoff is a distinct entry stage and then reaches ordinary game login.
- The coordination task on current main reserves this package as independently mergeable pure policy and serializes shared registration paths.

## Implemented contract

- account login, game login, protocol-session handoff and explicit staff diagnostic operation are distinct classes;
- unknown operation, lifecycle and outage values reject fail closed;
- startup and shutdown dominate all operations;
- lifecycle maintenance permits only the explicitly classified diagnostic operation with a separate capability;
- `CanAlwaysLogin` affects game login and handoff only in closing and closed lifecycle states;
- degraded and draining reject every supported operation;
- outage maintenance rejects login and handoff and permits only explicit diagnostics;
- decisions contain fixed reason codes and no localized protocol message;
- evaluation is `constexpr`, `noexcept`, deterministic and reads supplied values only.

## Shared path

`tests/unit/server/CMakeLists.txt` is shared. The package adds one source registration line without reordering unrelated entries. The branch was refreshed onto `beea2231a0ea66fd783260a3fdbfb71afec5d566` before validation.

## Validation plan

- table-driven outage-state and operation matrix;
- every `GameState_t` lifecycle value;
- explicit regular, `CanAlwaysLogin` and diagnostic capability cases;
- independent handoff classification;
- unknown enum rejection;
- repeated-input determinism and immutable-snapshot evidence;
- exact changed-path and no-runtime-wiring audit;
- exact-head CI, Required and autofix.

Database failure injection is not applicable because this package performs no database operation or runtime wiring.

## Non-goals

No live protocol wiring, database access, outage publication, reconnect, replay, retry, wait, session mutation, channel mutation, player drain, final-save orchestration, recovery probes, schema or deployment changes.

## Rollback

Revert the feature merge. Only the five declared paths belong to this package.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T21:42:00+02:00
head: 6941639ac1e0a9c93f7082e4e10adb23315ea0c7
head_scope: implementation and shared test registration before this task-record commit
branch: dudantas/prs-003c-login-handoff-admission-policy
pr: null
status: validating
context_routes:
  - production-resilience
  - database-outage
  - protocol-policy
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-login-handoff-admission-policy.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_policy.hpp
  - tests/unit/server/network/protocol/database_outage_admission_policy_test.cpp
  - tests/unit/server/CMakeLists.txt
proven:
  - PRS-003A and immutable outage snapshots are merged.
  - Issue 206 owns this pure-policy package.
  - No competing PRS-003C implementation was found.
  - The branch is refreshed onto current main beea2231a0ea66fd783260a3fdbfb71afec5d566.
  - One isolated constexpr policy, dedicated document and table-driven tests are implemented.
  - No live protocol, database, player, session or channel path was edited.
derived:
  - The supplied immutable values fully determine every policy decision.
unknown:
  - exact-head CI, Required and autofix results
conflicts: []
first_failure: null
rejected_hypotheses:
  - generic staff bypass
  - valid handoff implies outage safety
  - mutable global outage lookup
  - live protocol wiring
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003c-login-handoff-admission-policy.md
  - docs/architecture/prs-003c-login-handoff-admission-policy.md
  - src/server/network/protocol/database_outage_admission_policy.hpp
  - tests/unit/server/network/protocol/database_outage_admission_policy_test.cpp
  - tests/unit/server/CMakeLists.txt
validation:
  - command: startup and ownership audit
    result: PASS
    evidence: main, issue, branch, contracts, current lifecycle and handoff behavior verified
  - command: focused source and test matrix review
    result: PASS
    evidence: all outage states, supported operations, lifecycle values, capabilities and unknown values are covered
  - command: exact-head CI, Required and autofix
    result: NOT_RUN
    evidence: PR not yet opened
blockers: []
next_action: Open the feature PR, record its number, then validate exact final head CI and repository-required gates.
```
