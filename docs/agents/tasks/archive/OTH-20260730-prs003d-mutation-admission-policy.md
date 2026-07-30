---
task_id: OTH-20260730-prs003d-mutation-admission-policy
status: terminal
branch: dudantas/prs-003d-a
base_branch: main
start_sha: 30ad4f41987481219faf43fdab51596a0bec4732
refreshed_base_sha: 35b1a3f5ffe775d2973df6f996f2a966e7d4d761
issue: "231"
feature_pr: "236"
feature_head_sha: 24b8bd872382b48f81c717ed98a8d0e3266dbe5d
feature_merge_sha: 7e7f3b65751a2348146286018454e428f7732c53
lifecycle_pr: pending
lifecycle_merge_sha: pending
created: 2026-07-30
updated: 2026-07-30
owned_paths:
  - docs/architecture/prs-003d-mutation-admission-policy.md
  - src/game/database_outage_mutation_admission_policy.hpp
  - tests/unit/game/database_outage_mutation_admission_policy_test.cpp
  - tests/unit/game/CMakeLists.txt
---

# PRS-003D-A pure mutation outage admission policy

## Terminal result

PRS-003D-A is complete. Feature PR #236 merged into `main` as `7e7f3b65751a2348146286018454e428f7732c53`, and issue #231 closed as completed.

The implementation:

- defines explicit critical durable, ordinary durable and ephemeral/non-durable mutation operation classes;
- evaluates one immutable caller-supplied `DatabaseOutageSnapshot` and current `GameState_t` only;
- allows all known mutation classes in `Healthy` where lifecycle permits;
- rejects critical and ordinary durable mutations in `Degraded` while allowing only explicitly classified ephemeral/non-durable operations during the finite grace;
- rejects every mutation in `Draining` and outage `Maintenance`;
- rejects unknown operation, lifecycle and outage enum values fail closed with fixed reasons;
- remains header-only, `constexpr`, `noexcept`, deterministic and free of I/O, mutable global state, runtime adapters or database access;
- includes deterministic full outage/lifecycle matrices, unknown-enum coverage, immutable-input evidence and repeated-evaluation evidence.

The package intentionally does not wire live gameplay/economy mutation gates, schedule checkpoints, invoke final save, drain players, disconnect sessions, probe recovery, reconnect, ping, replay SQL, change schema, add durable fencing, add idempotency/ledger behavior or alter deployment.

## Validation

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T09:55:00+02:00
status: terminal
feature_pr: 236
feature_head: 24b8bd872382b48f81c717ed98a8d0e3266dbe5d
feature_merge: 7e7f3b65751a2348146286018454e428f7732c53
lifecycle_pr: pending
lifecycle_merge: pending
issue: 231
issue_state: closed_completed
proven:
  - terminal PRS-003C-B and PRS-002J dependencies were satisfied before implementation
  - final feature diff contains exactly the five declared paths including the active task record
  - final base audit reported behind_by zero
  - PR comments, reviews and review threads were empty
  - expected-head squash merge protected exact head 24b8bd872382b48f81c717ed98a8d0e3266dbe5d
  - open PRS-003E-A PR 238 owns four disjoint integration/workflow paths
  - open coordinator PR 239 owns only docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
  - coordinator record was not modified by Agent 1
  - no runtime mutation wiring, draining, checkpoint invocation, recovery, schema, fencing, ledger or deployment change was added
validation:
  - command: isolated C++20 syntax and pure-contract compile check
    result: PASS
    evidence: constexpr/noexcept evaluation and trivially-copyable decision were proven
  - command: CI #654 on exact final head 24b8bd872382b48f81c717ed98a8d0e3266dbe5d
    result: PASS
    evidence: Fast Checks, Lua, Linux release, Linux debug with CTest, Windows CMake, macOS and Docker completed successfully
  - command: Required #719
    result: PASS
    evidence: required workflow accepted the exact final feature head after full CI completion
  - command: autofix #565
    result: PASS
    evidence: no replacement commit was produced for the final feature head
  - command: final scope, freshness, mergeability and discussion audit
    result: PASS
    evidence: five exact paths, behind_by zero, mergeable non-draft PR and empty comments/reviews/threads
  - command: expected-head feature merge and issue audit
    result: PASS
    evidence: PR 236 merged as 7e7f3b65751a2348146286018454e428f7732c53 and issue 231 closed completed
blockers: []
next_action: merge this lifecycle archive PR, then record its PR number and merge SHA in one archive-only finalizer
```
