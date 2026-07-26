# Production Recovery Runbook

Status: **operator contract; commands and service names must be adapted to the pinned deployment package**

Tracking issue: `blakinio/Otheryn#116`

Related documents:

- `docs/architecture/production-resilience-and-recovery.md`
- `docs/operations/backup-and-pitr-policy.md`

## 1. Safety principles

1. Preserve evidence before changing data.
2. Stop public writes before attempting database repair or restore.
3. Never restore an old backup over the only copy of the current database.
4. Never automatically roll back the whole world after an ordinary game-process crash.
5. Never retry an arbitrary write whose commit result is unknown.
6. Recover into an isolated database first.
7. Record exact timestamps, image digests, SHAs, backup IDs and binlog positions.
8. Keep one incident commander and one declared source of truth.

## 2. Incident record

Create an incident record immediately with:

```yaml
incident_id: INC-YYYYMMDD-NNN
opened_at: ISO-8601
severity: SEV-1|SEV-2|SEV-3
commander: operator
symptom: concise description
first_bad_time: ISO-8601|null
last_known_good_time: ISO-8601|null
server_image_digest: sha256:...
server_source_sha: 40-hex
mariadb_image_or_version: exact value
map_hash: exact value
data_hash: exact value
channels_affected: []
write_status: enabled|blocked|unknown
current_primary_preserved: false
selected_runbook: null
recovery_point: null
actions: []
validation: []
```

Do not put passwords, tokens or private keys into the incident record.

## 3. First response checklist

1. Confirm whether the game process, database process, host, storage or network failed.
2. Stop new logins and channel switches if database durability is uncertain.
3. Block critical economy mutations if writes cannot be proven.
4. Capture process exit code, crash dump/core, logs and container inspect output.
5. Capture database error log and current readiness state.
6. Record the exact current time and last successful checkpoint/save/backup/binlog archive.
7. Preserve current database volumes and binlogs before destructive action.
8. Select exactly one scenario below.

## 4. Scenario A — one game channel crashed, database healthy

### Entry conditions

- MariaDB is healthy and accepts bounded read/write checks;
- no database corruption or unknown migration state is observed;
- only one game process/channel failed.

### Actions

1. Mark the channel unavailable at the login layer.
2. Confirm its session/heartbeat lease will expire or is explicitly fenced.
3. Preserve crash evidence.
4. Restart only the affected channel from the exact pinned image.
5. Verify the process receives a new runtime/session epoch when fencing is implemented.
6. Verify database migrations do not run unexpectedly or fail.
7. Verify the channel loads the expected map/datapack hashes.
8. Verify login, one controlled character load and logout/save.
9. Re-advertise the channel only after health and persistence checks pass.

### Forbidden actions

- restoring a database backup;
- rolling back every player to the last server save;
- restarting all channels without evidence that they are affected;
- clearing session locks manually without recording the operation.

### Exit evidence

- crash cause or `UNKNOWN`;
- restart count;
- channel recovery time;
- oldest lost non-durable checkpoint interval, when measurable;
- controlled save success;
- no stale-writer rejection or an explained expected rejection.

## 5. Scenario B — MariaDB crashed, storage appears intact

### Entry conditions

- database process stopped unexpectedly;
- data volume is present;
- no confirmed logical corruption or operator error.

### Actions

1. Keep game channels stopped or in maintenance.
2. Preserve the MariaDB error log and container/process metadata.
3. Start MariaDB normally and allow InnoDB crash recovery.
4. Do not set `innodb_force_recovery` for an ordinary crash.
5. Wait for database health/readiness.
6. Inspect recovery messages, aborted transactions and storage errors.
7. Run bounded integrity checks defined by the deployment package.
8. Verify current schema version and last successful backup/binlog archive.
9. Start one controlled non-public game process for runtime smoke.
10. Restore public service gradually.

### Escalate to Scenario C when

- MariaDB repeatedly crashes during startup;
- corruption is reported;
- expected tables or schema versions are missing;
- data reflects a harmful logical operation;
- the current primary cannot pass integrity checks.

## 6. Scenario C — logical corruption, bad migration or operator error

### Entry conditions

- a harmful mutation is identified;
- database is readable but semantically wrong; or
- current data cannot be trusted.

### Actions

