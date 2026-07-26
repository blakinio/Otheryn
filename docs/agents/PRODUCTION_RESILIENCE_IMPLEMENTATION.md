# Production Resilience Implementation Guide

This document is the required starting point for future agents implementing production resilience, backups, crash recovery or multichannel persistence safety in Otheryn.

Authoritative architecture:

- `docs/architecture/production-resilience-and-recovery.md`
- `docs/operations/backup-and-pitr-policy.md`
- `docs/operations/production-recovery-runbook.md`

Tracking issue for the design contract: `blakinio/Otheryn#116`

## 1. First reads

Before changing code or deployment files, read:

1. `AGENTS.md`
2. `docs/agents/CONTEXT_HANDOFF.md`
3. this document
4. the three authoritative documents above
5. the exact OAM-004 persistence document relevant to the touched boundary
6. live source and tests for the selected bounded package

Do not infer current behavior from chat history or from the architecture target alone.

## 2. Evidence states

Keep every claim in one of these states:

- `PROVEN`: demonstrated by exact source, deterministic test, controlled runtime or restore evidence;
- `DERIVED`: follows from proven contracts but is not directly exercised;
- `UNKNOWN`: not established;
- `CONFLICT`: reliable evidence disagrees.

Target design text is not proof that the implementation exists.

## 3. Package rule

Work on exactly one package at a time:

```text
PRS-001 backup/PITR foundation
PRS-002 dirty-player checkpoints
PRS-003 database-outage state machine
PRS-004 multichannel revision/session fencing
PRS-005 critical-operation idempotency and ledger/outbox
PRS-006 SQL/KV reconciliation
PRS-007 replica and manual failover
PRS-008 production Compose hardening
```

A package may be split further. Do not merge packages merely because they share database or deployment files.

## 4. Required task record

Create one active task under `docs/agents/tasks/active/` with:

- exact task-start `main` SHA;
- exact branch and issue/PR;
- owned paths;
- required reads and search-first paths;
- current behavior inventory;
- accepted target contract;
- explicit non-goals;
- failure-injection plan;
- rollback plan;
- one compact `## Context checkpoint`;
- exactly one `next_action`.

Validate the checkpoint with:

```sh
python tools/agents/checkpoint.py <task-path> --require-checkpoint
```

## 5. Shared invariants that must not regress

- no `MYSQL_OPT_RECONNECT` or arbitrary SQL statement replay;
- failed transaction callbacks roll back;
- database migration failure blocks normal startup;
- save failures remain observable;
- no success response before required durable commit;
- no automatic whole-world rollback after an ordinary game crash;
- no production operation depends on a backup that has not passed isolated restore;
- no stale writer can be accepted merely because it still has Redis/session data;
- no secret or production data enters Git, CI artifacts or issue text;
- no production deployment is added to the local Docker quickstart by accident.

## 6. PRS-001 — backup and PITR foundation

### Scope

Deployment/tooling only unless source changes are independently justified.

### Required outputs

- pinned MariaDB version/image;
- durability option file validated against that version;
- full backup job;
- optional incremental job or an explicit first-release exclusion;
- off-host encrypted upload;
- binlog archive and continuity checks;
- backup manifest and checksums;
- prepare verification;
- isolated restore test;
- exact-timestamp PITR test;
- metrics and failure alerts;
- operator documentation.

### Failure injection

At minimum:

- backup command fails;
- upload fails after local backup;
- checksum mismatch;
- missing binlog segment;
- prepare fails;
- restored database cannot start;
- target timestamp falls outside recoverable range.

The job must exit non-zero and preserve the previous known-good recovery set.

### Completion proof

A disposable database receives a known sequence of mutations. The package restores to a selected time, includes expected earlier mutations, excludes a later harmful mutation, and starts the exact pinned Otheryn image in controlled mode.

## 7. PRS-002 — dirty-player checkpoints

### Discovery questions

- Which mutations already trigger player saves?
- Which state remains in RAM until logout/server save?
- Which save paths are synchronous, queued or fire-and-forget?
- How are save failures surfaced?
- Can a player mutate while a snapshot/save is being assembled?
- Which state is SQL, KV or external?

### Target contract

- dirty generation/revision recorded on mutation;
- bounded checkpoint queue;
- save snapshot belongs to one generation;
- successful save clears only the saved generation;
- changes during save remain dirty;
- failed save remains dirty and is retried only by an explicit policy;
- oldest dirty age and failures are observable;
- logout, handoff and graceful shutdown request bounded final save;
- checkpoint work cannot starve gameplay or create unbounded queue growth.

### Failure injection

- player changes during save;
- SQL failure;
- KV failure after SQL commit;
- process crash before save;
- process crash after commit but before dirty flag acknowledgement;
- overloaded checkpoint queue;
- repeated failure for one player without blocking all players.

