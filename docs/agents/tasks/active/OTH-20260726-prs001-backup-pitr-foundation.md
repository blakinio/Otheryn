---
task_id: OTH-20260726-prs001-backup-pitr-foundation
status: validating
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
updated_at: 2026-07-26T12:04:00+02:00
head: e4c09752be6351333eb530bdb3de93675fc61be4
branch: dudantas/prs-001-backup-pitr-foundation
pr: 123
status: validating
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
  - Issue 122 and draft PR 123 own only the bounded PRS-001 package.
  - MariaDB is pinned to 11.4.12 and immutable index digest a794d9eb009e20de605858a11f32f63b4075cbd197c650436f0e3b457e4caed7.
  - The package creates a physical full backup with MariaDB backup metadata and archived binary logs.
  - Recovery sets are checksum-protected, symmetrically encrypted, staged and atomically published without replacing an existing identifier.
  - Verification rejects corrupted checksums, missing binlogs, unsafe payload paths, unexpected manifests and mismatched image/version identities.
  - Restore prepares the backup, copies it into an empty package-owned volume, starts isolated MariaDB and replays ordered binlogs to an approved UTC target.
  - The exact-time drill retained the base and expected mutation and excluded the later harmful mutation.
  - Backup, publication, checksum, missing-binlog, prepare, startup and out-of-range failures returned non-zero and preserved the known-good set.
  - PRS-001 workflow run 30197369724 passed on e4c09752be6351333eb530bdb3de93675fc61be4.
  - Repository CI run 30197369813 and Required run 30197369725 passed on the same exact head.
  - The workflow checkpoint validator passed on the same exact head.
  - No production credential, endpoint, key or data is committed or accessed.
  - The local quickstart, application runtime, schema and migrations are unchanged.
derived:
  - The disposable drill proves the mechanics of the bounded full-backup plus binlog model, not a deployed production backup service.
  - Incremental backup, real object storage, scheduler, retention, alert delivery and production RPO/RTO remain separate future evidence boundaries.
unknown:
  - Production object-store, credential, encryption-key and scheduler implementation.
  - Production database size, write rate, backup duration, storage capacity and measured RPO/RTO.
  - Production-shaped semantic integrity checks beyond the disposable mutation fixture.
conflicts: []
first_failure:
  marker: no-implemented-backup-pitr-foundation
  command: PRS-001 workflow run 30197369724
  result: RESOLVED
  evidence: The final exact-head drill completed physical backup, encrypted publication, prepare, isolated restore, exact-time PITR and all required failure injections successfully.
rejected_hypotheses:
  - Modify the local Docker quickstart to become the production backup stack.
  - Treat a Docker volume copy or VPS snapshot as the sole accepted database backup.
  - Treat a MariaDB replica as a backup.
  - Use real production credentials or data for validation.
  - Begin replication, failover, checkpointing, fencing or Compose hardening in PRS-001.
  - Add incremental backup before the full-backup and binlog proof is stable.
  - Claim production readiness or measured RPO/RTO from disposable CI timing.
changed_paths:
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
validation:
  - command: PRS-001 Backup PITR run 30197369724
    result: PASS
    evidence: Exact-head syntax, checkpoint, dependency, backup, encrypted publication, prepare, isolated restore, PITR and seven failure-injection gates passed.
  - command: repository CI run 30197369813
    result: PASS
    evidence: Applicable repository CI completed successfully on e4c09752be6351333eb530bdb3de93675fc61be4.
  - command: exact-head Required run 30197369725
    result: PASS
    evidence: Required completed successfully on e4c09752be6351333eb530bdb3de93675fc61be4.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/OTH-20260726-prs001-backup-pitr-foundation.md --require-checkpoint
    result: PASS
    evidence: The package workflow validated the checkpoint on the exact audited head.
  - command: production-safety and scope audit
    result: PASS
    evidence: Eleven declared paths only; no quickstart, runtime, schema, migration, production Compose, production data or credentials.
blockers:
  - refreshed exact-head package workflow and Required after this checkpoint update
  - final changed-path, discussion and target-main drift audit before ready/merge
next_action: Confirm all applicable workflows on the refreshed PR head, then perform the final path, discussion, mergeability and target-main drift audit before expected-head squash merge.
```
