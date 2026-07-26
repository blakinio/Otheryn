---
task_id: OTH-20260726-prs001-backup-pitr-foundation
status: implementing
branch: dudantas/prs-001-backup-pitr-foundation
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "122"
related_pr: "123"
owned_paths:
  - .github/workflows/prs001-backup-pitr.yml
  - deploy/production/README.md
  - deploy/production/mariadb/99-resilience.cnf.example
  - deploy/production/backup/README.md
  - deploy/production/backup/versions.env
  - deploy/production/backup/take-full-backup.sh
  - deploy/production/backup/publish-recovery-set.sh
  - deploy/production/backup/verify-recovery-set.sh
  - deploy/production/backup/restore-pitr.sh
  - tests/integration/production-resilience/prs001-drill.sh
  - docs/agents/tasks/active/OTH-20260726-prs001-backup-pitr-foundation.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
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
- PR 121 owns only the modular-engine architecture task and document; it does not overlap PRS-001 paths.
- `docs/agents/CONTEXT_ROUTING.md`, `docs/agents/BUILD_TEST_MATRIX.md` and `docs/agents/EXECUTION_MODE_ROUTING.md` do not exist in this repository and were removed from required reads.

## Selected bounded topology

- Official MariaDB image: `mariadb:11.4.12@sha256:a794d9eb009e20de605858a11f32f63b4075cbd197c650436f0e3b457e4caed7`.
- The image is used only by a disposable Docker network, primary container, restore container and package-owned volumes.
- A physical full backup is taken in the pinned image with `mariadb-backup`; the same image prepares and restores it.
- Binary logs are copied after an explicit log rotation and retained with the backup coordinate.
- A host directory outside database and backup volumes models the off-host artifact boundary for CI.
- Recovery payloads are symmetrically encrypted by GnuPG with an ephemeral passphrase file; manifests contain no secret material.
- Publication is staged and checksum-verified before an atomic rename; an existing recovery set is never replaced.
- Incremental backups are explicitly excluded from the first release; the accepted full-backup plus binlog model remains sufficient for the initial PITR proof.
- `docker/docker-compose.yml` remains unchanged, and no production Compose stack is introduced.

## Accepted target contract

The package must prove all of the following on disposable infrastructure pinned to exact revisions:

1. the selected exact MariaDB image and durability configuration;
2. a full physical backup with binlog coordinates;
3. checksums and a manifest that contains identifiers but no secrets;
4. encrypted off-host-style artifact handling through a test boundary with no real credentials;
5. successful `mariadb-backup --prepare`;
6. isolated restored-database startup;
7. exact-time binlog replay;
8. expected earlier mutations present and a later harmful mutation absent;
9. explicit detection of broken checksums, missing binlogs and invalid recovery ranges;
10. preservation of the previous known-good recovery set after a failed run;
11. focused evidence and operator documentation;
12. exact-head package CI and `Required` before merge.

## Explicit non-goals

- no production database, VPS, endpoint, credential, encryption key or backup-data access;
- no modification of `docker/docker-compose.yml`;
- no runnable production Compose rollout;
- no automatic restore, rollback, replication, promotion or failover;
- no PRS-002 through PRS-008 work;
- no application runtime, gameplay, schema or migration change;
- no claim of production readiness or measured RPO/RTO from the disposable CI drill;
- no production object-store provider or credential integration;
- no incremental backup in this first release.

## Required failure injection

- backup command failure;
- artifact publication failure after local backup;
- checksum mismatch;
- missing binlog segment;
- prepare failure;
- restored database startup failure;
- recovery target outside the available range.

Every injected failure must return non-zero, identify the first failure and retain the previous known-good recovery set.

## Rollback and removal

