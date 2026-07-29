---
task_id: OTH-20260729-prs003-database-outage-contract
status: completed
branch: main
base_branch: main
start_sha: d09b4f04887a74e31f9e47a82c1c96ab91d33325
feature_head: 18bf7d6856577033d23f2b2c3ee2a3c2fd84a0a3
feature_merge_sha: 7c437707288a4004af47752863c26751e35c3b72
lifecycle_pr: "197"
lifecycle_head: d81e29f76632b6c1a917734a3f1316d38b859193
lifecycle_merge_sha: 814acc85294060dd2f0c951a45428067bfcebd47
created: 2026-07-29
updated: 2026-07-29
completed: 2026-07-29
related_issue: "195"
related_pr: "196"
owned_paths:
  - docs/agents/tasks/archive/OTH-20260729-prs003-database-outage-contract.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - tests/unit/game/CMakeLists.txt
---

# PRS-003 database-outage state-machine discovery — completed

## Result

The bounded PRS-003 discovery package is complete. It records the proven startup and runtime database-failure behavior, accepts the deterministic `HEALTHY`, `DEGRADED`, `DRAINING` and `MAINTENANCE` contract, and adds focused source-contract validation without changing production runtime behavior.

Feature PR #196 was squash-merged into `main` as `7c437707288a4004af47752863c26751e35c3b72`. Issue #195 closed automatically as completed. Lifecycle PR #197 was squash-merged as `814acc85294060dd2f0c951a45428067bfcebd47`.

## Proven behavior

- startup database connection or migration failure remains fail closed;
- implicit reconnect and arbitrary SQL replay remain disabled;
- runtime database failures return local failure and do not currently publish a process-level outage transition;
- existing game lifecycle and login gates are not database-health policy;
- the accepted contract uses explicit classified events, immutable first-failure timing, finite degraded and drain deadlines, fail-closed admission, bounded PRS-002 final saves, explicit recovery evidence and low-cardinality observability;
- unknown commit outcomes never authorize replay;
- the next implementation slice is a database-independent pure state machine, not runtime wiring.

## Validation

Exact feature head: `18bf7d6856577033d23f2b2c3ee2a3c2fd84a0a3`.

- CI `30467582765`: PASS;
- Required `30467582613`: PASS;
- autofix `30467582325`: PASS;
- Fast Checks and Lua tests: PASS;
- Linux debug full CTest and database-backed applicable tests: PASS;
- Linux release, Windows Solution, Windows CMake and macOS compile/smoke jobs: PASS;
- changed-path audit: exactly the four declared feature paths;
- base drift audit: `behind_by=0` immediately before feature merge;
- feature PR comments, reviews, unresolved threads and requested reviewers: none;
- lifecycle PR #197 exact head `d81e29f76632b6c1a917734a3f1316d38b859193`;
- lifecycle Required `30469723858`: PASS;
- lifecycle PR changed exactly the active/archive task pair and had no discussion items;
- duplicate lifecycle PR #198 was closed unmerged after #197 became canonical.

Earlier workflow results belong to superseded heads and are not merge evidence for the final feature head.

## Safety boundaries preserved

- no runtime outage controller or gameplay admission change;
- no database, schema, migration, credential, secret, production host or deployment mutation;
- no connection pool, reconnect, arbitrary query replay, automatic process restart, automatic database promotion or whole-world rollback;
- no unbounded retry or wait;
- no PRS-004 fencing, PRS-005 idempotency, PRS-006 reconciliation, PRS-007 failover or PRS-008 production Compose work;
- no production RPO or RTO claim.

## Rollback

Revert feature merge `7c437707288a4004af47752863c26751e35c3b72`. The package changes only documentation, one deterministic source-contract test and its CMake registration. Revert lifecycle merge `814acc85294060dd2f0c951a45428067bfcebd47` only if task-record placement itself must be restored.

## Remaining parent-program gaps

The following remain separate future packages and are not implied complete by this record:

- PRS-003 runtime state-machine implementation and controlled draining;
- PRS-004 channel handoff, stale-writer prevention and session/revision fencing;
- durable restart reconciliation;
- measured production RPO;
- production alert thresholds and operational rollout.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T18:20:00+02:00
head: 814acc85294060dd2f0c951a45428067bfcebd47
head_scope: final lifecycle archive merge on main; this record-only terminal correction does not alter feature behavior or validation evidence
branch: dudantas/finalize-prs003-archive-state
pr: null
status: completed
feature_pr: 196
feature_head: 18bf7d6856577033d23f2b2c3ee2a3c2fd84a0a3
feature_merge_sha: 7c437707288a4004af47752863c26751e35c3b72
lifecycle_pr: 197
lifecycle_head: d81e29f76632b6c1a917734a3f1316d38b859193
lifecycle_merge_sha: 814acc85294060dd2f0c951a45428067bfcebd47
issue: 195
issue_state: closed_completed
ci_run: 30467582765
required_run: 30467582613
autofix_run: 30467582325
lifecycle_required_run: 30469723858
proven:
  - Feature PR 196 merged from its exact validated head and issue 195 closed as completed.
  - Lifecycle PR 197 passed Required and merged; the active task record is absent and this archive record is present on main.
  - Duplicate lifecycle PR 198 is closed without merge.
unknown:
  - Runtime PRS-003 implementation and all later parent-program packages remain separately scoped work.
blockers: []
next_action: No further action is required for the PRS-003 discovery contract; start PRS-003 Slice A only as a separately scoped pure database-independent state-machine task with a fresh preflight.
```
