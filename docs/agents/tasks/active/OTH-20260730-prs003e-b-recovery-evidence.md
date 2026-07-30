---
task_id: OTH-20260730-prs003e-b-recovery-evidence
status: active
branch: dudantas/prs-003e-b-recovery-evidence
base_branch: main
start_sha: 8465a28e9efe5258708ce7b12184c651b94f3d3d
issue: "262"
feature_pr: null
created: 2026-07-30
updated: 2026-07-30
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003e-b-recovery-evidence.md
  - docs/architecture/prs-003e-b-recovery-evidence.md
  - src/database/database_outage_recovery_evidence.hpp
  - tests/integration/prs_003e/recovery_evidence_probe.cpp
  - tests/integration/prs_003e/run_recovery_evidence_probe.sh
  - .github/workflows/prs-003e-b-recovery-evidence.yml
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/agents/tasks/archive/OTH-20260730-prs003e-a-disposable-mariadb-outage-injector.md
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
search_first:
  - open PRS issues and pull requests
  - matching dudantas/prs-003e-b branches
  - docs/agents/tasks/active/
  - src/database/database_outage_state.hpp
  - tests/integration/prs_003e/
---

# PRS-003E-B bounded recovery evidence and probe contract

## Current behavior inventory

- Terminal PRS-003E-A proves one-shot MariaDB outage classification and publication without reconnect or replay.
- `DatabaseOutageStateMachine` already accepts `recoveryEvidenceAccepted(sequence, now)` only from degraded or maintenance and does not change state automatically.
- Any later qualifying `runtimeFailure` clears accepted recovery evidence.
- No bounded owner currently defines the read plus transactional write/rollback success window that may emit the accepted evidence decision.
- No E-B branch, PR, active task or path ownership existed at the audited task start.

## Accepted target contract

One database-independent, header-only tracker receives finite constructor inputs, one fixed candidate start/deadline and explicit probe-attempt outcomes. A successful attempt requires read, transaction begin, isolated write, rollback and post-rollback unchanged-object evidence. Failures reset consecutive successes without extending the original deadline. The tracker emits `PublishRecoveryEvidenceAccepted` at most once after the required consecutive window. A helper may then call only the existing serialized state owner's `recoveryEvidenceAccepted`; it never calls `operatorResume` and never enters healthy.

The disposable MariaDB harness must use new dedicated sessions, never reuse or revive the failed gameplay handle, execute every probe operation once, use only a test-owned disposable table, and prove begin/write/rollback failures, unchanged rollback state, incomplete/reset windows, exact-once evidence publication, state preservation and later failure invalidation.

## Explicit non-goals

- no production `Database` wiring, scheduler, connection pool or background probe loop;
- no `MYSQL_OPT_RECONNECT`, `mysql_ping`, reconnect, arbitrary SQL replay or retry;
- no automatic operator resume or automatic transition to healthy;
- no protocol, login, handoff, mutation, drain or final-save changes;
- no schema migration, gameplay-data probe object, production credential or deployment change;
- no PRS-003E-C or PRS-004+ implementation and no RPO/RTO claim.

## Failure-injection plan

- deterministic synthetic outcomes cover read, begin, write, rollback and persisted-mutation rejection;
- fixed deadline and attempt budget cover expiration and exhaustion without extension;
- disposable loopback-only MariaDB injects killed-session begin and rollback failures, deterministic write rejection and successful transactional rollback;
- state-owner evidence covers degraded and maintenance acceptance without auto-resume, exact-once publication and later failure invalidation;
- source/runtime assertions prove the failed gameplay handle is never retried or replayed.

## Rollback plan

Revert the feature merge. The package owns only new header, documentation, test harness, runner and workflow files. It adds no persistent production state, schema, credentials or deployment surface.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T23:59:00+02:00
head: 8465a28e9efe5258708ce7b12184c651b94f3d3d
head_scope: task-start main plus this active-record commit on the canonical branch
branch: dudantas/prs-003e-b-recovery-evidence
pr: null
status: implementation-ready
context_routes:
  - production-resilience
  - database-outage
  - recovery-evidence
  - controlled-runtime
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003e-b-recovery-evidence.md
  - docs/architecture/prs-003e-b-recovery-evidence.md
  - src/database/database_outage_recovery_evidence.hpp
  - tests/integration/prs_003e/recovery_evidence_probe.cpp
  - tests/integration/prs_003e/run_recovery_evidence_probe.sh
  - .github/workflows/prs-003e-b-recovery-evidence.yml
proven:
  - main 8465a28e9efe5258708ce7b12184c651b94f3d3d is the audited task start.
  - PRS-003E-A is terminal and issue 262 dependency gate is open.
  - No open PR, matching branch or active task owned any frozen path.
  - All six frozen paths are new and E-B-specific.
  - Existing PRS-003 state owner already accepts recovery evidence without state change and invalidates it on later runtime failure.
derived:
  - A new standalone workflow can compile and exercise the new header without editing shared CMake or existing E-A files.
unknown:
  - exact first dedicated-workflow result
conflicts: []
first_failure:
  marker: none
  result: NOT_RUN
  evidence: implementation and validation have not started
rejected_hypotheses:
  - editing production database.cpp
  - modifying the terminal E-A workflow or harness
  - automatic resume after successful probes
  - reconnecting or replaying the failed operation
  - claiming shared CMake ownership
changed_paths:
  - docs/agents/tasks/active/OTH-20260730-prs003e-b-recovery-evidence.md
validation:
  - command: live dependency, conflict and ownership preflight
    result: PASS
    evidence: exact six-path new-file scope frozen in issue 262 and this task record
  - command: dedicated MariaDB evidence, CI, Required and autofix
    result: NOT_RUN
    evidence: implementation not yet committed
blockers: []
next_action: implement the bounded recovery-evidence tracker and disposable MariaDB harness within the frozen six-path ownership
```