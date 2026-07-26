# Production Resilience and Recovery Architecture

Status: **active design contract; implementation not authorized by this document alone**

Tracking issue: `blakinio/Otheryn#116`

Task-start target:

```text
blakinio/Otheryn@ff90e93d872b6b47720f711483a9832203d5258d
```

## 1. Purpose

This document defines the target reliability model for a production Otheryn deployment, including future multichannel operation. It separates process restart, database crash recovery, point-in-time restore, stale-writer prevention and application-level state durability.

The objective is not to promise that crashes never happen. The objective is to make failures bounded, observable, recoverable and unable to silently duplicate, erase or overwrite durable game state.

## 2. Current proven baseline

The following contracts already exist and must be preserved:

- database operations fail instead of silently reconnecting and replaying arbitrary statements;
- `DBTransaction::executeWithinTransaction()` rolls back when its callback fails;
- ordered database migration failure stops the chain and normal startup;
- world-save domains propagate success/failure instead of discarding it;
- player SQL save commits before Wheel KV mutations are staged;
- server and Lua root lifecycles have explicit shutdown boundaries.

Relevant evidence:

- `docs/architecture/oam-004a-database-transaction-integrity.md`
- `docs/architecture/oam-004b-fail-closed-database-migrations.md`
- `docs/architecture/oam-004c-world-save-failure-propagation.md`
- `docs/architecture/oam-004d-player-save-failure-propagation.md`

Current limitations remain explicit:

- player SQL commit and later durable KV flush are not atomic;
- complete crash/restart recovery semantics are not proven for all persistence paths;
- a Docker restart policy restarts a process but does not make in-memory state durable;
- no multichannel stale-writer fencing contract is proven in Otheryn;
- no production backup, PITR or replica topology is delivered by the repository quickstart.

## 3. Reliability targets

These are initial design targets. A production deployment package must benchmark and either accept or revise them with evidence.

| State class | Initial RPO target | Initial RTO target |
|---|---:|---:|
| committed critical economy operation | 0 acknowledged committed operations | 5 minutes after one game-process crash |
| ordinary dirty player state | at most 60 seconds | 5 minutes after one game-process crash |
| one game channel | database state remains authoritative | 5 minutes |
| primary database service | committed InnoDB transactions preserved | 30 minutes for ordinary crash recovery |
| corrupted database or operator error | restore to selected safe timestamp | 2 hours |
| complete VPS loss | off-host restore or manual replica promotion | 4 hours |

`RPO 0` applies only after the server has acknowledged a transaction as committed. It does not mean every in-memory gameplay mutation is synchronously persisted.

## 4. Failure taxonomy

### 4.1 Game-process crash

Examples: segmentation fault, fatal assertion, out-of-memory termination or forced container exit.

Expected response:

1. stop advertising the failed channel;
2. expire or fence its sessions;
3. restart the channel from the pinned image;
4. load the latest durable database state;
5. do **not** restore an old database snapshot automatically.

An ordinary game-process crash is not, by itself, authorization for a whole-world rollback.

### 4.2 Database process crash

InnoDB redo and undo recovery are responsible for restoring the database to a transactionally consistent state after normal crash startup. Otheryn must remain stopped or unavailable until the database passes readiness and application-level integrity checks.

Do not use `innodb_force_recovery` during normal recovery. It is an emergency data-extraction mode, not a repair or production operating mode.

### 4.3 Database outage with unknown commit outcome

A connection failure after a statement was sent may leave the application unable to know whether the database committed it. Therefore:

- arbitrary write replay is forbidden;
- only explicitly idempotent operations may be retried;
- critical mutations require an operation identity or transactionally stored deduplication key;
- prolonged database failure must move the affected game process to fail-closed draining or maintenance.

### 4.4 Logical corruption or operator error

Examples: bad migration, accidental `DELETE`, duplicated economic mutation or incorrect bulk update.

Expected response:

1. block further writes;
2. preserve the current database, logs and binlogs as evidence;
3. restore a full/incremental backup into an isolated recovery instance;
4. replay binary logs only to the selected pre-incident point;
5. validate recovered state before production cutover.

