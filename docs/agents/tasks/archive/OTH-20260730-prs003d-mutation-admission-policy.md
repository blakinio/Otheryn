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
lifecycle_pr: "244"
lifecycle_merge_sha: 1ecffdb1c1dfbffabf2bded78de7f8b0f09774c9
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

PRS-003D-A is complete. Feature PR #236 merged into `main` as `7e7f3b65751a2348146286018454e428f7732c53`, issue #231 closed as completed, and lifecycle archive PR #244 merged as `1ecffdb1c1dfbffabf2bded78de7f8b0f09774c9`.

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
updated_at: 2026-07-30T10:05:00+02:00
status: terminal
feature_pr: 236
feature_head: 24b8bd872382b48f81c717ed98a8d0e3266dbe5d
feature_merge: 7e7f3b65751a2348146286018454e428f7732c53
lifecycle_pr: 244
lifecycle_head: 5e245f453235508e198656123a4a88c8d34959a3
lifecycle_merge: 1ecffdb1c1dfbffabf2bded78de7f8b0f09774c9
issue: 231
issue_state: closed_completed
proven:
  - terminal PRS-003C-B and PRS-002J dependencies were satisfied before implementation
  - final feature diff contains exactly the five declared paths including the active task record
  - final feature base audit reported behind_by zero
  - feature PR comments, reviews and review threads were empty
  - expected-head squash merge protected exact feature head 24b8bd872382b48f81c717ed98a8d0e3266dbe5d
  - lifecycle PR changed only the active-record deletion and archive-record addition
  - lifecycle base audit reported behind_by zero
  - lifecycle PR comments, reviews and review threads were empty
  - active task record is absent from main after lifecycle merge
  - open PRS-003E-A and coordinator work remain on disjoint owned paths
  - coordinator record was not modified by Agent 1
  - no runtime mutation wiring, draining, checkpoint invocation, recovery, schema, fencing, ledger or deployment change was added
validation:
  - command: isolated C++20 syntax and pure-contract compile check
    result: PASS
    evidence: constexpr/noexcept evaluation and trivially-copyable decision were proven
  - command: CI #654 on exact final feature head 24b8bd872382b48f81c717ed98a8d0e3266dbe5d
    result: PASS
    evidence: Fast Checks, Lua, Linux release, Linux debug with CTest, Windows CMake, macOS and Docker completed successfully
  - command: Required #719
    result: PASS
    evidence: required workflow accepted the exact final feature head after full CI completion
  - command: autofix #565
    result: PASS
    evidence: no replacement commit was produced for the final feature head
  - command: final feature scope, freshness, mergeability and discussion audit
    result: PASS
    evidence: five exact paths, behind_by zero, mergeable non-draft PR and empty comments/reviews/threads
  - command: expected-head feature merge and issue audit
    result: PASS
    evidence: PR 236 merged as 7e7f3b65751a2348146286018454e428f7732c53 and issue 231 closed completed
  - command: lifecycle Required #728 on exact head 5e245f453235508e198656123a4a88c8d34959a3
    result: PASS
    evidence: no CI workflow was applicable to the two governance-only paths
  - command: lifecycle scope, freshness and discussion audit
    result: PASS
    evidence: exactly two lifecycle paths, behind_by zero and empty comments/reviews/threads
  - command: lifecycle merge and active-record audit
    result: PASS
    evidence: PR 244 merged as 1ecffdb1c1dfbffabf2bded78de7f8b0f09774c9 and the active record is absent from main
blockers: []
next_action: none
```
