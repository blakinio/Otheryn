---
task_id: OTH-20260730-prs003e-a-disposable-mariadb-outage-injector
status: terminal
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
lifecycle_pr: "258"
lifecycle_head: 4f00a739166e306ece09f76bde5148b9bc119bc1
lifecycle_required_run: 30580880580
lifecycle_merge_sha: c308f175d4988ac30cfc296c0de16d3389f5a18f
finalizer_pr: "259"
finalizer_head: 04ca821c031eb8b15c0c567441789a2cd66f4740
finalizer_required_run: 30581120699
finalizer_merge_sha: 1fecde7768deeef4fa8af763fd4c56e41eb3363c
owned_paths:
  - .github/workflows/prs-003e-database-outage.yml
  - tests/integration/prs_003e/database_outage_injector.cpp
  - tests/integration/prs_003e/run_disposable_mariadb_outage.sh
  - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
---

# PRS-003E-A disposable MariaDB outage injector

## Terminal result

PRS-003E-A is complete and terminal. Feature PR #238 merged exact head `91f90c9325cbabcfd67d16e09317daa4aea1b47b` as `09297920ffa15feea2a05b24909d58b8e2a33e2a`; issue #232 closed completed. Lifecycle PR #258 passed Required `30580880580` and merged as `c308f175d4988ac30cfc296c0de16d3389f5a18f`. One-file finalizer PR #259 passed Required `30581120699` and merged as `1fecde7768deeef4fa8af763fd4c56e41eb3363c`.

## Proven evidence

- disposable loopback-only MariaDB 11.4 is created and removed by a dedicated test runner;
- a killed in-flight query proves `CR_SERVER_LOST`;
- the next one-shot operation on the same dead handle proves `CR_SERVER_GONE_ERROR`;
- transaction begin failure and ordinary query failure are known-not-committed;
- transaction commit and rollback failures have unknown commit outcome;
- failures publish fixed reason, outcome, event reason and monotonic sequence through the accepted PRS-003 seams;
- caller-visible `false` is preserved;
- every operation is attempted once, no failed write is replayed and no evidence row remains committed;
- no reconnect API, `MYSQL_OPT_RECONNECT`, `mysql_ping`, retry loop or automatic resume exists in the harness.

## Validation

Feature head `91f90c9325cbabcfd67d16e09317daa4aea1b47b` passed disposable MariaDB `30578360334`, full CI `30578360728`, Required `30578360313` and autofix `30578360325`. Final feature audit proved `behind_by=0`, exactly four owned paths and no discussion items. Lifecycle PR #258 changed exactly the active/archive pair, passed Required and merged expected-head. Finalizer PR #259 changed exactly this archive file, passed Required, remained fresh and discussion-free, and merged expected-head.

## Safety boundaries

- no production source or production fault injection;
- no `src/database/database.cpp`, state-machine contract or existing test CMake registration change;
- no reconnect, ping, replay, retry framework, recovery runtime or automatic resume;
- no mutation admission, draining or final-save orchestration;
- no schema migration, persistent database state, real credential or public database port;
- no PRS-004+ implementation and no RPO/RTO claim.

## Program order

- PRS-003E-B opens after this terminal PRS-003E-A;
- PRS-003E-C opens after terminal PRS-003E-B;
- terminal PRS-003D plus terminal PRS-003E open durable PRS-004;
- an additional PRS-003E slice is allowed only if controlled evidence proves a real gap.

## Rollback

Revert feature merge `09297920ffa15feea2a05b24909d58b8e2a33e2a`. No persistent data, schema, credentials or deployment state requires reversal.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T23:02:00+02:00
head: 1fecde7768deeef4fa8af763fd4c56e41eb3363c
head_scope: terminal PRS-003E-A finalizer merge; this metadata-only record adds historical finalizer evidence
branch: main
pr: 259
status: terminal
context_routes:
  - production-resilience
  - database
  - failure-injection
  - controlled-runtime
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
proven:
  - Feature PR 238 merged exact head 91f90c9325cbabcfd67d16e09317daa4aea1b47b as 09297920ffa15feea2a05b24909d58b8e2a33e2a.
  - Issue 232 is closed completed.
  - Exact-head MariaDB 30578360334, CI 30578360728, Required 30578360313 and autofix 30578360325 passed.
  - Feature diff was exactly four declared test/workflow/task paths, behind_by was zero, and discussions were empty.
  - Lifecycle PR 258 changed exactly the active/archive pair, passed Required 30580880580 and merged as c308f175d4988ac30cfc296c0de16d3389f5a18f.
  - Finalizer PR 259 changed exactly one archive path, passed Required 30581120699 and merged as 1fecde7768deeef4fa8af763fd4c56e41eb3363c.
  - Active task record is absent and this terminal archive record is present on main.
  - No production source, reconnect, replay, recovery runtime, automatic resume, schema or PRS-004+ work was added.
derived:
  - PRS-003E-A supplies controlled runtime outage evidence without changing runtime recovery policy.
unknown: []
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
  - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
validation:
  - command: feature exact-head MariaDB, CI, Required and autofix
    result: PASS
    evidence: Runs 30578360334, 30578360728, 30578360313 and 30578360325 succeeded on 91f90c9325cbabcfd67d16e09317daa4aea1b47b.
  - command: feature scope, freshness and discussion audit
    result: PASS
    evidence: Four paths, behind_by zero, mergeable non-draft PR and no discussion items.
  - command: lifecycle Required, scope, freshness and discussion audit
    result: PASS
    evidence: PR 258 changed the active/archive pair, passed Required 30580880580, had behind_by zero and no discussion items, and merged as c308f175d4988ac30cfc296c0de16d3389f5a18f.
  - command: finalizer Required, scope, freshness and discussion audit
    result: PASS
    evidence: PR 259 changed one archive path, passed Required 30581120699, had behind_by zero and no discussion items, and merged as 1fecde7768deeef4fa8af763fd4c56e41eb3363c.
blockers: []
next_action: none
```
