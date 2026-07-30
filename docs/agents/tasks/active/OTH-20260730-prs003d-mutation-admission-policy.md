---
task_id: OTH-20260730-prs003d-mutation-admission-policy
status: active
branch: dudantas/prs-003d-a
base_branch: main
start_sha: 30ad4f41987481219faf43fdab51596a0bec4732
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
- PRS-003B publishes classified runtime database failures to the process-level state owner without gating gameplay mutations.
- PRS-003C-B gates live login and handoff only; it explicitly excludes mutation admission and draining.
- PRS-002J provides the accepted bounded synchronous final-player-save boundary, but this slice does not invoke it.
- No existing pure mutation admission policy classifies critical durable, ordinary durable or ephemeral/non-durable mutation operations.

## Accepted target contract

Add one header-only, database-independent policy that evaluates an immutable outage snapshot, an explicit mutation operation class and the current `GameState_t`. It returns a deterministic allow/reject disposition, a fixed reason and the evaluated input classes.

Assuming lifecycle `GAME_STATE_NORMAL`:

- `Healthy`: allow all known mutation classes;
- `Degraded`: reject critical and ordinary durable mutations, allow only explicitly classified ephemeral/non-durable mutations;
- `Draining`: reject every mutation class;
- `Maintenance`: reject every mutation class;
- unknown operation or outage state: reject fail closed.

Lifecycle rules:

- allow mutation evaluation only in `INIT` and `NORMAL`;
- reject `STARTUP`, `CLOSING`, `CLOSED`, `SHUTDOWN` and `MAINTAIN` with fixed reasons;
- reject unknown lifecycle values fail closed.

## Explicit non-goals

- no runtime gameplay or economy call-site wiring;
- no global outage lookup inside the policy;
- no scheduler, deadline execution, disconnect, player removal, checkpoint or final-save invocation;
- no recovery probe, reconnect, ping, SQL retry or replay;
- no schema, migration, PRS-004 durable fencing, PRS-005 idempotency/ledger, deployment or production mutation;
- no caller-visible error framework and no broad economy gating.

## Failure-injection plan

Database failure injection is not applicable to this pure slice. Deterministic unit tests inject every known and unknown operation, lifecycle and outage enum value, verify immutable input preservation and repeat identical evaluations.

## Rollback plan

Revert the feature merge. The package creates no persistent data, schema, runtime integration, credentials or deployment state.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T08:41:00+02:00
head: dc735160ae9b0dfa42bde8abbf0aabe35e163203
branch: dudantas/prs-003d-a
pr: 236
status: validating
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
  - main baseline 30ad4f41987481219faf43fdab51596a0bec4732 contains terminal PRS-003C-B archive metadata
  - issue 231 is the only discovered PRS-003D-A issue
  - no open pull request or dudantas/prs-003d branch existed at task start
  - active task directory was absent on main and no owned-path overlap was discovered
  - feature diff contains exactly the five declared paths and was behind_by zero at PR creation
  - isolated C++20 syntax, constexpr, noexcept and trivially-copyable checks passed
  - PR 236 is open from dudantas/prs-003d-a to main
derived:
  - the pure policy is ready for repository exact-head validation
unknown:
  - exact runtime mutation call sites remain intentionally unowned until PRS-003D-B
conflicts: []
first_failure: null
rejected_hypotheses:
  - runtime gameplay gating in D-A
  - allowing unknown operation or enum values
  - allowing durable mutations during degraded grace
  - invoking PRS-002 final save in the pure policy
changed_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-mutation-admission-policy.md
  - docs/architecture/prs-003d-mutation-admission-policy.md
  - src/game/database_outage_mutation_admission_policy.hpp
  - tests/unit/game/database_outage_mutation_admission_policy_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: live dependency and ownership preflight
    result: PASS
    evidence: terminal PRS-003C-B and PRS-002J archives read; no open PR or PRS-003D branch found
  - command: isolated C++20 syntax and constexpr/noexcept compile check
    result: PASS
    evidence: policy compiled and executed against minimal accepted enum contracts
  - command: repository CI, Required and autofix on exact final head
    result: NOT_RUN
    evidence: PR 236 opened and checks are pending
blockers: []
next_action: inspect PR 236 exact-head CI, Required and autofix results; fix only confirmed failures inside the declared five paths
```
