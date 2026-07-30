---
task_id: OTH-20260730-prs003e-a-disposable-mariadb-outage-injector
status: completed
branch: dudantas/prs-003e-a
base_branch: main
start_sha: 30ad4f41987481219faf43fdab51596a0bec4732
feature_head: 91f90c9325cbabcfd67d16e09317daa4aea1b47b
feature_merge_sha: 09297920ffa15feea2a05b24909d58b8e2a33e2a
created: 2026-07-30
updated: 2026-07-30
completed: 2026-07-30
related_issue: "232"
related_pr: "238"
lifecycle_pr: pending
lifecycle_merge_sha: pending
owned_paths:
  - .github/workflows/prs-003e-database-outage.yml
  - tests/integration/prs_003e/database_outage_injector.cpp
  - tests/integration/prs_003e/run_disposable_mariadb_outage.sh
  - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
---

# PRS-003E-A disposable MariaDB outage injector

## Result

Feature PR #238 merged into `main` as `09297920ffa15feea2a05b24909d58b8e2a33e2a`. Issue #232 closed as completed. This lifecycle change moves the durable task record from `active` to `archive` without changing the feature implementation.

## Proven evidence

- disposable loopback-only MariaDB 11.4 is created and removed by a dedicated test runner;
- a killed in-flight query proves `CR_SERVER_LOST`;
- the next one-shot operation on the same dead handle proves `CR_SERVER_GONE_ERROR`;
- transaction begin failure is known-not-committed;
- transaction commit and rollback failures have unknown commit outcome;
- an ordinary query failure is known-not-committed;
- failures publish fixed reason, outcome, event reason and monotonic sequence through the accepted PRS-003 seams;
- caller-visible `false` is preserved;
- each operation is attempted once, no failed write is replayed and no evidence row remains committed;
- no reconnect API, `MYSQL_OPT_RECONNECT`, `mysql_ping`, retry loop or automatic resume exists in the harness.

## Exact-head validation

Feature head `91f90c9325cbabcfd67d16e09317daa4aea1b47b` passed:

- disposable MariaDB evidence run `30578360334`;
- full CI run `30578360728`, including Linux release/debug, Windows CMake/Solution, macOS, smoke tests and Linux debug CTest;
- Required run `30578360313`;
- autofix run `30578360325` with no corrective commit.

Final feature audit proved `behind_by=0`, exactly four owned paths, a mergeable non-draft PR and no comments, reviews or review threads.

## Safety boundaries

- no production source or production fault injection;
- no `src/database/database.cpp` or state-machine contract change;
- no existing test CMake registration change;
- no reconnect, ping, replay or retry framework;
- no recovery probe runtime or operator resume implementation;
- no mutation admission, draining or final-save orchestration;
- no schema migration, persistent database state, real credential or public database port;
- no PRS-004+ work and no RPO/RTO claim.

## Remaining program order

- PRS-003E-B opens after terminal PRS-003E-A;
- PRS-003E-C opens after terminal PRS-003E-B;
- terminal PRS-003D plus terminal PRS-003E open durable PRS-004;
- an additional PRS-003E slice is allowed only if controlled evidence proves a real gap.

## Rollback

Revert feature merge `09297920ffa15feea2a05b24909d58b8e2a33e2a`. No persistent data, schema, credentials or deployment state requires reversal.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T22:52:00+02:00
head: pending-lifecycle-head
head_scope: active-to-archive lifecycle candidate after feature merge 09297920
branch: dudantas/prs-003e-a-archive
pr: pending
status: validating
context_routes:
  - production-resilience
  - database
  - failure-injection
  - controlled-runtime
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
  - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
proven:
  - Feature PR 238 merged exact head 91f90c9325cbabcfd67d16e09317daa4aea1b47b as 09297920ffa15feea2a05b24909d58b8e2a33e2a.
  - Issue 232 is closed completed.
  - Exact-head MariaDB 30578360334, CI 30578360728, Required 30578360313 and autofix 30578360325 passed.
  - Feature diff was exactly four declared test/workflow/task paths and behind_by was zero.
  - Feature discussions, reviews and review threads were empty.
  - No production source, reconnect, replay, recovery runtime, schema or PRS-004+ work was added.
derived:
  - PRS-003E-A supplies controlled runtime evidence without changing runtime recovery policy.
unknown:
  - Lifecycle PR number, lifecycle Required run and lifecycle merge SHA.
  - Finalizer PR number, Required run and merge SHA.
conflicts: []
first_failure:
  marker: rollback-failure-reason-mismatch
  result: CONTAINED
  evidence: Initial controlled evidence proved rollback failure is connection-scoped with unknown outcome; the test expectation was corrected without production changes.
rejected_hypotheses:
  - production fault injection
  - reconnect or replay after connection loss
  - recovery runtime in PRS-003E-A
  - automatic resume
  - schema or deployment changes
changed_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
  - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
validation:
  - command: feature exact-head MariaDB, CI, Required and autofix
    result: PASS
    evidence: Runs 30578360334, 30578360728, 30578360313 and 30578360325 succeeded on 91f90c9325cbabcfd67d16e09317daa4aea1b47b.
  - command: feature scope, freshness and discussion audit
    result: PASS
    evidence: Four paths, behind_by zero, mergeable non-draft PR and no discussion items.
  - command: lifecycle Required and final audit
    result: NOT_RUN
    evidence: Lifecycle PR has not yet been opened.
blockers: []
next_action: Open and validate the active-to-archive lifecycle PR, merge it expected-head, then create one-file terminal finalizer.
```
