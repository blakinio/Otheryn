---
task_id: OTH-20260730-prs003e-a-disposable-mariadb-outage-injector
status: terminal
branch: dudantas/prs-003e-a
base_branch: main
start_sha: 30ad4f41987481219faf43fdab51596a0bec4732
feature_head: 91f90c9325cbabcfd67d16e09317daa4aea1b47b
feature_merge_sha: 09297920ffa15feea2a05b24909d58b8e2a33e2a
feature_pr: "238"
lifecycle_pr: "258"
lifecycle_head: 4f00a739166e306ece09f76bde5148b9bc119bc1
lifecycle_required_run: 30580880580
lifecycle_merge_sha: c308f175d4988ac30cfc296c0de16d3389f5a18f
finalizer_pr: "259"
finalizer_head: 04ca821c031eb8b15c0c567441789a2cd66f4740
finalizer_required_run: 30581120699
finalizer_merge_sha: 1fecde7768deeef4fa8af763fd4c56e41eb3363c
issue: "232"
created: 2026-07-30
updated: 2026-07-30
completed: 2026-07-30
owned_paths:
  - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
---

# PRS-003E-A disposable MariaDB outage injector

## Terminal result

PRS-003E-A is terminal. Feature PR #238 merged exact validated head `91f90c9325cbabcfd67d16e09317daa4aea1b47b` as `09297920ffa15feea2a05b24909d58b8e2a33e2a`; issue #232 closed completed. Lifecycle PR #258 passed Required `30580880580` and merged exact head `4f00a739166e306ece09f76bde5148b9bc119bc1` as `c308f175d4988ac30cfc296c0de16d3389f5a18f`, removing the active record and creating this archive. Finalizer PR #259 passed Required `30581120699` and merged exact head `04ca821c031eb8b15c0c567441789a2cd66f4740` as `1fecde7768deeef4fa8af763fd4c56e41eb3363c`.

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

## Feature validation

- exact feature head: `91f90c9325cbabcfd67d16e09317daa4aea1b47b`;
- disposable MariaDB run `30578360334`: PASS;
- CI #675 / `30578360728`: PASS;
- Required #760 / `30578360313`: PASS;
- autofix #583 / `30578360325`: PASS with no replacement commit;
- Linux, macOS, Windows, Docker, smoke, schema-import and test jobs: PASS;
- scope: exactly four declared paths;
- freshness: `behind_by=0`;
- discussion: no comments, reviews, review threads or requested reviewers;
- expected-head squash merge: `09297920ffa15feea2a05b24909d58b8e2a33e2a`.

## Lifecycle validation

- lifecycle PR #258, exact head `4f00a739166e306ece09f76bde5148b9bc119bc1`;
- Required #762 / `30580880580`: PASS;
- scope: exactly the active-record deletion and archive-record addition;
- freshness: `behind_by=0`;
- discussion: no comments, reviews or review threads;
- expected-head squash merge: `c308f175d4988ac30cfc296c0de16d3389f5a18f`.

## Finalizer validation

- finalizer PR #259, exact head `04ca821c031eb8b15c0c567441789a2cd66f4740`;
- Required #764 / `30581120699`: PASS;
- scope: exactly one archive file;
- freshness: `behind_by=0`;
- discussion: no comments, reviews or review threads;
- expected-head squash merge: `1fecde7768deeef4fa8af763fd4c56e41eb3363c`;
- this archive-only correction records historical finalizer evidence and changes no runtime behavior.

## First-failure chain

Superseded heads exposed an incorrect rollback-reason expectation and direct reconnect-option use. The final implementation removed every reconnect option, reused the same dead handle for one server-gone observation, accepted the native connection-scoped rollback reason and passed the complete replacement validation set.

## Safety boundaries preserved

- no production source or production fault injection;
- no `src/database/database.cpp`, state-machine contract or existing test CMake registration change;
- no reconnect, ping, replay, retry framework, recovery runtime or automatic resume;
- no mutation admission, draining or final-save orchestration;
- no schema migration, persistent database state, real credential or public database port;
- no PRS-004+ implementation and no RPO/RTO claim.

## Program order

- PRS-003E-B may open after a fresh live dependency and ownership audit;
- PRS-003E-C opens after terminal PRS-003E-B;
- terminal PRS-003D plus terminal PRS-003E open durable PRS-004.

## Rollback

Revert feature merge `09297920ffa15feea2a05b24909d58b8e2a33e2a`. Archive-only lifecycle and metadata commits require no runtime rollback.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T23:00:00+02:00
head: 1fecde7768deeef4fa8af763fd4c56e41eb3363c
head_scope: terminal feature, lifecycle and finalizer merges on main; this correction records historical evidence only
branch: dudantas/prs-003e-a-terminal-evidence
pr: null
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
  - Dedicated MariaDB 30578360334, CI 30578360728, Required 30578360313 and autofix 30578360325 passed.
  - Feature diff was exactly four declared paths, behind_by was zero and discussions were empty.
  - Lifecycle PR 258 changed exactly the active/archive pair, passed Required 30580880580 and merged exact head 4f00a739166e306ece09f76bde5148b9bc119bc1 as c308f175d4988ac30cfc296c0de16d3389f5a18f.
  - Finalizer PR 259 changed exactly one archive file, passed Required 30581120699 and merged exact head 04ca821c031eb8b15c0c567441789a2cd66f4740 as 1fecde7768deeef4fa8af763fd4c56e41eb3363c.
  - Issue 232 is closed completed, the active record is absent and this terminal archive is present.
  - No production source, reconnect, replay, recovery runtime, automatic resume, schema or PRS-004+ work was added.
derived:
  - PRS-003E-A supplies controlled runtime outage evidence without changing runtime recovery policy.
unknown: []
conflicts: []
first_failure:
  marker: rollback-failure-reason-mismatch and reconnect-option use on superseded heads
  result: CONTAINED
  evidence: final head removed reconnect configuration, accepted native rollback connection failure and passed the complete replacement set
rejected_hypotheses:
  - production fault injection
  - reconnect or replay after connection loss
  - recovery runtime in PRS-003E-A
  - automatic resume
  - schema or deployment changes
changed_paths:
  - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
validation:
  - command: feature exact-head dedicated evidence, CI, Required and autofix
    result: PASS
    evidence: runs 30578360334, 30578360728, 30578360313 and 30578360325 succeeded on 91f90c9325cbabcfd67d16e09317daa4aea1b47b
  - command: lifecycle PR 258
    result: PASS
    evidence: exact active/archive pair, Required 30580880580 and expected-head merge c308f175d4988ac30cfc296c0de16d3389f5a18f
  - command: finalizer PR 259
    result: PASS
    evidence: one archive file, Required 30581120699 and expected-head merge 1fecde7768deeef4fa8af763fd4c56e41eb3363c
blockers: []
next_action: none
```
