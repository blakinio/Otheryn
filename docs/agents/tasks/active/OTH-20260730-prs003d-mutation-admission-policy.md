---
task_id: OTH-20260730-prs003d-mutation-admission-policy
status: active
branch: dudantas/prs-003d-a
base_branch: main
start_sha: 30ad4f41987481219faf43fdab51596a0bec4732
refreshed_base_sha: 35b1a3f5ffe775d2973df6f996f2a966e7d4d761
issue: "231"
feature_pr: "236"
created: 2026-07-30
updated: 2026-07-30
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-mutation-admission-policy.md
  - docs/architecture/prs-003d-mutation-admission-policy.md
  - src/game/database_outage_mutation_admission_policy.hpp
  - tests/unit/game/database_outage_mutation_admission_policy_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/architecture/prs-002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/archive/OTH-20260729-prs002j-final-player-save.md
  - docs/agents/tasks/archive/OTH-20260729-prs003c-login-handoff-integration.md
---

# PRS-003D-A pure mutation outage admission policy

## Current behavior inventory

- PRS-003A exposes immutable `DatabaseOutageSnapshot` values with `Healthy`, `Degraded`, `Draining` and `Maintenance` states.
- PRS-003B publishes classified runtime database failures without gating gameplay mutations.
- PRS-003C-B gates live login and handoff only; it excludes mutation admission and draining.
- PRS-002J provides the accepted bounded synchronous final-player-save boundary, but this slice does not invoke it.
- No prior pure mutation admission policy classified critical durable, ordinary durable or ephemeral/non-durable mutation operations.

## Accepted target contract

The header-only, database-independent policy evaluates one immutable outage snapshot, one explicit mutation operation class and the current `GameState_t`. It returns a deterministic allow/reject disposition, a fixed reason and the evaluated inputs.

Assuming lifecycle `GAME_STATE_NORMAL`:

- `Healthy`: allow all known mutation classes;
- `Degraded`: reject critical and ordinary durable mutations, allow only explicitly classified ephemeral/non-durable mutations;
- `Draining`: reject every mutation class;
- `Maintenance`: reject every mutation class;
- unknown operation or outage state: reject fail closed.

Lifecycle permits mutation evaluation only in `INIT` and `NORMAL`; all other and unknown lifecycle values reject fail closed.

## Explicit non-goals

- no runtime gameplay/economy call-site wiring;
- no global outage lookup inside the policy;
- no scheduler, deadline execution, disconnect, player removal, checkpoint or final-save invocation;
- no recovery probe, reconnect, ping, SQL retry or replay;
- no schema, migration, PRS-004 durable fencing, PRS-005 idempotency/ledger, deployment or production mutation;
- no caller-visible error framework or broad economy gating.

## Failure-injection plan

Database failure injection is not applicable. Deterministic unit tests inject every known and unknown operation, lifecycle and outage enum value, verify immutable input preservation and repeat identical evaluations.

## Rollback plan

Revert the feature merge. The package creates no persistent data, schema, runtime integration, credentials or deployment state.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T09:27:00+02:00
head: 2a7bb9ea5d5e86aa4473e3ba2a6bff0343e7062e
head_scope: exact validated implementation head before this governance-only evidence commit
branch: dudantas/prs-003d-a
pr: 236
status: merge-ready-pending-replacement-checks
context_routes:
  - production-resilience
  - database-outage
  - mutation-policy
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-mutation-admission-policy.md
  - docs/architecture/prs-003d-mutation-admission-policy.md
  - src/game/database_outage_mutation_admission_policy.hpp
  - tests/unit/game/database_outage_mutation_admission_policy_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - terminal PRS-003C-B and PRS-002J dependencies were read and satisfied before implementation
  - issue 231 and PR 236 are the unique PRS-003D-A records
  - current main 35b1a3f5ffe775d2973df6f996f2a966e7d4d761 differs from task-start main only by the disjoint coordinator-owned record
  - coordinator ownership is disjoint and its record was not modified
  - exact implementation head 2a7bb9ea5d5e86aa4473e3ba2a6bff0343e7062e passed CI 30521707135, Required 30521706962 and autofix 30521706932
  - full CI included fast checks, Lua tests, Linux release, Linux debug with CTest, Windows CMake, macOS and Docker
  - final feature diff contains exactly the five declared owned paths and was behind_by zero
  - PR 236 is open, mergeable and has no comments or review discussion
  - isolated C++20 syntax, constexpr, noexcept and trivially-copyable checks passed
  - no runtime, draining, checkpoint, recovery, schema, fencing, ledger or deployment integration is present
derived:
  - this governance-only evidence commit requires a complete replacement exact-head check set before merge
  - exact runtime mutation call sites remain intentionally unowned until terminal PRS-003D-A permits PRS-003D-B
unknown: []
conflicts: []
first_failure:
  marker: refreshed-head-autofix-replacement
  result: CONTAINED
  evidence: superseded runs were cancelled only because autofix replaced the head; replacement head 2a7bb9ea5d5e86aa4473e3ba2a6bff0343e7062e passed all gates
rejected_hypotheses:
  - runtime gameplay gating in D-A
  - allowing unknown operation or enum values
  - allowing durable mutations during degraded grace
  - invoking PRS-002 final save in the pure policy
  - editing the coordinator record
  - treating cancelled superseded runs as a code failure
changed_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-mutation-admission-policy.md
  - docs/architecture/prs-003d-mutation-admission-policy.md
  - src/game/database_outage_mutation_admission_policy.hpp
  - tests/unit/game/database_outage_mutation_admission_policy_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: live dependency and ownership preflight
    result: PASS
    evidence: no duplicate PRS-003D package or owned-path overlap existed at task start
  - command: isolated C++20 syntax and contract compile check
    result: PASS
    evidence: policy compiled as constexpr/noexcept and decision remained trivially copyable
  - command: exact implementation-head CI
    result: PASS
    evidence: CI 30521707135 succeeded on 2a7bb9ea5d5e86aa4473e3ba2a6bff0343e7062e
  - command: exact implementation-head Required
    result: PASS
    evidence: Required 30521706962 succeeded after CI completion on the same head
  - command: exact implementation-head autofix
    result: PASS
    evidence: autofix 30521706932 succeeded on the same head
  - command: final scope, freshness and discussion audit
    result: PASS
    evidence: five exact paths, behind_by zero, mergeable PR and empty discussion timeline
  - command: replacement checks for this governance-only commit
    result: PENDING
    evidence: any checkpoint-only commit is a new final head and must pass all applicable exact-head gates
blockers: []
next_action: require exact-head CI, Required and autofix for this governance-only commit, then repeat scope/freshness/discussion audit and expected-head squash merge PR 236
```