- All package services and data are disposable and isolated from production.
- Test teardown removes only package-owned containers, networks, volumes and temporary artifacts.
- The package can be reverted by removing its bounded scripts, test, workflow and documentation without changing application state or the local quickstart.
- No rollback procedure may delete an unverified current database or the previous known-good recovery set.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T11:31:00+02:00
head: caa98c0368c49dbfa3b206830d8d4a50c5d03a08
branch: dudantas/prs-001-backup-pitr-foundation
pr: 123
status: implementing
context_routes:
  - operations
  - database-persistence
  - docker
  - ci
  - security
  - agent-governance
owned_paths:
  - .github/workflows/prs001-backup-pitr.yml
  - deploy/production/README.md
  - deploy/production/mariadb/99-resilience.cnf.example
  - deploy/production/backup/README.md
  - deploy/production/backup/versions.env
  - deploy/production/backup/take-full-backup.sh
  - deploy/production/backup/publish-recovery-set.sh
  - deploy/production/backup/verify-recovery-set.sh
  - deploy/production/backup/restore-pitr.sh
  - tests/integration/production-resilience/prs001-drill.sh
  - docs/agents/tasks/active/OTH-20260726-prs001-backup-pitr-foundation.md
proven:
  - Task-start main is 4eedf835621e2a64d093dd5096b4b28e632e50f3.
  - Issue 122 owns PRS-001 and excludes PRS-002 through PRS-008.
  - The production-resilience architecture task is merged and formally archived.
  - Draft PR 123 initially changed only the active PRS-001 task record.
  - deploy/production is non-runnable and its MariaDB option file is design-only.
  - The local quickstart uses mariadb:11.4 and remains outside this package.
  - Repository search found no existing mariadb-backup implementation.
  - Open PR 121 has no overlap with the selected PRS-001 paths.
  - Three initially referenced governance files do not exist and were removed from required reads.
  - Official Docker Hub publishes MariaDB 11.4.12 with index digest a794d9eb009e20de605858a11f32f63b4075cbd197c650436f0e3b457e4caed7.
  - MariaDB documents that mariadb-backup is present in the official image and prepare should use the same server version.
  - Exact-head Required run 30196242411 passed on initial task head 3d0a78458774e7b0b546f76a412a9b7e55a55340.
derived:
  - A separate disposable Docker drill can prove the full-backup and PITR mechanics without creating production deployment behavior.
  - Full backup plus archived binlogs is the bounded first-release model; incremental backup remains deferred.
unknown:
  - Exact package runtime and resource use on the repository runner.
  - Exact command-level compatibility of the pinned image with the proposed drill until CI executes it.
  - Whether Required automatically recognizes the new package workflow as applicable.
  - Production object-store, credential and scheduler integration, which remain outside this package.
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
  - Add incremental backup before the full-backup and binlog proof is stable.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-prs001-backup-pitr-foundation.md
validation:
  - command: live main and open-PR ownership audit
    result: PASS
    evidence: Main is 4eedf835621e2a64d093dd5096b4b28e632e50f3 and open PR 121 has no overlap with selected paths.
  - command: architecture, policy and implementation-guide review
    result: PASS
    evidence: PRS-001 scope, safety boundaries, failure injection and completion proof are recorded without importing other PRS packages.
  - command: official MariaDB image and backup-reference review
    result: PASS
    evidence: MariaDB 11.4.12 and its official multi-platform digest are selected; official documentation covers physical backup, prepare, container restore and PITR.
  - command: exact-head Required 30196242411
    result: PASS
    evidence: Required completed successfully on initial task head 3d0a78458774e7b0b546f76a412a9b7e55a55340.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/OTH-20260726-prs001-backup-pitr-foundation.md --require-checkpoint
    result: NOT_RUN
    evidence: The connector-only environment has no repository checkout; confirm through exact-head repository CI or a later execution environment before merge.
blockers: []
next_action: Add the pinned version file and bounded backup, publication, verification, restore, drill and workflow files, then use exact-head CI failures to refine the implementation without touching production or quickstart paths.
```
