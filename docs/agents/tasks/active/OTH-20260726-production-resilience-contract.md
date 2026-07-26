---
task_id: OTH-20260726-production-resilience-contract
status: validating
branch: dudantas/production-resilience-contract
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "116"
related_pr: "117"
owned_paths:
  - docs/architecture/production-resilience-and-recovery.md
  - docs/operations/backup-and-pitr-policy.md
  - docs/operations/production-recovery-runbook.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - deploy/production/README.md
  - deploy/production/mariadb/99-resilience.cnf.example
  - docs/agents/tasks/active/OTH-20260726-production-resilience-contract.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/operations/backup-and-pitr-policy.md
  - docs/operations/production-recovery-runbook.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
search_first:
  - docs/architecture/oam-004a-database-transaction-integrity.md
  - docs/architecture/oam-004b-fail-closed-database-migrations.md
  - docs/architecture/oam-004c-world-save-failure-propagation.md
  - docs/architecture/oam-004d-player-save-failure-propagation.md
  - docker/docker-compose.yml
optional_reads: []
---

# Production resilience and recovery design contract

## Goal

Define a durable, evidence-bounded architecture for game-process crash recovery, MariaDB crash recovery, backup/PITR, database-outage behavior, dirty-player checkpoints, multichannel stale-writer fencing, critical-operation idempotency and future production Docker packaging. Produce operator and future-agent documents without changing production runtime, schema, quickstart Docker or deployment behavior.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T09:56:00+02:00
head: edd30610e2e30e2f6c52ed97113178cc9c2d030c
branch: dudantas/production-resilience-contract
pr: 117
status: validating
context_routes:
  - architecture
  - operations
  - database-persistence
  - docker
  - multichannel
  - agent-governance
owned_paths:
  - docs/architecture/production-resilience-and-recovery.md
  - docs/operations/backup-and-pitr-policy.md
  - docs/operations/production-recovery-runbook.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - deploy/production/README.md
  - deploy/production/mariadb/99-resilience.cnf.example
  - docs/agents/tasks/active/OTH-20260726-production-resilience-contract.md
proven:
  - Task-start Otheryn main is ff90e93d872b6b47720f711483a9832203d5258d.
  - Issue 116 owns the documentation-only architecture scope and explicitly authorizes no runtime, schema, deployment or production database mutation.
  - OAM-004 already disables silent DB reconnect/replay, rolls back failed callbacks, stops failed migrations and propagates world-save failures.
  - OAM-004 leaves player SQL versus durable KV atomicity and complete crash/restart semantics explicitly unresolved.
  - The existing docker/docker-compose.yml is a local quickstart with MariaDB health dependency and restart policies, not a production backup/PITR deployment.
  - The new architecture forbids automatic whole-world rollback after an ordinary game-process crash and separates restart, InnoDB crash recovery, PITR and host-loss recovery.
  - The backup policy requires prepared, checksummed, encrypted off-host backups and isolated exact-time restore drills before production readiness is claimed.
  - The agent guide defines bounded PRS-001 through PRS-008 implementation packages and failure-injection gates.
  - deploy/production is established only as a non-runnable future ownership boundary; the MariaDB option file is explicitly design-only and not mounted anywhere.
  - Draft PR 117 starts from exact task base ff90e93d872b6b47720f711483a9832203d5258d and contains exactly the seven owned paths.
derived:
  - Canary/Otheryn can use container restarts for process availability while keeping database state authoritative after an ordinary channel crash.
  - Safe future multichannel persistence requires database-enforced revision/session fencing rather than Redis-only leases.
  - Critical retryable economy operations require idempotency identities and transactionally coupled audit/outbox state.
unknown:
  - Exact production VPS, storage, object-store, MariaDB image and monitoring stack.
  - Real database size, write rate, backup duration and acceptable measured checkpoint interval.
  - Exact source paths and schema design for PRS-002 through PRS-006.
  - Whether repository documentation/checkpoint validators accept the final text unchanged.
  - Exact-head draft PR CI and Required outcome.
conflicts: []
first_failure:
  marker: no-production-recovery-contract
  command: task-start repository and OAM-004 evidence review
  result: RESOLVED_BY_DESIGN
  evidence: Existing persistence hardening did not define an end-to-end production backup, PITR, crash, outage, stale-writer or operator recovery contract; this bounded package adds that contract without claiming implementation.
rejected_hypotheses:
  - Roll back the complete database after every game-process crash.
  - Treat Docker restart or healthcheck as data recovery proof.
  - Enable automatic query replay after connection loss.
  - Treat a MariaDB replica as a backup.
  - Implement automatic failover before fencing and split-brain prevention.
  - Add production behavior to the local docker quickstart.
  - Combine all resilience implementation packages into one broad PR.
changed_paths:
  - deploy/production/README.md
  - deploy/production/mariadb/99-resilience.cnf.example
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/agents/tasks/active/OTH-20260726-production-resilience-contract.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/operations/backup-and-pitr-policy.md
  - docs/operations/production-recovery-runbook.md
validation:
  - command: task-start OAM-004 and Docker quickstart contract review
    result: PASS
    evidence: Current proven and unresolved persistence/deployment boundaries are separated in the new documents.
  - command: official MariaDB and Docker operating-reference review
    result: PASS
    evidence: Design aligns with current MariaDB redo/PITR/binlog guidance and Docker restart/health dependency semantics; final implementation must revalidate pinned versions.
  - command: scope and safety audit
    result: PASS
    evidence: Only documentation, a non-runnable deployment boundary and a design-only option example are changed; no runtime, schema, workflow, quickstart or production data path changes.
  - command: draft PR creation and exact changed-path audit
    result: PASS
    evidence: PR 117 is open as draft with exactly seven owned paths and zero target-base drift at creation.
  - command: checkpoint validator
    result: NOT_RUN
    evidence: Requires repository checkout or CI on the committed task record.
  - command: exact-head Required
    result: NOT_RUN
    evidence: Awaiting PR 117 workflow results.
blockers:
  - checkpoint/documentation validation
  - exact-head draft PR CI and Required
  - clean discussion and target-main drift audit
next_action: Inspect PR 117 exact-head CI and Required, repair only documentation/checkpoint defects, then mark the PR ready without starting PRS-001 implementation.
```
