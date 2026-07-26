---
task_id: OTH-20260726-prs001-backup-pitr-foundation
status: completed
branch: dudantas/prs-001-backup-pitr-foundation
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "122"
related_pr: "123"
feature_head: "170e06a4c0feb2684a18f2f6b0f7bea614b0fed4"
feature_merge: "3813a25cc91e37714b69d9eac2fff9e7aaaf3cb2"
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
  - docs/agents/tasks/archive/OTH-20260726-prs001-backup-pitr-foundation.md
required_reads:
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/operations/backup-and-pitr-policy.md
  - docs/operations/production-recovery-runbook.md
search_first:
  - deploy/production/backup
  - .github/workflows/prs001-backup-pitr.yml
optional_reads: []
---

# PRS-001 backup and PITR foundation — completed

## Result

PR #123 was squash-merged as `3813a25cc91e37714b69d9eac2fff9e7aaaf3cb2`. Otheryn now contains the bounded PRS-001 physical-backup and point-in-time recovery foundation for disposable and isolated environments.

The package pins MariaDB `11.4.12` to immutable image digest `sha256:a794d9eb009e20de605858a11f32f63b4075cbd197c650436f0e3b457e4caed7`, records backup metadata and binlog coordinates, encrypts and checksum-protects recovery payloads, publishes them atomically, verifies recovery-set integrity, prepares and starts an isolated restored database, and replays a contiguous binlog range to an approved UTC target.

## Preserved boundary

- no production database, host, endpoint, credential, key or backup data was accessed;
- no production scheduler, object-store adapter, Compose rollout, replication, promotion or failover was added;
- `docker/docker-compose.yml` remained unchanged;
- no application runtime, gameplay, schema or migration behavior was changed;
- incremental backups and PRS-002 through PRS-008 remain separate work;
- disposable CI timing does not establish production RPO, RTO or readiness.

## Final checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T18:40:00+02:00
head: 3813a25cc91e37714b69d9eac2fff9e7aaaf3cb2
branch: main
pr: 123
status: completed
context_routes:
  - operations
  - database-persistence
  - docker
  - ci
  - security
  - agent-governance
proven:
  - Issue 122 defined the bounded PRS-001 package and was closed as completed after merge.
  - PR 123 changed exactly eleven declared implementation, documentation, workflow, test and task paths.
  - MariaDB 11.4.12 is pinned to immutable digest a794d9eb009e20de605858a11f32f63b4075cbd197c650436f0e3b457e4caed7.
  - The package creates a physical full backup with MariaDB metadata, coordinates and archived binary logs.
  - Recovery payloads are encrypted, checksum-protected, staged and atomically published without replacing an existing recovery-set identifier.
  - Verification rejects malformed manifests, image or version mismatch, corrupt checksums, unsafe archive paths and missing or discontinuous binlogs.
  - Restore validates coordinates and recoverable range before prepare, copy-back, isolated startup and exact-time replay.
  - The disposable drill proves the expected earlier mutation is present and the later harmful mutation is absent.
  - Backup, publication, checksum, missing-binlog, prepare, startup and invalid-range failure injections return non-zero and preserve the previous known-good set.
  - Unrelated Party teardown issue 125 was fixed and archived before final PRS-001 validation.
  - Exact-final-head PRS-001 Backup PITR run 30207709938 succeeded on 170e06a4c0feb2684a18f2f6b0f7bea614b0fed4.
  - Exact-final-head full CI run 30207710023 succeeded, including Linux debug full tests, Linux release, macOS and both Windows variants.
  - Exact-final-head autofix.ci run 30207709965 succeeded without moving the head.
  - Exact-final-head Required run 30207709926 succeeded.
  - Final comments, reviews and review-thread audits were empty.
  - The branch was behind main by zero and remained limited to the eleven declared paths immediately before merge.
  - PR 123 was squash-merged with expected head 170e06a4c0feb2684a18f2f6b0f7bea614b0fed4 as 3813a25cc91e37714b69d9eac2fff9e7aaaf3cb2.
derived:
  - The disposable proof establishes the bounded recovery mechanics, not a deployed production backup service.
  - Atomic publication and retention of the previous verified set prevent a failed run from replacing the last known-good recovery set.
  - Production storage, credentials, scheduling, capacity and measured RPO or RTO require separate packages and controlled environment evidence.
unknown:
  - The production object-store and credential-management implementation.
  - Production backup cadence, retention capacity and measured RPO or RTO.
  - Incremental-backup and automated recovery orchestration design.
conflicts: []
first_failure:
  marker: party-test-post-success-segfault
  result: RESOLVED
  evidence: Issue 125 was fixed by PR 126 and archived by PR 131; subsequent sanitizer and full Linux-debug runs passed before PRS-001 merged.
rejected_hypotheses:
  - Modify Party runtime or tests inside PRS-001.
  - Skip tests or weaken Required.
  - Turn the local Docker quickstart into the production backup stack.
  - Treat a Docker volume copy or VPS snapshot as the sole accepted database backup.
  - Use real production credentials or data for validation.
  - Expand PRS-001 into replication, failover, fencing or later PRS packages.
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
  - docs/agents/tasks/archive/OTH-20260726-prs001-backup-pitr-foundation.md
validation:
  - command: PRS-001 Backup PITR run 30207709938
    result: PASS
    evidence: Syntax, checkpoint, dependencies, physical backup, encrypted publication, verification, prepare, isolated restore, PITR and all seven failure injections passed.
  - command: full CI run 30207710023
    result: PASS
    evidence: All affected platform, runtime, schema, Lua, formatting and C++ test gates succeeded on the exact final feature head.
  - command: autofix.ci run 30207709965
    result: PASS
    evidence: Formatting automation completed without changing the final feature head.
  - command: Required run 30207709926
    result: PASS
    evidence: Required completed successfully on the same exact head.
  - command: final scope, discussion and target-main drift audit
    result: PASS
    evidence: Exactly eleven approved paths, no comments, reviews or threads, mergeable true and behind_by zero before expected-head squash merge.
blockers: []
next_action: Complete the lifecycle-only archive PR, then select PRS-002 only through a separate issue, task and bounded validation contract.
```
