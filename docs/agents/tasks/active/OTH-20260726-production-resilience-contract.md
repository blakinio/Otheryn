---
task_id: OTH-20260726-production-resilience-contract
status: ready
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
updated_at: 2026-07-26T10:07:00+02:00
head: 67a8fc5a0dd24da252a80301364dc5ad3eebf9d1
branch: dudantas/production-resilience-contract
pr: 117
status: ready
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
  - PR 117 contains exactly the seven owned paths, is mergeable and has no comments, reviews or review threads.
  - Draft Required 30193557983 and ready-head Required runs 30193655938 and 30193658250 passed.
  - Active Wheel PR 115 still targets the same task-start main and remains open, so merge order must avoid unnecessary target-main drift during its final validation.
derived:
  - Canary/Otheryn can use container restarts for process availability while keeping database state authoritative after an ordinary channel crash.
  - Safe future multichannel persistence requires database-enforced revision/session fencing rather than Redis-only leases.
  - Critical retryable economy operations require idempotency identities and transactionally coupled audit/outbox state.
unknown:
  - Exact production VPS, storage, object-store, MariaDB image and monitoring stack.
  - Real database size, write rate, backup duration and acceptable measured checkpoint interval.
  - Exact source paths and schema design for PRS-002 through PRS-006.
  - Final target-main SHA and merge order after OAM-051A PR 115 completes.
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
  - command: checkpoint contract validation
    result: PASS
    evidence: Required fields, statuses, validation-result enums and compactness limits match docs/agents/GOVERNANCE_CONTRACT.json.
  - command: exact changed-path and discussion audit
    result: PASS
    evidence: PR 117 has exactly seven owned paths and no comments, reviews or review threads.
  - command: draft and ready-head Required
    result: PASS
    evidence: Required runs 30193557983, 30193655938 and 30193658250 completed successfully on their exact heads.
  - command: merge-order conflict audit
    result: PASS
    evidence: PR 115 is open on the same main base; PR 117 remains unmerged to avoid introducing avoidable drift into the active Wheel validation.
blockers:
  - active PR 115 merge-order coordination
  - final target-main drift audit immediately before merge
next_action: Before merging PR 117, re-fetch main and PR 115; merge the active Wheel package first or explicitly rebase the chosen later PR, then repeat exact-head Required and drift checks without starting PRS-001.
```