Do not claim 60-second RPO until a controlled crash test proves it.

## 8. PRS-003 — database-outage state machine

### Required states

```text
HEALTHY
DEGRADED
DRAINING
MAINTENANCE
```

### Required decisions

- which exact errors enter `DEGRADED`;
- maximum degraded duration;
- which operations are blocked immediately;
- how new login/channel switch is disabled;
- how final checkpoints are bounded;
- how recovery returns to `HEALTHY`;
- how operators force maintenance safely.

### Prohibitions

- no arbitrary query replay;
- no endless gameplay while state cannot be persisted;
- no automatic recovery that assumes unknown writes failed;
- no hidden process exit without publishing the reason.

## 9. PRS-004 — revision and session fencing

### Required source of authority

Durable shared-state fencing must be enforced by MariaDB or an equally authoritative durable store. Redis may accelerate leases but cannot be the sole proof that a writer is current.

### Target shape

- one active epoch per character/session writer;
- monotonic state revision or compare-and-swap token;
- save/update predicates include expected epoch and revision;
- zero affected rows means stale conflict;
- handoff creates a new epoch before the new writer mutates shared state;
- old process cannot save after timeout, reconnect or delayed shutdown;
- stale rejection is logged and metered without leaking sensitive state.

### Required tests

- old writer after normal handoff;
- old writer after crash/restart;
- two channels race to acquire the same character;
- Redis unavailable while DB fencing works;
- new writer saves, old writer attempts later save;
- revision conflict without session conflict;
- duplicate disconnect/reconnect events.

## 10. PRS-005 — idempotency and economic ledger/outbox

Start with one bounded critical operation, not every economy path.

Required properties:

- stable operation ID from the command boundary;
- database uniqueness constraint;
- operation input hash or immutable business identity;
- mutation and operation result committed together;
- duplicate request returns deterministic prior result;
- unknown-outcome retry cannot duplicate value;
- append-only audit entry;
- reconciliation query for incomplete operations;
- no logging of secrets or full private payloads.

A ledger that is written after the value mutation in a separate transaction does not prove atomicity.

## 11. PRS-006 — SQL/KV reconciliation

Inventory each accepted SQL/KV domain separately.

Preferred pattern:

1. authoritative SQL mutation plus outbox event in one transaction;
2. asynchronous idempotent KV projection;
3. delivery status/retry metadata;
4. startup reconciliation of incomplete events;
5. deterministic rebuild where possible.

Do not build a generic framework before one real domain proves the abstraction.

## 12. PRS-007 — replica and manual failover

Prerequisites:

- PRS-001 restore foundation proven;
- exact MariaDB replication configuration pinned;
- monitored replica lag;
- old-primary fencing procedure;
- application endpoint cutover procedure;
- backup remains independent from replica.

Completion requires a controlled primary-loss drill. Automatic promotion remains forbidden unless a later package proves quorum/coordination and split-brain prevention.

## 13. PRS-008 — production Compose hardening

Keep production deployment separate from `docker/docker-compose.yml`.

Required properties:

- immutable images/digests;
- no default credentials;
- database and Redis private networks only;
- explicit persistent volumes and ownership;
- map/datapack read-only mounts;
- service health checks and startup dependencies;
- restart policy with crash-loop alerting;
- graceful `SIGTERM` and adequate stop grace period;
- resource limits based on measured use;
- backup jobs in a separate operational profile or scheduler;
- structured logs and metrics;
- documented upgrade and rollback;
- no claim that container health equals application/data correctness.

## 14. Validation ladder

For every package:

```text
source/config inventory
-> target contract review
-> focused static checks
-> deterministic unit/integration tests
-> controlled runtime
-> failure injection
-> restart/crash proof
-> backup/restore or fencing proof when applicable
-> exact-head CI/Required
-> clean discussion and drift audit
```

Skipping a layer requires an explicit `not-applicable` rationale.

## 15. Restore evidence record

Every restore drill should record:

```yaml
restore_id: RESTORE-YYYYMMDD-NNN
source_backup_id: exact id
source_backup_checksum: sha256
base_binlog_coordinate: exact value
target_recovery_time: ISO-8601
last_applied_binlog: exact value
mariadb_version: exact value
server_image_digest: sha256
server_source_sha: 40-hex
prepare_result: PASS|FAIL
startup_result: PASS|FAIL
pitr_result: PASS|FAIL
application_smoke: PASS|FAIL
harmful_event_absent: PASS|FAIL
rpo_seconds: integer
rto_seconds: integer
first_failure: text|null
artifacts: protected references only
```

## 16. Handoff quality gate

Before handing work to another agent, the task checkpoint must say:

- what is proven now;
- what remains unknown;
- exact current branch/head/PR;
- exact changed paths;
- exact validation results;
- first failed test or operation;
- blockers;
- one safe next action.

Do not instruct the next agent to read the previous chat.
