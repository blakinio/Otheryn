---
task_id: OTH-20260730-prs003d-runtime-bank-mutation-gate
status: validating
branch: dudantas/prs-003d-b
base_branch: main
start_sha: 704405c625278c7ec4d197ebd03e4c3d829c76ef
issue: "248"
feature_pr: "249"
created: 2026-07-30
updated: 2026-07-30
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-runtime-bank-mutation-gate.md
  - docs/architecture/prs-003d-runtime-bank-mutation-gate.md
  - src/game/database_outage_mutation_gate.hpp
  - src/game/bank/bank.cpp
  - tests/unit/game/database_outage_mutation_gate_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/architecture/prs-003d-mutation-admission-policy.md
  - docs/agents/tasks/archive/OTH-20260730-prs003d-mutation-admission-policy.md
  - docs/agents/tasks/archive/OTH-20260729-prs002j-final-player-save.md
---

# PRS-003D-B runtime bank mutation gate

## Current behavior inventory

- Terminal PRS-003D-A exposes a pure fail-closed mutation admission policy over one immutable outage snapshot and current lifecycle.
- The accepted process snapshot seam is `getDatabaseOutageSnapshot()`.
- `Bank::credit`, `debit`, `transferTo`, `withdraw` and `deposit` route balance updates through `Bank::balance(uint64_t)`.
- Before this slice, `Bank::balance(uint64_t)` called `Bankable::setBankBalance()` without consulting database-outage state.
- Player storage and broad gameplay/economy entry points are intentionally outside this slice.

## Accepted target contract

One runtime adapter captures exactly one immutable snapshot, evaluates the PRS-003D-A policy and invokes a caller-supplied boolean mutation at most once only when admitted. `Bank::balance(uint64_t)` is explicitly `CriticalDurable`, evaluates before `setBankBalance()` and preserves the existing caller-visible boolean result.

## Explicit non-goals

- no broad economy, market, player-storage or generic Lua mutation gating;
- no draining, disconnect, player removal, checkpoint or final-save orchestration;
- no recovery probe, resume, reconnect, ping, SQL retry or replay;
- no schema, migration, durable fencing, idempotency/ledger, deployment or production operation;
- no coordinator or PRS-003E-A path changes.

## Failure-injection plan

Deterministic unit tests inject healthy, degraded, draining, maintenance, disallowed lifecycle and unknown enum inputs. They count snapshot captures and mutation invocations, prove no post-rejection mutation, preserve a permitted mutation's `false` result, verify immutable snapshot preservation and inspect the live bank source ordering.

## Rollback plan

Revert the feature merge. The slice adds no persistent data, schema, credentials, deployment state, draining or recovery behavior.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T10:52:00+02:00
head: 5ea4d31520ef8dae61bb1974ae7ccfc69198e1e2
head_scope: exact six-path implementation head before this PR-link checkpoint update
branch: dudantas/prs-003d-b
pr: 249
status: validating
context_routes:
  - production-resilience
  - database-outage
  - mutation-admission
  - bank
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-runtime-bank-mutation-gate.md
  - docs/architecture/prs-003d-runtime-bank-mutation-gate.md
  - src/game/database_outage_mutation_gate.hpp
  - src/game/bank/bank.cpp
  - tests/unit/game/database_outage_mutation_gate_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - PRS-003D-A is terminal on main with complete archive metadata.
  - Issue 248, branch dudantas/prs-003d-b and PR 249 are the unique D-B package records.
  - Coordinator PR 239 owns only its coordinator record.
  - PRS-003E-A PR 238 owns four disjoint workflow and integration-test paths.
  - The feature diff contains exactly the six declared paths and is behind_by zero.
  - Bank balance writes converge on Bank::balance(uint64_t) before Bankable::setBankBalance().
  - The adapter captures one immutable snapshot and invokes the boolean mutation at most once only after admission.
  - The live bank seam uses CriticalDurable, current lifecycle and the accepted process snapshot before the setter.
  - No draining, checkpoint, recovery, schema, fencing, ledger or deployment behavior is present.
derived:
  - one gated bank-balance seam is the smallest reviewable critical-durable runtime slice
unknown:
  - exact final feature head and repository CI evidence after this checkpoint update
conflicts: []
first_failure: null
rejected_hypotheses:
  - broad economy gating in one PR
  - player-storage gating through a void-returning broad seam
  - draining or checkpoint orchestration in D-B
  - touching coordinator or PRS-003E-A paths
changed_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003d-runtime-bank-mutation-gate.md
  - docs/architecture/prs-003d-runtime-bank-mutation-gate.md
  - src/game/database_outage_mutation_gate.hpp
  - src/game/bank/bank.cpp
  - tests/unit/game/database_outage_mutation_gate_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: live dependency and ownership audit
    result: PASS
    evidence: terminal D-A; no D-B duplicate; active coordinator and E-A ownership is disjoint
  - command: six-path scope and source ordering audit
    result: PASS
    evidence: behind_by zero; live bank gate appears before setBankBalance and returns the mutation result
  - command: exact-final-head CI, Required and autofix
    result: NOT_RUN
    evidence: PR 249 opened and replacement checks are pending after this checkpoint update
blockers: []
next_action: require exact-final-head CI, Required and autofix for PR 249, then repeat scope, freshness and discussion audits
```