1. Block all writes and public logins.
2. Record the earliest known harmful timestamp and last known good timestamp.
3. Preserve a snapshot/copy of the current database and all binlogs.
4. Select the newest verified backup chain older than the harmful event.
5. Restore the chain into an isolated recovery instance.
6. Prepare the physical backup if not already prepared.
7. Read the backup binlog coordinates.
8. Inspect binlogs around the harmful event.
9. Select a stopping timestamp/position immediately before the harmful change.
10. Replay binlogs into the isolated instance only.
11. Run the validation checklist in section 10.
12. Obtain incident approval for cutover.
13. Stop the old primary permanently from accepting writes.
14. Promote the recovered instance through the controlled deployment procedure.
15. Start one non-public game process, then public services gradually.

### Forbidden actions

- replaying binlogs directly into the only damaged primary;
- deleting the damaged data before incident closure;
- selecting a recovery point based only on file modification time;
- reopening public writes before validation.

## 7. Scenario D — primary VPS or storage lost

### Actions

1. Treat the old host as unavailable and potentially capable of returning.
2. Fence the old host at the network, credential and database-write layers.
3. Decide between off-host restore and manual replica promotion.
4. For restore, use Scenario C from verified off-host artifacts.
5. For replica promotion, require the separately approved replica/fencing package.
6. Rotate credentials that existed on the lost host.
7. Verify image, map, datapack, configuration and database identities.
8. Restore service gradually.

Automatic promotion is forbidden until split-brain prevention is proven.

## 8. Scenario E — database unavailable while game processes remain alive

### Immediate behavior target

```text
healthy
  -> transient-degraded
  -> draining
  -> maintenance/stopped
```

### Operator actions

1. Stop new logins and channel switches.
2. Disable critical economy operations.
3. Observe whether in-flight writes returned known failure or unknown outcome.
4. Do not manually replay unknown writes.
5. Attempt only bounded final checkpoints whose transaction ownership is valid.
6. Enter maintenance and disconnect players before unpersistable RAM state grows without bound.
7. Recover the database using Scenario B, C or D.
8. Restart game processes from durable state.

Until `PRS-003` is implemented, operators must not claim that this state machine is automatic.

## 9. Emergency InnoDB extraction

`innodb_force_recovery` is an emergency read/extraction tool. It does not repair corruption.

Rules:

- use only after preserving the original data;
- start at the lowest level and increase one level at a time only if required;
- isolate the instance from public writes;
- extract data to a new clean database;
- never continue normal production on forced-recovery mode;
- document every level attempted and result.

Prefer a known-good backup plus PITR when available.

## 10. Recovered-state validation

Minimum validation before cutover:

### Database

- expected schema version;
- no migration startup failure;
- account and player counts within explained bounds;
- no orphaned critical foreign-key relationships where enforced;
- sampled bank, guild-bank, market and item ownership checks;
- sampled house/tile persistence checks;
- latest expected binlog event is at or before the selected recovery point;
- no harmful event is present.

### Application

- exact server image digest and source SHA;
- exact map/datapack hashes;
- controlled startup completes;
- login succeeds for a disposable/test account;
- character load succeeds;
- bounded mutation and logout save succeeds;
- restart and second load observe the saved state;
- no public service exposure during validation.

### Multichannel, when implemented

- only one authoritative writer per character;
- stale session write is rejected;
- one login gateway advertises only healthy channels;
- channel hashes and build identities match policy;
- Redis/cache loss does not bypass database fencing.

## 11. Cutover checklist

1. Freeze the selected recovered database state.
2. Record final checksums and recovery coordinates.
3. Confirm the old primary cannot accept writes.
4. Update the deployment to the recovered database endpoint.
5. Start database and verify readiness.
6. Start login service but keep public routing closed.
7. Start one game channel and run controlled smoke.
8. Start remaining channels sequentially.
9. Open public login.
10. Monitor writes, checkpoint age, errors and stale-writer rejections.
11. Preserve incident artifacts until review completion.

## 12. Rollback of the recovery attempt

If validation or cutover fails:

- stop public writes again;
- do not write back into the preserved old primary;
- return to the previous isolated recovery checkpoint or create a new recovery attempt;
- record the first failed validation;
- avoid stacking untracked manual fixes on the recovery database.

## 13. Post-incident requirements

Within the incident review:

- exact timeline;
- first failure and root cause or explicit `UNKNOWN`;
- achieved RPO and RTO;
- data lost, duplicated or manually repaired;
- why automatic controls did or did not engage;
- backup/PITR evidence used;
- stale-writer/idempotency evidence;
- corrective bounded tasks with owners;
- update to this runbook when the actual procedure differed.

Do not close an incident only because services restarted.