### 4.5 Host or storage loss

A backup stored only on the production VPS is considered lost with that VPS. Recovery requires an off-host copy or a separately hosted replica plus off-host backups.

### 4.6 Multichannel stale writer

A disconnected or paused channel must not overwrite newer state written by another channel. Every future multichannel write path touching shared durable player or economy state must use a database-enforced fencing condition.

## 5. State ownership classes

### 5.1 Critical transactional state

Examples:

- bank and guild-bank balance changes;
- market offer creation, fill, cancellation and expiry;
- direct trade finalization;
- store purchase and paid reward claims;
- valuable item creation, destruction or transfer;
- house transfer and ownership mutation;
- account sanctions or entitlement changes.

Required properties:

- one explicit transaction owner;
- fail-closed result propagation;
- unique operation identity where retry/reconnect is possible;
- no success response before durable commit;
- append-only audit/ledger or transactional outbox when the operation crosses subsystems;
- deterministic duplicate detection.

### 5.2 Checkpointed player state

Examples:

- experience, level, skills and vocation progression;
- inventory, depot, inbox and stash;
- quest/storage state;
- charms, prey, bosstiary and Wheel state;
- position and ordinary character metadata.

Target model:

- mark changed players dirty;
- checkpoint dirty players in bounded batches;
- default target interval no greater than 60 seconds;
- always checkpoint on normal logout, channel handoff and graceful shutdown;
- expose checkpoint age, queue depth, duration and failures as metrics;
- never clear dirty state until the owning durable save reports success.

### 5.3 Per-channel world state

Examples:

- house items and doors;
- persistent map/tile state;
- channel-owned runtime metadata.

A future multichannel package must define whether each row is globally identified, channel-scoped or audited with a source channel. This document does not import the legacy multichannel schema.

### 5.4 Ephemeral runtime state

Examples:

- monsters and ordinary NPC runtime instances;
- combat target and temporary pathfinding state;
- projectiles, visual effects and short-lived timers;
- local chat and non-durable encounter state.

This state may be reconstructed or lost after a crash unless a specific module establishes a stronger durable contract.

## 6. Required application invariants

### 6.1 No blind global rollback

A database restore affects all players and channels. It is allowed only for proven database corruption, unrecoverable logical damage or host loss, and only after the incident owner selects the recovery point.

### 6.2 Fail closed on persistence unavailability

When durable writes cannot be trusted:

- stop new logins and channel switches;
- block critical economy operations;
- stop accepting mutations whose safe persistence cannot be established;
- enter draining/maintenance after a bounded grace period;
- disconnect players only after attempting the bounded final checkpoint;
- never continue indefinitely on unpersistable RAM state.

### 6.3 Revision and session fencing

The target shared-state write shape is:

```sql
UPDATE player_state
SET state_revision = state_revision + 1,
    ...
WHERE player_id = ?
  AND state_revision = ?
  AND session_epoch = ?;
```

A zero-row update is a stale-write rejection, not success. Exact table placement and schema changes belong to a separate implementation package.

Required concepts:

- monotonic `state_revision` or equivalent compare-and-swap token;
- session or lease epoch bound to the authoritative writer;
- new epoch after crash/restart/handoff;
- database validation, not Redis alone, for durable shared-state fencing;
- metrics and alerts for stale-write rejection.

### 6.4 Idempotency

Every retryable critical command needs a stable `operation_id`. The database must enforce uniqueness within the operation's business scope. Receiving the same operation again returns the recorded result or a deterministic duplicate response; it does not execute the mutation twice.

### 6.5 Cross-store mutations

SQL plus KV, SQL plus Redis or SQL plus an external service are not one transaction merely because one function invokes both.

Preferred order:

1. commit authoritative SQL state and an outbox/ledger event in one transaction;
2. asynchronously apply secondary state;
3. mark delivery complete idempotently;
4. reconcile incomplete deliveries after restart.

Do not introduce distributed transactions without a separate explicit architecture decision.

## 7. Target production topology

