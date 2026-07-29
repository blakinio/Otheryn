---
task_id: OTH-20260729-prs003-database-outage-contract
status: completed
branch: main
base_branch: main
start_sha: d09b4f04887a74e31f9e47a82c1c96ab91d33325
created: 2026-07-29
updated: 2026-07-29
related_issue: "195"
related_pr: "196"
feature_head: 18bf7d6856577033d23f2b2c3ee2a3c2fd84a0a3
feature_merge_sha: 7c437707288a4004af47752863c26751e35c3b72
lifecycle_pr: null
lifecycle_head: null
lifecycle_merge_sha: null
owned_paths:
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - tests/unit/game/prs_003_database_outage_contract_test.cpp
  - tests/unit/game/CMakeLists.txt
---

# PRS-003 database-outage state-machine discovery

## Completed outcome

The bounded PRS-003 discovery milestone proved the live database-failure boundaries and accepted one deterministic fail-closed target contract before runtime implementation.

## Proven current behavior

- startup database connection or migration failure aborts normal startup;
- implicit MySQL reconnect and arbitrary SQL statement replay are disabled;
- runtime `Database` failures log and return `false` or `nullptr` without publishing a central outage transition;
- asynchronous database tasks do not change process-level database-health state;
- `GameState_t` has no degraded or draining state;
- login gates are driven by the existing lifecycle state, not database health;
- PRS-002 bounded final saves exist, but no outage controller currently decides admission or draining.

## Accepted target contract

- one database-independent state machine owns `HEALTHY`, `DEGRADED`, `DRAINING` and `MAINTENANCE` policy state;
- transitions use fixed classified events and low-cardinality reasons, never parsed log text;
- a first known-not-committed runtime failure enters degraded with one finite deadline;
- unknown commit outcome, repeated qualifying failure or degraded-deadline expiry enters draining without replay;
- draining closes durable admission, uses bounded PRS-002 final saves and has one finite drain deadline;
- maintenance never auto-resumes;
- explicit recovery requires bounded read and transactional write/rollback evidence plus an operator recovery decision;
- automatic database promotion, automatic whole-world rollback and arbitrary replay remain forbidden.

## Validation evidence

- feature PR: #196;
- exact feature head: `18bf7d6856577033d23f2b2c3ee2a3c2fd84a0a3`;
- feature squash merge: `7c437707288a4004af47752863c26751e35c3b72`;
- final exact-head CI: `30467582765` — PASS;
- final exact-head Required: `30467582613` — PASS;
- final exact-head autofix: `30467582325` — PASS;
- Linux debug passed disposable schema import and full CTest;
- Linux release, Windows Solution, Windows CMake and macOS passed applicable build and smoke gates;
- final feature audit: exactly four owned paths, `behind_by=0`, no comments, reviews, review threads or requested reviewers;
- issue #195 closed as completed.

## Failure and correction record

The pre-validation source-contract audit found that the test required an explicit prohibition on automatic database promotion while the contract used shorter wording. The contract was clarified before the final exact-head validation. One CI attempt was also cancelled by workflow concurrency and was rerun successfully without a source change.

## Non-goals preserved

- no runtime outage-state implementation;
- no reconnect, query replay or connection pool;
- no schema, migration, production database, credential or deployment mutation;
- no PRS-004 fencing, PRS-005 idempotency, PRS-006 reconciliation, PRS-007 failover or PRS-008 Compose change;
- no production RPO/RTO claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T18:15:00+02:00
head: 7c437707288a4004af47752863c26751e35c3b72
head_scope: feature merge on main before lifecycle archive merge
branch: dudantas/archive-prs-003-database-outage-contract
pr: null
status: archiving
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
  - docs/agents/tasks/archive/OTH-20260729-prs003-database-outage-contract.md
proven:
  - PR 196 merged from exact head 18bf7d6856577033d23f2b2c3ee2a3c2fd84a0a3 as 7c437707288a4004af47752863c26751e35c3b72.
  - Exact-head CI 30467582765, Required 30467582613 and autofix 30467582325 passed.
  - Feature audit found exactly four owned paths, behind_by zero and no discussion or review items.
  - Issue 195 closed as completed.
  - The accepted next implementation is Slice A, a pure database-independent state machine with deterministic tests and no runtime wiring.
derived:
  - The discovery milestone requires no further implementation or feature validation.
unknown:
  - Lifecycle archive PR number, head, Required result and merge SHA.
conflicts: []
first_failure:
  marker: pre-validation automatic-database-promotion wording mismatch
  evidence: Clarified before final validation; all exact-head checks passed.
rejected_hypotheses:
  - reconnect and replay arbitrary SQL
  - overload GAME_STATE_CLOSED with outage semantics
  - disconnect everyone immediately on the first failed statement
  - auto-resume after one successful query
  - combine PRS-003 with PRS-004 through PRS-008
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs003-database-outage-contract.md
  - docs/agents/tasks/archive/OTH-20260729-prs003-database-outage-contract.md
validation:
  - command: feature exact-head CI, Required and autofix
    result: PASS
    evidence: Runs 30467582765, 30467582613 and 30467582325 succeeded on 18bf7d6856577033d23f2b2c3ee2a3c2fd84a0a3.
  - command: feature final audit and expected-head merge
    result: PASS
    evidence: Four owned paths, behind_by zero, no discussion items and squash merge 7c437707288a4004af47752863c26751e35c3b72.
  - command: lifecycle archive move and Required
    result: NOT_RUN
    evidence: Archive branch has just been created.
blockers: []
next_action: Remove the active record, open the two-path lifecycle archive PR, validate Required on its exact head and merge with expected-head protection.
```
