---
task_id: OTH-20260730-prs003d-runtime-bank-mutation-gate
status: terminal
branch: dudantas/prs-003d-b
base_branch: main
start_sha: 704405c625278c7ec4d197ebd03e4c3d829c76ef
issue: "248"
feature_pr: "249"
feature_head_sha: c963aef818ff2fcf034cf9f979b2d2f415b26a15
feature_merge_sha: e18467d1f79e5388ec3bb824815dd8ecd0103c06
lifecycle_pr: "250"
lifecycle_head_sha: 49fe7e7b00ddfb5f3bcebd6409deea6932cf823f
lifecycle_merge_sha: a1e6181605d02049a9542d5b8352de2ff6266d0e
finalizer_pr: "251"
finalizer_head_sha: a2ee8ae5f9dbaccf3d5ddd58e254c41c7e0b0a09
finalizer_required_run: "30531918811"
finalizer_merge_sha: 9c8d59884e8128e5beb1473034b991489c07552a
created: 2026-07-30
updated: 2026-07-30
owned_paths:
  - docs/architecture/prs-003d-runtime-bank-mutation-gate.md
  - src/game/database_outage_mutation_gate.hpp
  - src/game/bank/bank.cpp
  - tests/unit/game/database_outage_mutation_gate_test.cpp
  - tests/unit/game/CMakeLists.txt
---

# PRS-003D-B runtime bank mutation gate

## Terminal result

PRS-003D-B is terminal. Feature PR #249 merged into `main` as `e18467d1f79e5388ec3bb824815dd8ecd0103c06`, issue #248 closed completed, lifecycle archive PR #250 merged as `a1e6181605d02049a9542d5b8352de2ff6266d0e`, and archive finalizer PR #251 merged as `9c8d59884e8128e5beb1473034b991489c07552a`.

The implementation:

- captures exactly one immutable outage snapshot per gated mutation attempt;
- evaluates the terminal PRS-003D-A policy with current lifecycle;
- invokes a caller-supplied boolean mutation at most once only after admission;
- classifies the shared bank-balance setter seam as `CriticalDurable`;
- rejects before `Bankable::setBankBalance()` and returns the existing caller-visible `false` value;
- keeps `Bank::credit`, `debit`, `transferTo`, `withdraw` and `deposit` routed through the gated balance setter;
- proves single capture, no post-rejection mutation, unknown-state fail-closed behavior, deterministic decisions, result preservation and live source ordering.

This package intentionally does not add broad economy, market, player-storage or generic Lua mutation gating. It adds no draining, checkpoint/final-save orchestration, recovery, reconnect, ping, replay, schema, migration, durable fencing, idempotency/ledger, deployment or production operation.

This archive-only metadata repair records historical finalizer evidence and changes no active task, coordinator, feature, architecture, runtime, test, schema or deployment path.

## Validation

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T11:50:00+02:00
status: terminal
feature_pr: 249
feature_head: c963aef818ff2fcf034cf9f979b2d2f415b26a15
feature_merge: e18467d1f79e5388ec3bb824815dd8ecd0103c06
lifecycle_pr: 250
lifecycle_head: 49fe7e7b00ddfb5f3bcebd6409deea6932cf823f
lifecycle_merge: a1e6181605d02049a9542d5b8352de2ff6266d0e
finalizer_pr: 251
finalizer_head: a2ee8ae5f9dbaccf3d5ddd58e254c41c7e0b0a09
finalizer_required: 30531918811
finalizer_merge: 9c8d59884e8128e5beb1473034b991489c07552a
issue: 248
issue_state: closed_completed
proven:
  - terminal PRS-003D-A was satisfied before D-B opened
  - final feature diff contains exactly the six declared paths
  - final feature base audit reported behind_by zero
  - feature PR comments, reviews and review threads were empty
  - expected-head squash merge protected exact feature head c963aef818ff2fcf034cf9f979b2d2f415b26a15
  - lifecycle PR changed only the active-record deletion and archive-record addition
  - lifecycle base audit reported behind_by zero
  - lifecycle PR comments, reviews and review threads were empty
  - active task record is absent from main after lifecycle merge
  - finalizer PR changed only this archive record
  - finalizer base audit reported behind_by zero
  - finalizer PR comments, reviews and review threads were empty
  - coordinator PR 239 and PRS-003E-A PR 238 remain on disjoint owned paths
  - no broad economy, draining, checkpoint, recovery, schema, fencing, ledger or deployment behavior was added
unknown: []
conflicts: []
validation:
  - command: autofix #573 on exact final feature head c963aef818ff2fcf034cf9f979b2d2f415b26a15
    result: PASS
    evidence: no replacement commit was produced
  - command: CI #663 on exact final feature head c963aef818ff2fcf034cf9f979b2d2f415b26a15
    result: PASS
    evidence: fast checks, Lua, Linux release/debug with CTest, Windows CMake/Solution, macOS and Docker completed successfully
  - command: Required #739 on the same exact feature head
    result: PASS
    evidence: Required accepted completed CI
  - command: final feature scope, freshness, mergeability and discussion audit
    result: PASS
    evidence: six exact paths, behind_by zero, mergeable non-draft PR and empty comments/reviews/threads
  - command: expected-head feature merge and issue audit
    result: PASS
    evidence: PR 249 merged as e18467d1f79e5388ec3bb824815dd8ecd0103c06 and issue 248 closed completed
  - command: lifecycle Required #741 on exact lifecycle head 49fe7e7b00ddfb5f3bcebd6409deea6932cf823f
    result: PASS
    evidence: no CI workflow was applicable to the two governance-only paths
  - command: lifecycle scope, freshness and discussion audit
    result: PASS
    evidence: exactly two lifecycle paths, behind_by zero and empty comments/reviews/threads
  - command: lifecycle merge and active-record audit
    result: PASS
    evidence: PR 250 merged as a1e6181605d02049a9542d5b8352de2ff6266d0e and the active record is absent from main
  - command: finalizer Required #743 on exact finalizer head a2ee8ae5f9dbaccf3d5ddd58e254c41c7e0b0a09
    result: PASS
    evidence: no CI workflow was applicable to the one archive-only path
  - command: finalizer scope, freshness, discussion and merge audit
    result: PASS
    evidence: PR 251 was one-file-only, behind_by zero, discussion-clean and merged as 9c8d59884e8128e5beb1473034b991489c07552a
blockers: []
next_action: none
```