Initial production remains a modular monolith per channel, deployed as separate processes/containers:

```text
public edge
  -> login service/gateway
  -> game channel 1
  -> game channel 2 ... N

private network
  -> MariaDB primary
  -> Redis when an accepted multichannel package requires it
  -> metrics/log collection

separate failure domain
  -> backup repository/object storage
  -> optional MariaDB replica
```

Rules:

- one immutable server image is reused across channels;
- image tags must resolve to immutable digests or release SHAs;
- database and Redis are not published to the public network;
- map/datapack inputs are read-only to game containers;
- runtime data, logs and database data use explicit persistent volumes;
- health checks establish readiness, not data correctness;
- restart policies are process availability controls, not recovery guarantees;
- production deployment remains separate from `docker/docker-compose.yml`, which is a local quickstart.

## 8. Backup and recovery layers

The required layers are complementary:

1. InnoDB redo/undo crash recovery for a database-process crash;
2. application checkpoints for state otherwise held only in RAM;
3. binary logs for point-in-time roll-forward;
4. prepared full/incremental physical backups;
5. off-host encrypted retention;
6. optional replica for reduced host-failure RTO;
7. tested runbooks and isolated restore drills.

A replica is not a backup because destructive logical changes can replicate.

## 9. Observability and automatic response

Minimum signals:

- process restart count and crash-loop state;
- channel heartbeat age and advertised availability;
- player checkpoint queue depth, oldest dirty age and save failures;
- last successful full/incremental backup;
- last archived binlog and recoverable timestamp;
- backup prepare/verification result;
- database readiness, connection failures and transaction failures;
- disk usage for data, binlogs and backups;
- stale-writer and duplicate-operation rejections;
- aggregate server-save result;
- replica lag when a replica exists.

Automatic restart may be used for a single game-process crash. Automatic database promotion and automatic rollback are forbidden until a later package proves fencing, split-brain prevention and recovery validation.

## 10. Delivery sequence

Future agents must implement this architecture in bounded packages:

1. `PRS-001` — production backup, binlog and isolated restore-drill foundation;
2. `PRS-002` — dirty-player checkpoint scheduler and metrics;
3. `PRS-003` — database outage state machine: healthy, degraded, draining, maintenance;
4. `PRS-004` — player/session revision fencing for multichannel shared writes;
5. `PRS-005` — critical-operation idempotency and economic outbox/ledger;
6. `PRS-006` — SQL/KV reconciliation for accepted cross-store domains;
7. `PRS-007` — optional replica and manual failover with explicit fencing;
8. `PRS-008` — production Compose packaging, hardening and rollback validation.

Each package requires its own issue, task-start SHA, owned paths, failure injection, rollback plan and exact-head validation. This document grants no permission to combine the sequence into one broad PR.

## 11. Explicit non-goals

- no automatic whole-world rollback after an ordinary game crash;
- no Kubernetes requirement;
- no automatic MariaDB failover;
- no speculative distributed transaction framework;
- no claim that all current gameplay persistence is crash-safe;
- no production secrets or credentials in Git;
- no modification of the local Docker quickstart;
- no migration of the legacy multichannel implementation by implication.

## 12. External operating references

Use exact documentation for the pinned production versions during implementation:

- MariaDB InnoDB redo log and crash recovery: <https://mariadb.com/docs/server/server-usage/storage-engines/innodb/innodb-redo-log>
- MariaDB Backup PITR: <https://mariadb.com/docs/server/server-usage/backup-and-restore/mariadb-backup/point-in-time-recovery-pitr-mariadb-backup>
- MariaDB Backup prepare/restore options: <https://mariadb.com/docs/server/server-usage/backing-up-and-restoring-databases/mariadb-backup/mariadb-backup-options>
- MariaDB binary log: <https://mariadb.com/docs/server/server-management/server-monitoring-logs/binary-log>
- Docker restart policies: <https://docs.docker.com/engine/containers/start-containers-automatically/>
- Docker Compose service health/dependencies: <https://docs.docker.com/reference/compose-file/services/>
