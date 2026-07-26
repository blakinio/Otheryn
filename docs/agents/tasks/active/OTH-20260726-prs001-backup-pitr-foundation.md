---
task_id: OTH-20260726-prs001-backup-pitr-foundation
status: blocked
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
updated_at: 2026-07-26T12:38:00+02:00
head: 26bebd72c22086f34a954e2cb732d596de5ca8ce
branch: dudantas/prs-001-backup-pitr-foundation
pr: 123
status: blocked
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
  - Issue 122 and PR 123 own only the bounded PRS-001 package.
  - MariaDB is pinned to 11.4.12 and immutable index digest a794d9eb009e20de605858a11f32f63b4075cbd197c650436f0e3b457e4caed7.
  - The package creates a physical full backup with MariaDB backup metadata and archived binary logs.
  - Recovery sets are checksum-protected, symmetrically encrypted, staged and atomically published without replacing an existing identifier.
  - Verification rejects corrupted checksums, missing binlogs, unsafe payload paths, unexpected manifests and mismatched image/version identities.
  - Restore prepares the backup, copies it into an empty package-owned volume, starts isolated MariaDB and replays ordered binlogs to an approved UTC target.
  - The exact-time drill retained the base and expected mutation and excluded the later harmful mutation.
  - All seven required failure injections returned non-zero and preserved the known-good set.
  - PRS-001 workflow 30197442306, repository CI 30197442433 and Required 30197442329 passed on exact head 26bebd72c22086f34a954e2cb732d596de5ca8ce before ready transition.
  - The workflow checkpoint validator passed on the same exact head.
  - Ready-head CI 30197504976 failed twice only after PartyTest.GetPlayersAndDisbandHandleNullEntries reported OK and then segfaulted during teardown.
  - Each failing attempt passed 482 of 483 Linux debug tests; all other ready-head CI platforms passed.
  - Issue 125 separately owns the repeated Party test teardown SIGSEGV and explicitly excludes its fix from PRS-001.
  - No production credential, endpoint, key or data is committed or accessed.
  - The local quickstart, application runtime, schema and migrations are unchanged.
derived:
  - The disposable drill proves the mechanics of the bounded full-backup plus binlog model, not a deployed production backup service.
  - The repeated Party test teardown SIGSEGV is outside the eleven PRS-001 paths but blocks repository Required from becoming green.
unknown:
  - Root cause and bounded fix for issue 125.
  - Production object-store, credential, encryption-key and scheduler implementation.
  - Production database size, write rate, backup duration, storage capacity and measured RPO/RTO.
conflicts: []
first_failure:
  marker: party-test-post-success-segfault
  command: ready-head CI 30197504976 jobs 89781674816 and 89782999565
  result: OPEN
  evidence: PartyTest.GetPlayersAndDisbandHandleNullEntries reports OK, then both attempts terminate with SIGSEGV during teardown; the remaining 482 tests pass.
rejected_hypotheses:
  - Modify Party runtime or tests inside PRS-001.
  - Hide the failure by skipping the test or weakening Required.
  - Continue retrying the same deterministic failure without a fix.
  - Modify the local Docker quickstart to become the production backup stack.
  - Treat a Docker volume copy or VPS snapshot as the sole accepted database backup.
  - Use real production credentials or data for validation.
  - Begin replication, failover, checkpointing, fencing or Compose hardening in PRS-001.
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
  - command: PRS-001 Backup PITR run 30197442306
    result: PASS
    evidence: Exact-head syntax, checkpoint, dependency, backup, encrypted publication, prepare, isolated restore, PITR and seven failure-injection gates passed.
  - command: repository CI run 30197442433
    result: PASS
    evidence: Full repository CI completed successfully on exact head 26bebd72c22086f34a954e2cb732d596de5ca8ce before ready transition.
  - command: exact-head Required run 30197442329
    result: PASS
    evidence: Required completed successfully on the same exact head before ready transition.
  - command: ready-head CI run 30197504976
    result: FAIL
    evidence: Two attempts reproduced the unrelated Party test post-success SIGSEGV; all other jobs and 482 of 483 Linux debug tests passed.
  - command: production-safety and scope audit
    result: PASS
    evidence: Eleven declared paths only; no quickstart, runtime, schema, migration, production Compose, production data or credentials.
blockers:
  - issue 125 must fix the repeated Party test teardown SIGSEGV before PR 123 can obtain final ready-head Required
next_action: Resolve issue 125 in a separate bounded PR, then rerun PR 123 exact-head CI and Required and repeat the final path, discussion and target-main drift audit before merge.
```
