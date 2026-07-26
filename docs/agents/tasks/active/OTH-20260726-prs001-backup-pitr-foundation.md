---
task_id: OTH-20260726-prs001-backup-pitr-foundation
status: investigating
branch: dudantas/prs-001-backup-pitr-foundation
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "122"
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260726-prs001-backup-pitr-foundation.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/EXECUTION_MODE_ROUTING.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/operations/backup-and-pitr-policy.md
  - docs/operations/production-recovery-runbook.md
  - deploy/production/README.md
  - deploy/production/mariadb/99-resilience.cnf.example
search_first:
  - deploy/production
  - .github/workflows
  - docker/docker-compose.yml
  - tests
  - tools
optional_reads:
  - docs/architecture/oam-004a-database-transaction-integrity.md
  - docs/architecture/oam-004b-fail-closed-database-migrations.md
  - docs/architecture/oam-004c-world-save-failure-propagation.md
  - docs/architecture/oam-004d-player-save-failure-propagation.md
---

# PRS-001 backup and PITR foundation

## Goal

Implement one bounded, disposable backup and point-in-time recovery foundation that proves backup creation, integrity verification, isolated restore and exact-time recovery without accessing or changing any production host, database, credential or data.

## Task-start target

```text
blakinio/Otheryn@4eedf835621e2a64d093dd5096b4b28e632e50f3
```

## Current behavior inventory

- The architecture and lifecycle contract from issue 116 is merged and archived.
- `deploy/production/` is a non-runnable ownership boundary only.
- `deploy/production/mariadb/99-resilience.cnf.example` is design input and is not mounted anywhere.
- The local quickstart uses `mariadb:11.4`, named volumes and restart/health behavior, but it is not a production backup or PITR deployment.
- Repository search found no existing `mariadb-backup` implementation.
- PR 121 owns only the modular-engine architecture task and document; it does not overlap this initial task path.

## Accepted target contract

The package must eventually prove all of the following on disposable infrastructure pinned to exact revisions:

1. an exact MariaDB image/version and validated durability configuration;
2. a full physical backup with binlog coordinates;
3. checksums and a manifest that contains identifiers but no secrets;
4. encrypted off-host-style artifact handling through a test boundary with no real credentials;
5. successful `mariadb-backup --prepare`;
6. isolated restored-database startup;
7. exact-time binlog replay;
8. expected earlier mutations present and a later harmful mutation absent;
9. explicit detection of broken checksums, missing binlogs and invalid recovery ranges;
10. preservation of the previous known-good recovery set after a failed run;
11. focused metrics/evidence and operator documentation;
12. exact-head applicable CI and `Required` before merge.

## Explicit non-goals

- no production database, VPS, endpoint, credential, encryption key or backup-data access;
- no modification of `docker/docker-compose.yml`;
- no runnable production Compose rollout;
- no automatic restore, rollback, replication, promotion or failover;
- no PRS-002 through PRS-008 work;
- no application runtime, gameplay, schema or migration change unless separately justified and added to owned paths before editing;
- no claim of production readiness or measured RPO/RTO before an isolated controlled drill succeeds;
- no storage-provider-specific production integration in the initial discovery step.

## Discovery decisions required before implementation

- exact MariaDB patch version and immutable image digest;
- disposable integration topology and lifecycle;
- artifact-store test boundary and encryption mechanism;
- repository paths for scripts, fixtures, manifests, tests and workflow integration;
- exact schema/mutation fixture used to prove PITR boundaries;
- strategy for deterministic timestamps or binlog positions;
- failure-injection seams and retained evidence;
- whether incremental backup is included or explicitly deferred for the first release.

## Required failure injection

- backup command failure;
- artifact upload/storage failure after local backup;
- checksum mismatch;
- missing binlog segment;
- prepare failure;
- restored database startup failure;
- recovery target outside the available range.

Every injected failure must return non-zero, identify the first failure and retain the previous known-good recovery set.

## Rollback and removal

- All package services and data must be disposable and isolated from production.
- Test teardown must remove only package-owned containers, networks, volumes and temporary artifacts.
- A failed package can be reverted by removing its bounded deployment/tooling, tests and workflow entries without changing application state or the local quickstart.
- No rollback procedure may delete an unverified current database or the previous known-good recovery set.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T11:17:00+02:00
head: 4eedf835621e2a64d093dd5096b4b28e632e50f3
branch: dudantas/prs-001-backup-pitr-foundation
pr: none
status: investigating
context_routes:
  - operations
  - database-persistence
  - docker
  - ci
  - security
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260726-prs001-backup-pitr-foundation.md
proven:
  - Task-start main is 4eedf835621e2a64d093dd5096b4b28e632e50f3.
  - Issue 122 owns PRS-001 and excludes PRS-002 through PRS-008.
  - The production-resilience architecture task is merged and formally archived.
  - deploy/production is non-runnable and its MariaDB option file is design-only.
  - The local quickstart uses mariadb:11.4 and must remain unchanged.
  - Repository search found no existing mariadb-backup implementation.
  - Open PR 121 changes only its own task and modular-engine architecture document.
derived:
  - PRS-001 requires a separate disposable integration harness rather than extending the local quickstart.
  - Exact implementation paths must be selected only after CI and tooling inventory.
unknown:
  - Exact pinned MariaDB patch version and immutable digest.
  - Exact disposable artifact-store and encryption test mechanism.
  - Exact CI runner capabilities and runtime duration for physical backup/PITR tests.
  - Exact implementation and test paths to own after discovery.
  - Whether first release includes incremental backups or explicitly defers them.
conflicts: []
first_failure:
  marker: no-implemented-backup-pitr-foundation
  command: task-start architecture and repository inventory
  result: OPEN
  evidence: The accepted architecture exists, but no executable backup, prepare, isolated restore or PITR proof exists in the repository.
rejected_hypotheses:
  - Modify the local Docker quickstart to become the production backup stack.
  - Treat a Docker volume copy or VPS snapshot as the sole accepted database backup.
  - Treat a MariaDB replica as a backup.
  - Use real production credentials or data for validation.
  - Begin replication, failover, checkpointing, fencing or Compose hardening in PRS-001.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-prs001-backup-pitr-foundation.md
validation:
  - command: live main and open-PR ownership audit
    result: PASS
    evidence: Main is 4eedf835621e2a64d093dd5096b4b28e632e50f3 and open PR 121 has no path overlap with the initial task record.
  - command: architecture, policy and implementation-guide review
    result: PASS
    evidence: PRS-001 scope, safety boundaries, failure injection and completion proof are recorded without importing other PRS packages.
  - command: existing backup-tooling search
    result: PASS
    evidence: No repository mariadb-backup implementation was found; the quickstart remains a separate non-production boundary.
  - command: checkpoint contract validation
    result: NOT_RUN
    evidence: Run after the task record is committed on its branch.
blockers: []
next_action: Inventory current CI, production-boundary and test infrastructure, select the exact disposable PRS-001 topology and pinned MariaDB version, then update owned paths before changing implementation files.
```
