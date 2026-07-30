---
task_id: OTH-20260730-prs003e-a-disposable-mariadb-outage-injector
status: validating
branch: dudantas/prs-003e-a
base_branch: main
start_sha: 30ad4f41987481219faf43fdab51596a0bec4732
created: 2026-07-30
updated: 2026-07-30
related_issue: "232"
related_pr: "238"
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
  - tests/integration/prs_003e/database_outage_injector.cpp
  - tests/integration/prs_003e/run_disposable_mariadb_outage.sh
  - .github/workflows/prs-003e-database-outage.yml
shared_paths: []
excluded_paths:
  - src/database/database.cpp
  - src/database/database_outage_state.hpp
  - src/database/database_failure_classification.hpp
  - tests/unit/database/CMakeLists.txt
  - tests/unit/server/CMakeLists.txt
  - src/game/
  - src/server/
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/agents/tasks/archive/OTH-20260729-prs002j-final-player-save.md
  - docs/agents/tasks/archive/OTH-20260729-prs003c-login-handoff-integration.md
search_first:
  - docs/agents/tasks/active/
  - docs/agents/tasks/archive/
  - src/database/database.cpp
  - src/database/database_failure_classification.hpp
  - src/database/database_outage_state.hpp
  - tests/unit/database/database_failure_classification_test.cpp
  - tests/unit/database/CMakeLists.txt
  - .github/workflows/
---

# PRS-003E-A disposable MariaDB outage injector

## Goal

Add the smallest test-only controlled-runtime harness that uses one disposable MariaDB 11.4 container and the accepted PRS-003 classification/publisher headers to prove real client failures without changing production database or recovery behavior.

## Live ownership audit

- task-start `main` is `30ad4f41987481219faf43fdab51596a0bec4732`;
- current synchronized feature parent is `253ab64f30da6e9c540193df207d4b52717456b3`, created by merging current `main` `35b1a3f5ffe775d2973df6f996f2a966e7d4d761` into this feature branch;
- PRS-003C-B is terminal through feature PR #228, lifecycle PR #229 and finalizer PR #230;
- no open PR, branch, issue or active task matching PRS-003D or PRS-003E existed before issue #232 and this branch were created;
- concurrent PRS-003D-A PR #236 owns only its task, policy architecture, `src/game/database_outage_mutation_admission_policy.hpp`, `tests/unit/game/CMakeLists.txt` and its unit test;
- all PRS-003E-A owned paths remain new and disjoint from PRS-003D-A, production paths, `database.cpp`, existing test CMake files and the PRS-003 state-machine contract;
- if a concurrent task claims any owned path, source changes stop and the conflict is recorded here.

## Accepted evidence

The disposable harness proves:

- a query interrupted while in flight reports client `CR_SERVER_LOST`;
- the next one-shot operation on the same dead handle reports `CR_SERVER_GONE_ERROR`;
- transaction begin failure is classified known-not-committed;
- transaction commit failure is classified unknown outcome;
- rollback failure is classified unknown outcome;
- ordinary query failure is classified known-not-committed;
- each failure publishes the fixed reason, commit outcome and deterministic sequence expected by PRS-003A/B;
- caller-visible failure remains `false` after publication;
- no reconnect API or client reconnect option is invoked, the same dead handle remains dead and each operation is attempted once;
- no failed write is replayed and the disposable evidence table contains no duplicate/replayed row.

## Injection design

- start a disposable `mariadb:11.4` container bound only to loopback on an ephemeral host port;
- use test-only empty-root authentication inside the disposable runner;
- use a separate control connection to issue `KILL CONNECTION` against a test connection;
- interrupt `SELECT SLEEP(...)` to deterministically create lost-connection evidence;
- reuse the same dead handle once to obtain server-gone evidence without any reconnect call or option;
- kill transaction connections immediately before begin, commit or rollback calls;
- compile one standalone C++ test binary against the runner's MariaDB Connector/C and repository headers;
- remove the container and binary on every exit.

## Safety boundaries

- test-only fault injection; no production fault endpoint or runtime hook;
- no edit to `src/database/database.cpp` or any production source;
- no reconnect API, `MYSQL_OPT_RECONNECT`, `mysql_ping`, retry loop, arbitrary SQL replay or automatic resume;
- no mutation admission, draining, disconnect or final-save orchestration;
- no recovery runtime, probe contract or operator-resume implementation;
- no schema migration; only a disposable table inside the ephemeral database;
- no real credentials, secrets, production data, persistent volume or public database port;
- no PRS-004+ implementation and no RPO/RTO claim.

