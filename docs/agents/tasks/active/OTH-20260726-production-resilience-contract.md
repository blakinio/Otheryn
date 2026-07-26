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
updated_at: 2026-07-26T10:51:00+02:00
head: 4c8034c1caa8b8454b9338277bbae415026219db
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
  - Current main is bd0b58a362d89e449a6863ba299d1c50ad4e6685.
  - PR 115 merged as 47863ce250bce73c1b9af3077f82e9bf6e99e3d1 and its lifecycle task was archived by bd0b58a362d89e449a6863ba299d1c50ad4e6685.
  - PR 117 audited head is 4c8034c1caa8b8454b9338277bbae415026219db on dudantas/production-resilience-contract.
  - PR 117 contains exactly the seven owned paths and no other open PR exists in the repository.
  - PR 117 has no conversation comments, submitted reviews or review threads.
  - Main drift from ff90e93d872b6b47720f711483a9832203d5258d is exactly the merged Wheel package and its lifecycle archive, with no overlap with the seven owned paths.
  - Exact-head Required run 30193714520 passed on 4c8034c1caa8b8454b9338277bbae415026219db.
  - Scope review found documentation, one non-runnable deployment boundary and one design-only MariaDB option example only.
  - No production credentials, endpoints, backup data, runnable production Compose, quickstart modification, runtime code, schema, migration or workflow change is present.
  - The architecture forbids ordinary-crash whole-world rollback, arbitrary SQL replay and automatic failover before durable fencing and split-brain prevention are proven.
  - OAM-004 fail-closed transaction, migration and save-failure contracts remain preserved; SQL versus durable KV crash atomicity remains unresolved.
  - PRS-001 through PRS-008 remain independent future packages and no PRS implementation begins in PR 117.
derived:
  - The two-commit target-main drift is semantically disjoint from the production-resilience documentation contract.
  - PR 117 may be squash-merged after its refreshed exact head passes Required and the final race-safe drift/discussion audit remains clean.
unknown:
  - Exact production VPS, storage, object-store, MariaDB image and monitoring stack.
  - Real database size, write rate, backup duration and measured RPO/RTO.
  - Exact implementation paths and schema design for PRS-002 through PRS-006.
conflicts: []
first_failure:
  marker: no-production-recovery-contract
  command: task-start repository and OAM-004 evidence review
  result: RESOLVED_BY_DESIGN
  evidence: The repository lacked an end-to-end production backup, PITR, crash, outage, stale-writer and operator recovery contract; this bounded package adds only that contract.
rejected_hypotheses:
  - Roll back the complete database after every game-process crash.
  - Treat Docker restart or healthcheck as data recovery proof.
  - Enable automatic replay of arbitrary SQL after connection loss.
  - Treat a MariaDB replica as a backup.
  - Implement automatic failover before authoritative fencing and split-brain prevention.
  - Add production behavior to the local docker quickstart.
  - Combine the eight resilience implementation packages.
changed_paths:
  - deploy/production/README.md
  - deploy/production/mariadb/99-resilience.cnf.example
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/agents/tasks/active/OTH-20260726-production-resilience-contract.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/operations/backup-and-pitr-policy.md
  - docs/operations/production-recovery-runbook.md
validation:
  - command: required first-read and OAM-004 persistence-contract review
    result: PASS
    evidence: All mandated documents were read from the PR branch and accepted invariants remain explicit.
  - command: exact seven-path and open-PR ownership audit
    result: PASS
    evidence: PR 117 has exactly seven intended paths and no competing open PR owns repository paths.
  - command: scope, secrets and unsupported-readiness audit
    result: PASS
    evidence: No secrets, endpoints, real backup data, runnable Compose, quickstart, runtime, schema, migration or workflow changes were found.
  - command: comments, reviews and unresolved-thread audit
    result: PASS
    evidence: All three discussion surfaces are empty.
  - command: target-main drift review
    result: PASS
    evidence: Main advanced by the disjoint Wheel merge and lifecycle archive only.
  - command: exact-head Required
    result: PASS
    evidence: Required run 30193714520 completed successfully on audited head 4c8034c1caa8b8454b9338277bbae415026219db.
  - command: checkpoint contract validation
    result: PASS
    evidence: The checkpoint uses the required schema, evidence states, compactness limits and one concrete next action.
blockers:
  - refreshed exact-head Required and final race-safe audit before merge
next_action: Confirm Required on the refreshed PR 117 head, repeat the seven-path, discussion, mergeability and target-main drift audit, then expected-head squash-merge PR 117 and open the lifecycle-only archive PR.
```
