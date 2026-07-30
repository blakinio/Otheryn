---
task_id: OTH-20260730-prs003e-a-disposable-mariadb-outage-injector
status: implementing
branch: dudantas/prs-003e-a
base_branch: main
start_sha: 30ad4f41987481219faf43fdab51596a0bec4732
created: 2026-07-30
updated: 2026-07-30
related_issue: "232"
related_pr: pending
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
- PRS-003C-B is terminal through feature PR #228, lifecycle PR #229 and finalizer PR #230;
- no open PR, branch, issue or active task matching PRS-003D or PRS-003E existed before issue #232 and this branch were created;
- all owned paths are new and disjoint from production paths, `database.cpp`, both existing test CMake files and the PRS-003 state-machine contract;
- if a concurrent task claims any owned path, source changes stop and the conflict is recorded here.

## Accepted evidence

The disposable harness must prove:

- a query interrupted while in flight reports client `CR_SERVER_LOST`;
- the next one-shot operation on the same dead handle reports `CR_SERVER_GONE_ERROR`;
- transaction begin failure is classified known-not-committed;
- transaction commit failure is classified unknown outcome;
- rollback failure is classified unknown outcome;
- ordinary query failure is classified known-not-committed;
- each failure publishes the fixed reason, commit outcome and deterministic sequence expected by PRS-003A/B;
- caller-visible failure remains `false` after publication;
- reconnect is disabled, the dead handle remains dead and each operation is attempted once;
- no failed write is replayed and the disposable evidence table contains no duplicate/replayed row.

## Injection design

- start a disposable `mariadb:11.4` container bound only to loopback on an ephemeral host port;
- use test-only empty-root authentication inside the disposable runner;
- use a separate control connection to issue `KILL CONNECTION` against a test connection;
- interrupt `SELECT SLEEP(...)` to deterministically create lost-connection evidence;
- reuse the dead handle once to obtain server-gone evidence without reconnect;
- kill transaction connections immediately before begin, commit or rollback calls;
- compile one standalone C++ test binary against the runner's MariaDB Connector/C and repository headers;
- remove the container and binary on every exit.

## Safety boundaries

- test-only fault injection; no production fault endpoint or runtime hook;
- no edit to `src/database/database.cpp` or any production source;
- no reconnect, `mysql_ping`, retry loop, arbitrary SQL replay or automatic resume;
- no mutation admission, draining, disconnect or final-save orchestration;
- no recovery runtime, probe contract or operator-resume implementation;
- no schema migration; only a disposable table inside the ephemeral database;
- no real credentials, secrets, production data, persistent volume or public database port;
- no PRS-004+ implementation and no RPO/RTO claim.

## Rollback

Revert the feature PR and remove its dedicated workflow/test subtree. No schema, persistent data, credential, deployment or production rollback is required.

## Remaining separate work

- PRS-003E-B bounded recovery evidence/probe contract, only after terminal PRS-003D;
- PRS-003E-C explicit auditable operator-controlled resume, only after PRS-003E-B and terminal PRS-003D;
- any additional slice only if controlled evidence proves a real gap.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T08:38:38+02:00
head: pending-implementation
head_scope: active PRS-003E-A task record on branch created from main 30ad4f4
branch: dudantas/prs-003e-a
pr: pending
status: implementing
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
  - No competing PRS-003D or PRS-003E issue, branch, PR or active ownership record was found before task start.
  - The accepted PRS-003B classifier and publisher already expose fixed operation, native-error, outcome, reason and sequence seams.
  - This package owns no production path and no existing test CMake registration.
derived:
  - A standalone controlled-runtime harness can exercise accepted headers without changing runtime recovery or PRS-003D state-machine ownership.
unknown:
  - Exact native error sequence and all required evidence until the dedicated workflow runs on the exact feature head.
  - Feature PR, checks, merge and lifecycle archive metadata.
conflicts: []
first_failure: null
rejected_hypotheses:
  - production fault-injection endpoint
  - modify database.cpp to expose test hooks
  - reconnect or replay after connection loss
  - use real credentials or persistent database state
  - combine recovery runtime, draining or operator resume
changed_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
validation:
  - command: live issue, branch, PR and ownership audit
    result: PASS
    evidence: No competing PRS-003D/003E ownership existed; issue 232 and branch dudantas/prs-003e-a were created from main 30ad4f4.
  - command: required-read and seam audit
    result: PASS
    evidence: Governance, resilience, PRS-003, PRS-002J and terminal PRS-003C-B records plus classifier/publisher source and existing tests were inspected.
blockers: []
next_action: Implement the three remaining owned test/workflow paths, validate the exact diff, and open the feature PR.
```