## Rollback

Revert the feature PR and remove its dedicated workflow/test subtree. No schema, persistent data, credential, deployment or production rollback is required.

## Remaining separate work

- PRS-003E-B bounded recovery evidence/probe contract opens after terminal PRS-003E-A;
- PRS-003E-C explicit auditable operator-controlled resume opens after terminal PRS-003E-B;
- terminal PRS-003D plus terminal PRS-003E open durable PRS-004;
- any additional slice opens only if controlled evidence proves a real gap.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T09:44:00+02:00
head: de0f8b88dea45e794b5d576665c30e6bd3a25c8c
head_scope: exact-validated feature head before this dependency-graph-only checkpoint update
branch: dudantas/prs-003e-a
pr: 238
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
  - tests/integration/prs_003e/database_outage_injector.cpp
  - tests/integration/prs_003e/run_disposable_mariadb_outage.sh
  - .github/workflows/prs-003e-database-outage.yml
proven:
  - PRS-003C-B is terminal on main.
  - Issue 232, branch dudantas/prs-003e-a and feature PR 238 are the single PRS-003E-A package.
  - PR 238 changes exactly the four declared owned paths.
  - Concurrent PRS-003D-A PR 236 has completely disjoint actual and declared paths.
  - No production path, database.cpp, existing test CMake file or PRS-003 state-machine contract is modified.
  - Exact head de0f8b8 passed disposable MariaDB run 30522591120, CI run 30522591264, Required run 30522591126 and autofix run 30522591168.
  - The controlled run proves CR_SERVER_LOST, CR_SERVER_GONE_ERROR, begin, commit and rollback failures, known-not-committed and unknown outcomes, fixed event/reason/sequence, fail-closed caller false, one attempt and no replay.
  - The current source invokes no reconnect API or client reconnect option and reuses the same dead handle for server-gone evidence.
  - PRS-003E-B follows terminal PRS-003E-A, PRS-003E-C follows terminal PRS-003E-B, and durable PRS-004 remains blocked until terminal PRS-003D plus terminal PRS-003E.
derived:
  - The existing PRS-003 classifier conservatively reports a killed rollback connection as ConnectionLost or ServerGone with unknown outcome; the initial QueryFailed expectation was incorrect and was corrected without production changes.
unknown:
  - Exact-final-head controlled MariaDB evidence, CI, Required and autofix after this dependency-graph-only update.
  - Feature merge SHA and lifecycle archive/finalizer metadata.
conflicts: []
first_failure:
  marker: rollback-failure-reason-mismatch
  result: CONTAINED
  evidence: Controlled run 30520781311 proved the native rollback failure is connection-scoped; the test now validates the accepted native reason with unknown outcome.
rejected_hypotheses:
  - production fault-injection endpoint
  - modify database.cpp to expose test hooks
  - reconnect API or client reconnect option
  - retry or replay after connection loss
  - use real credentials or persistent database state
  - combine recovery runtime, draining or operator resume
changed_paths:
  - .github/workflows/prs-003e-database-outage.yml
  - docs/agents/tasks/active/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
  - tests/integration/prs_003e/database_outage_injector.cpp
  - tests/integration/prs_003e/run_disposable_mariadb_outage.sh
validation:
  - command: live issue, branch, PR and ownership audit
    result: PASS
    evidence: One PRS-003E-A package exists; PRS-003D-A PR 236 has disjoint owned and actual paths.
  - command: required-read and seam audit
    result: PASS
    evidence: Governance, resilience, PRS-003, PRS-002J and terminal PRS-003C-B records plus classifier/publisher source and existing tests were inspected.
  - command: exact-head controlled MariaDB, CI, Required and autofix on de0f8b8
    result: PASS
    evidence: Runs 30522591120, 30522591264, 30522591126 and 30522591168 completed successfully.
  - command: exact-final-head controlled MariaDB evidence, CI, Required and autofix
    result: NOT_RUN
    evidence: This dependency-graph-only checkpoint update requires fresh exact-head validation before merge.
blockers: []
next_action: Require exact-final-head controlled MariaDB evidence, CI, Required and autofix; then repeat scope, patch, discussion and main-freshness audits before expected-head squash merge.
```
