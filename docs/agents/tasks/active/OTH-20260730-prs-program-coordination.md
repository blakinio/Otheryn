---
task_id: OTH-20260730-prs-program-coordination
status: active
branch: dudantas/prs-program-coordination
base_branch: main
start_sha: 30ad4f41987481219faf43fdab51596a0bec4732
created: 2026-07-30
updated: 2026-07-30
related_issue: "233"
related_pr: pending
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/agents/tasks/archive/OTH-20260726-prs001-backup-pitr-foundation.md
  - docs/agents/tasks/archive/OTH-20260726-prs002-dirty-player-checkpoint-contract.md
  - docs/agents/tasks/archive/OTH-20260726-prs002a-player-persistence-state.md
  - docs/agents/tasks/archive/OTH-20260726-prs002b-generation-aware-save-scheduling.md
  - docs/agents/tasks/archive/OTH-20260726-prs002c-bounded-player-storage-mutations.md
  - docs/agents/tasks/archive/OTH-20260726-prs002d-failed-checkpoint-evidence.md
  - docs/agents/tasks/archive/OTH-20260727-prs002e-sql-failure-rollback-evidence.md
  - docs/agents/tasks/archive/OTH-20260727-prs002f-kv-post-commit-failure-evidence.md
  - docs/agents/tasks/archive/OTH-20260728-prs002g-commit-before-ack-crash-evidence.md
  - docs/agents/tasks/archive/OTH-20260728-prs002h-bounded-checkpoint-queue-admission.md
  - docs/agents/tasks/archive/OTH-20260729-prs002i-checkpoint-operational-metrics.md
  - docs/agents/tasks/archive/OTH-20260729-prs002j-final-player-save.md
  - docs/agents/tasks/archive/OTH-20260729-prs003-database-outage-contract.md
  - docs/agents/tasks/archive/OTH-20260729-prs003a-database-outage-state-machine.md
  - docs/agents/tasks/archive/OTH-20260729-prs003b-database-failure-classification.md
  - docs/agents/tasks/archive/OTH-20260729-prs003c-login-handoff-admission-policy.md
  - docs/agents/tasks/archive/OTH-20260729-prs003c-login-handoff-integration.md
  - docs/agents/tasks/archive/OTH-20260729-prs004a-session-revision-fencing-contract.md
search_first:
  - docs/agents/tasks/active/
  - docs/agents/tasks/archive/
  - open issues
  - open pull requests
  - dudantas package branches
---

# PRS program coordination — PRS-003D through PRS-008

## Mission

Coordinate terminal delivery of PRS-003D, PRS-003E, durable PRS-004, PRS-005, PRS-006, PRS-007, PRS-008, an independent final audit and closure of parent issue #116. This task owns governance and lifecycle evidence only; it owns no feature code, package architecture, schema, migration, save, handoff or deployment path.

## Live baseline

- task-start `main`: `30ad4f41987481219faf43fdab51596a0bec4732`;
- coordination issue: `#233`;
- coordinator branch: `dudantas/prs-program-coordination`;
- parent resilience issue `#116`: open;
- PRS-003C-B issue `#222`: closed completed;
- PRS-003C-B terminal feature/lifecycle/finalizer chain ends at task-start `main`;
- PRS-004A is terminal only as a pure process-local fencing contract; durable schema/CAS/save/handoff integration remains unimplemented;
- no open PRS package issue, pull request, matching `dudantas/prs*` branch or active task record was found during preflight.

## Coordinator ownership

```yaml
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
future_lifecycle_paths:
  - docs/agents/tasks/archive/OTH-20260730-prs-program-coordination.md
```

The future archive path is reserved only for the coordinator lifecycle move and finalizer. It is not active ownership while this record remains under `active/`.

## Dependency graph

```text
terminal PRS-003C-B
  ├─> PRS-003D-A policy
  │     └─> PRS-003D-B runtime mutation gates
  │           └─> PRS-003D-C bounded draining/final checkpoints
  │
  └─> PRS-003E-A test-only outage injection
          └─> PRS-003E-B recovery evidence/probes
                  └─> PRS-003E-C operator resume

terminal PRS-003D + PRS-003E
  └─> PRS-004B schema
        └─> PRS-004C CAS API
              └─> PRS-004D save wiring
                    └─> PRS-004E handoff
                          └─> PRS-004F stale-writer evidence

terminal durable PRS-004
  └─> PRS-005 one critical operation

terminal PRS-005
  └─> PRS-006 one SQL/KV domain

terminal PRS-006
  └─> PRS-007 manual replica/failover

terminal PRS-007
  └─> PRS-008 production Compose

terminal PRS-003D–PRS-008
  └─> final independent audit and issue #116 closure
```

PRS-003D-A and test-only PRS-003E-A may proceed in parallel only after exact, disjoint file ownership is proven. PRS-004 through PRS-008 may perform read-only discovery while their gates are closed, but may not modify runtime, schema or deployment paths.

## Agent roles

