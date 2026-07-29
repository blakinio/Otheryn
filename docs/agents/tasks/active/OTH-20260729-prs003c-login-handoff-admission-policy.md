---
task_id: OTH-20260729-prs003c-login-handoff-admission-policy
status: validating
branch: dudantas/prs-003c-login-handoff-admission-policy
base_branch: main
start_sha: 6a6007667dfd82010b0240342180961cd553466f
rebased_onto_sha: 97bd35040ca8551ed0a7a62e60525ba696bf6259
created: 2026-07-29
updated: 2026-07-29
related_issue: "206"
related_pr: "213"
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

`tests/unit/server/CMakeLists.txt` is shared. The package adds one source registration line without reordering unrelated entries. The branch was refreshed onto `97bd35040ca8551ed0a7a62e60525ba696bf6259` before exact-head validation.

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
updated_at: 2026-07-29T22:00:00+02:00
head: 332d482a31ed5c01bc02e2d1c206117197654fa2
head_scope: code-fix head before recording the confirmed compile failure and its correction
branch: dudantas/prs-003c-login-handoff-admission-policy
pr: 213
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
  - Issue 206 and PR 213 own this pure-policy package.
  - No competing PRS-003C implementation was found.
  - The branch is refreshed onto main 97bd35040ca8551ed0a7a62e60525ba696bf6259.
  - One isolated constexpr policy, dedicated document and table-driven tests are implemented.
  - No live protocol, database, player, session or channel path was edited.
  - Linux Release compiled and completed Canary and Global smoke tests on the pre-fix head.
derived:
  - The supplied immutable values fully determine every policy decision.
unknown:
  - replacement exact-head CI, Required and autofix results after the bounded test-helper correction
conflicts: []
first_failure:
  marker: linux-debug static_assert noexcept at database_outage_admission_policy_test.cpp line 44
  evidence: the noexcept expression included makeSnapshot, whose test-helper declaration lacked noexcept
rejected_hypotheses:
  - policy evaluate is not noexcept
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
  - command: branch freshness and shared-path refresh
    result: PASS
    evidence: current main 97bd35040ca8551ed0a7a62e60525ba696bf6259 merged without feature-path conflict
  - command: checkpoint schema audit
    result: PASS
    evidence: required first_failure marker and evidence mapping are present
  - command: CI 30485660238 linux-release
    result: PASS
    evidence: build, generated-doc check, Canary smoke and Global smoke succeeded
  - command: CI 30485660238 linux-debug
    result: FAIL
    evidence: static_assert evaluated the non-noexcept makeSnapshot helper before calling the noexcept policy
  - command: bounded compile correction
    result: PASS
    evidence: makeSnapshot is now explicitly constexpr noexcept; production policy code is unchanged
  - command: replacement exact-head CI, Required and autofix
    result: NOT_RUN
    evidence: this checkpoint update creates the final validation head
blockers: []
next_action: Validate CI, Required and autofix on the exact PR 213 head, then audit current-main drift, scope and discussions before expected-head squash merge.
```
