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

## Current target

```text
main: 8c0ffb213a4f235d6eeee6a26fef919376453c30
integrated PRS-001 head: a2d6971574e13c157816b9038e5065d481335c12
```

The branch was synchronized with current `main` after issue #125 and PR #126 fixed the unrelated Party unit-test teardown use-after-free. Backup branch `backup/prs001-pre-main-sync-765277a` preserves the pre-sync PRS-001 head.

## Bounded topology

- MariaDB `11.4.12` is pinned to immutable index digest `sha256:a794d9eb009e20de605858a11f32f63b4075cbd197c650436f0e3b457e4caed7`.
- The drill uses only an isolated Docker network, unique package-owned containers, volumes and temporary host directories.
- A physical full backup records MariaDB backup metadata and binlog coordinates.
- An explicit binlog rotation precedes archive capture.
- Recovery payloads are checksum-protected and symmetrically encrypted with an ephemeral passphrase file.
- Publication stages and verifies a recovery set before atomic rename and never replaces an existing identifier.
- Verification rejects malformed manifests, version/image mismatch, corrupted checksums, unsafe archive paths and missing binlogs.
- Restore prepares and copies the physical backup into an empty package-owned volume, starts isolated MariaDB and replays a contiguous binlog sequence to an approved UTC target.
- The drill proves an earlier mutation is present and a later harmful mutation is absent.
- Incremental backups remain deferred.
- `docker/docker-compose.yml` remains unchanged.

## Required proof

1. exact pinned image and conservative durability configuration;
2. physical full backup with binlog coordinates;
3. redacted manifest and outer/inner checksums;
4. encrypted off-host-style filesystem publication;
5. successful `mariadb-backup --prepare`;
6. isolated restored-database startup;
7. exact-time binlog replay;
8. expected earlier mutation present and later harmful mutation absent;
9. non-zero detection of backup, publication, checksum, missing-binlog, prepare, startup and invalid-range failures;
10. preservation of the previous known-good recovery set after every injected failure;
11. exact-head package workflow, repository CI and `Required`;
12. final path, discussion and target-main drift audit.

## Explicit non-goals

- no production database, VPS, endpoint, credential, encryption key or backup-data access;
- no production scheduler, object-store adapter or Compose stack;
- no modification of the local Docker quickstart;
- no automatic restore, rollback, replication, promotion or failover;
- no PRS-002 through PRS-008 work;
- no application runtime, gameplay, schema or migration change;
- no production-readiness, RPO or RTO claim from disposable CI timing;
- no incremental backup in this first release.

## Failure and cleanup boundary

Every injected failure must return non-zero and leave the previously published known-good set unchanged. Disposable cleanup removes only package-owned containers, networks, volumes and temporary artifacts. A failed local backup may retain its unique unpublished backup directory for inspection; it must never replace or delete a verified published recovery set.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T16:10:00+02:00
head: a2d6971574e13c157816b9038e5065d481335c12
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
  - Issue 122 and PR 123 own exactly the bounded eleven-path PRS-001 package.
  - MariaDB is pinned to 11.4.12 and immutable digest a794d9eb009e20de605858a11f32f63b4075cbd197c650436f0e3b457e4caed7.
  - The package creates a physical full backup with MariaDB metadata and archived binary logs.
  - Recovery sets are checksum-protected, encrypted, staged and atomically published without replacing an existing identifier.
  - Verification rejects corrupt checksums, missing binlogs, unsafe archive paths, unexpected manifests and image/version mismatch.
  - Restore validates coordinates and binlog continuity before isolated prepare, copy-back, startup and exact-time replay.
  - The prior disposable drill retained the base and expected mutation and excluded the later harmful mutation.
  - All seven required failure injections previously returned non-zero and preserved the known-good set.
  - Previous package workflow 30197442306, repository CI 30197442433 and Required 30197442329 passed on exact head 26bebd72c22086f34a954e2cb732d596de5ca8ce.
  - Issue 125 was resolved by PR 126 and archived by PR 131 without changing any PRS-001 path.
  - Current main 8c0ffb213a4f235d6eeee6a26fef919376453c30 was merged into the PRS-001 branch as a2d6971574e13c157816b9038e5065d481335c12.
  - After synchronization the branch is zero commits behind main and still changes only the eleven declared paths.
derived:
  - The disposable proof validates bounded mechanics, not a deployed production backup service.
  - The former unrelated Party-test blocker no longer prevents exact-head PRS-001 validation.
unknown:
  - Refreshed exact-head PRS-001 drill result after main synchronization.
  - Refreshed exact-head repository CI and Required results.
  - Production object-store, credential, key, scheduler, capacity and measured RPO/RTO design.
conflicts: []
first_failure:
  marker: party-test-post-success-segfault
  command: ready-head CI 30197504976 jobs 89781674816 and 89782999565
  result: RESOLVED
  evidence: Issue 125 was fixed in PR 126; final main-synchronized Party ASAN, CI and Required passed before PRS-001 resumed.
rejected_hypotheses:
  - Modify Party runtime or tests inside PRS-001.
  - Hide failures by skipping tests or weakening Required.
  - Modify the local Docker quickstart to become the production backup stack.
  - Treat a Docker volume copy or VPS snapshot as the sole accepted database backup.
  - Use real production credentials or data for validation.
  - Begin replication, failover, fencing or production Compose hardening in PRS-001.
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
    evidence: Previous exact-head syntax, checkpoint, dependency, backup, encrypted publication, prepare, isolated restore, PITR and seven failure-injection gates passed.
  - command: repository CI run 30197442433
    result: PASS
    evidence: Previous full repository CI completed successfully before the unrelated Party teardown regression was exposed.
  - command: exact-head Required run 30197442329
    result: PASS
    evidence: Previous Required completed successfully on the same PRS-001 source head.
  - command: main synchronization and scope audit
    result: PASS
    evidence: Current main merged without path conflicts; executable modes were preserved; branch is zero behind and diff remains eleven declared paths.
  - command: refreshed PRS-001 package workflow
    result: NOT_RUN
    evidence: Triggered by this checkpoint update on the synchronized branch.
  - command: refreshed repository CI and Required
    result: NOT_RUN
    evidence: Triggered by this checkpoint update on the synchronized branch.
blockers:
  - refreshed exact-head PRS-001 backup and PITR drill
  - refreshed exact-head repository CI and Required
  - final path, discussion and target-main drift audit before merge
next_action: Run the refreshed exact-head PRS-001 workflow, repository CI and Required, then mark PR 123 ready only if all gates and the final audit pass.
```
