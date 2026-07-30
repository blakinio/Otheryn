---
task_id: OTH-20260730-prs003e-b-recovery-evidence
status: active
branch: dudantas/prs-003e-b-recovery-evidence
base_branch: main
start_sha: 8465a28e9efe5258708ce7b12184c651b94f3d3d
issue: "262"
feature_pr: "264"
created: 2026-07-30
updated: 2026-07-31
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
- `DatabaseOutageStateMachine` accepts `recoveryEvidenceAccepted(sequence, now)` only from degraded or maintenance and does not change state automatically.
- Any later qualifying `runtimeFailure` clears accepted recovery evidence.
- Before this slice, no bounded owner defined the read plus transactional write/rollback success window that may emit accepted evidence.

## Delivered contract

One database-independent, header-only tracker receives finite constructor inputs, one fixed candidate start/deadline and explicit probe-attempt outcomes. A successful attempt requires read, transaction begin, isolated write, rollback and post-rollback unchanged-object evidence. Failures reset consecutive successes without extending the original deadline. The tracker emits `PublishRecoveryEvidenceAccepted` at most once after the required consecutive window and calls only the existing serialized state owner's `recoveryEvidenceAccepted`; it never calls `operatorResume` or enters healthy.

The disposable MariaDB harness opens new dedicated sessions, never reuses or revives the failed gameplay handle, executes every operation once, uses only a test-owned disposable table, and proves read/begin/write/rollback failures, unchanged rollback state, incomplete/reset windows, exact-once publication, state preservation, later invalidation and no replay.

## Explicit non-goals

- no production `Database` wiring, scheduler, connection pool or background probe loop;
- no `MYSQL_OPT_RECONNECT`, `mysql_ping`, reconnect, arbitrary SQL replay or retry;
- no automatic operator resume or automatic transition to healthy;
- no protocol, login, handoff, mutation, drain or final-save changes;
- no schema migration, gameplay-data probe object, production credential or deployment change;
- no PRS-003E-C or PRS-004+ implementation and no RPO/RTO claim.

## Failure evidence

- deterministic synthetic outcomes cover read, begin, write, rollback and persisted-mutation rejection;
- fixed deadline and attempt budget cover expiration and exhaustion without extension;
- disposable loopback-only MariaDB injects killed-session begin and rollback failures, deterministic write rejection and successful transactional rollback;
- degraded and maintenance state-owner evidence proves exact-once acceptance without auto-resume and later failure invalidation;
- unknown-outcome gameplay mutation and commit are each attempted once and never replayed.

## Rollback plan

Revert the feature merge. The package owns only new header, documentation, test harness, runner and workflow files. It adds no persistent production state, schema, credentials or deployment surface.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T00:25:00+02:00
head: e0930e3fca423bbb7f2f5b8e626a2fe088b35cec
head_scope: exact validated implementation/autofix head before this governance-only evidence checkpoint
branch: dudantas/prs-003e-b-recovery-evidence
pr: 264
status: merge-ready-pending-replacement-checks
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
  - main 8465a28e9efe5258708ce7b12184c651b94f3d3d was the audited task start and PRS-003E-A was terminal.
  - issue 262 and PR 264 are the unique PRS-003E-B records.
  - all six changed paths exactly match the frozen new-file ownership and do not overlap coordinator or other active work.
  - strict standalone C++20 compilation with warnings-as-errors passed for the tracker and MariaDB harness.
  - dedicated PRS-003E-B workflow 30586300932 passed on exact head e0930e3fca423bbb7f2f5b8e626a2fe088b35cec.
  - regression PRS-003E-A workflow 30586300777 passed on the same head.
  - autofix 30586301018 passed on the same head.
  - full CI 30586300959 passed fast checks, Lua, Linux debug tests, Linux release, Windows CMake and solution, macOS, Docker and quickstart smoke.
  - Required 30586300723 passed on the same head.
  - PR 264 was mergeable, behind_by zero and had no comments, reviews, review threads or requested reviewers at the audit.
  - the implementation contains no reconnect option, ping, failed-operation replay, automatic healthy transition or operator resume call.
derived:
  - this governance-only checkpoint creates a new final head and therefore requires complete replacement exact-head checks.
unknown: []
conflicts: []
first_failure:
  marker: autofix-final-newline
  result: CONTAINED
  evidence: initial autofix 30586236839 found only missing final newlines in the two new C++ files; bot commit e0930e3fca423bbb7f2f5b8e626a2fe088b35cec changed no logic and then passed all applicable gates
rejected_hypotheses:
  - editing production database.cpp
  - modifying the terminal PRS-003E-A workflow or harness
  - automatic resume after successful probes
  - reconnecting or replaying the failed operation
  - claiming shared CMake ownership
  - treating the newline-only autofix replacement as a functional failure
changed_paths:
  - .github/workflows/prs-003e-b-recovery-evidence.yml
  - docs/agents/tasks/active/OTH-20260730-prs003e-b-recovery-evidence.md
  - docs/architecture/prs-003e-b-recovery-evidence.md
  - src/database/database_outage_recovery_evidence.hpp
  - tests/integration/prs_003e/recovery_evidence_probe.cpp
  - tests/integration/prs_003e/run_recovery_evidence_probe.sh
validation:
  - command: live dependency, conflict and ownership preflight
    result: PASS
    evidence: exact six-path new-file scope frozen in issue 262 and this task record
  - command: strict standalone C++20 compilation
    result: PASS
    evidence: tracker and MariaDB harness compiled with warnings-as-errors
  - command: PRS-003E-B Recovery Evidence 30586300932
    result: PASS
    evidence: disposable loopback MariaDB controlled evidence passed on e0930e3fca423bbb7f2f5b8e626a2fe088b35cec
  - command: PRS-003E MariaDB Outage Evidence 30586300777
    result: PASS
    evidence: terminal E-A regression evidence passed on the same head
  - command: autofix 30586301018
    result: PASS
    evidence: no remaining formatting changes on the same head
  - command: CI 30586300959
    result: PASS
    evidence: full cross-platform and Docker matrix passed on the same head
  - command: Required 30586300723
    result: PASS
    evidence: required gate passed after CI on the same head
  - command: replacement checks for this governance-only checkpoint
    result: PENDING
    evidence: this commit creates a new final head that must pass all applicable gates unchanged
blockers: []
next_action: require replacement exact-head dedicated evidence, CI, Required and autofix, repeat scope, freshness and discussion audits, then expected-head squash merge PR 264
```