| Agent | Package | Initial gate |
|---|---|---|
| 1 | PRS-003D | open for bounded policy discovery |
| 2 | PRS-003E | open for test-only injection discovery |
| 3 | PRS-004 | read-only until terminal PRS-003D and PRS-003E |
| 4 | PRS-005 | read-only until durable PRS-004 |
| 5 | PRS-006 | read-only until terminal PRS-005 |
| 6 | PRS-007 | read-only until terminal PRS-006 |
| 7 | PRS-008 | read-only until terminal PRS-007 |
| 8 | final independent audit | closed until terminal PRS-003D–PRS-008 |

## Ownership registry

```yaml
active_packages: []
```

A package enters this registry only after its bounded issue, `dudantas/...` branch, single active task record and exact non-overlapping `owned_paths` exist on GitHub. Registry data mirrors those records and never replaces them.

## Conflict policy

Before accepting any feature PR, audit every active task record, open PR, package branch, declared path, actual changed file and full relevant patch. Treat shared CMake registration, resilience architecture documents, `src/database/database.cpp`, `src/io/iologindata.cpp`, save/handoff paths, migration registration and production Docker/Compose entry points as serialized resources.

If ownership overlaps, preserve the earlier valid owner, stop the later package, close any duplicate implementation PR without merge and require a narrower or refreshed slice. Never resolve overlap through a broad merge of competing implementations.

## Safety exclusions

The coordinator will not authorize reconnect/replay frameworks, `MYSQL_OPT_RECONNECT`, `mysql_ping` recovery, unknown-outcome write retry without idempotency, unbounded retry/draining, automatic maintenance resume, automatic database promotion, automatic world rollback, stale writes without durable fencing, Redis-only writer authority, success before durable commit, unauthorized schema changes, production credentials/data mutation, real deployment, local quickstart mutation for PRS-008 or unsupported RPO/RTO claims.

## CI and lifecycle state

```yaml
coordination_record:
  changed_paths:
    - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
  focused_validation: NOT_RUN
  ci: NOT_RUN
  required: NOT_RUN
  autofix: NOT_RUN
  pr: pending
program_merge_evidence:
  prs003c_b:
    feature_pr: 228
    feature_merge: ec14b683b04078aabca42cbe051fff3c5f0554a1
    lifecycle_pr: 229
    lifecycle_merge: 7bef45b2f01d410d4890ffa0bef71ed088460dc5
    finalizer_merge: 30ad4f41987481219faf43fdab51596a0bec4732
    issue: 222
    issue_state: closed_completed
  prs004a:
    feature_pr: 212
    feature_merge: b00507ec22542b8cf284040bea57bc70941d0964
    lifecycle_pr: 215
    lifecycle_merge: 87bc63889839960cc9dd7d4502cfb4e25a5eaadb
    finalizer_merge: a263e7c7370b39bbf65557ccb570cf29ed775e74
    issue: 207
    issue_state: closed_completed
```

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T08:39:00+02:00
head: 30ad4f41987481219faf43fdab51596a0bec4732
head_scope: task-start main before the coordinator-record commit
branch: dudantas/prs-program-coordination
pr: null
status: active
context_routes:
  - production-resilience
  - coordination
  - database-persistence
  - deployment
  - ci
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
proven:
  - Live main is 30ad4f41987481219faf43fdab51596a0bec4732.
  - Parent issue 116 is open and PRS-003C-B issue 222 is closed completed.
  - PRS-003C-B and PRS-004A have terminal archives with exact feature, lifecycle and finalizer evidence.
  - PRS-004A is process-local only and does not prove durable fencing.
  - No existing open coordination issue, open PRS package issue, open PRS pull request, matching dudantas/prs branch or active task record was found.
  - Issue 233 and branch dudantas/prs-program-coordination now reserve the coordinator scope.
derived:
  - PRS-003D-A and PRS-003E-A may begin in parallel only after exact disjoint ownership is established.
  - All later runtime, schema and deployment gates remain closed.
unknown:
  - Exact file ownership for PRS-003D-A and PRS-003E-A pending package-specific source discovery.
  - Exact-head coordinator PR checks pending publication.
conflicts: []
first_failure:
  marker: local-github-clone-dns-unavailable
  result: CONTAINED
  evidence: Local sandbox could not resolve github.com; live repository reads and writes use the authorized GitHub connector.
rejected_hypotheses:
  - combine multiple PRS packages into one broad feature PR
  - let a later agent take a path already owned by an earlier valid task
  - treat unresolved or process-local evidence as durable completion
  - mutate production data, credentials or deployment
changed_paths:
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
validation:
  - command: live repository preflight
    result: PASS
    evidence: main, issues, pull requests, branches, active tasks, mandatory contracts and terminal archives were audited through GitHub.
  - command: repository checkpoint validator
    result: NOT_RUN
    evidence: Run through exact-head repository CI because the local sandbox has no GitHub clone.
  - command: exact-head CI, Required and autofix
    result: NOT_RUN
    evidence: Coordinator pull request is not published yet.
blockers: []
next_action: publish the one-path coordinator pull request, require exact-head checks, and merge it only after scope, discussion and base-freshness audits pass.
```
