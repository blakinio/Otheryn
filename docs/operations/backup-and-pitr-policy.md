# Backup and Point-in-Time Recovery Policy

Status: **design policy; no production backup is established until a restore drill passes**

Tracking issue: `blakinio/Otheryn#116`

Architecture contract: `docs/architecture/production-resilience-and-recovery.md`

## 1. Policy objective

Otheryn must be recoverable after database corruption, operator error, complete VPS loss and an unusable primary database. A backup is accepted only when it is complete, prepared, checksummed, stored outside the production failure domain and successfully restored in an isolated drill.

## 2. Initial protection schedule

The values below are initial production targets and must be validated against real database size, write rate and storage cost.

| Artifact | Target frequency | Minimum retention | Required location |
|---|---:|---:|---|
| full physical backup | daily | 14 days | off-host encrypted storage |
| incremental physical backup | hourly | 72 hours | off-host encrypted storage |
| binary-log archive | continuous or no more than 5-minute delay | 14 days | off-host encrypted storage |
| weekly recovery point | weekly | 8 weeks | off-host immutable/versioned storage |
| monthly recovery point | monthly | 12 months | off-host immutable/versioned storage |
| configuration/manifests | on every production change | matching release retention | Git plus protected release artifact |

A production package may simplify the first release to daily full backups plus continuously archived binlogs if incremental operation is not yet proven. It must not weaken off-host storage, checksums or restore testing.

## 3. Backup set contents

Every recovery set must bind:

- exact Otheryn image digest and source SHA;
- exact MariaDB image/version;
- full backup identifier and completion time;
- incremental chain identifiers, when used;
- `xtrabackup_binlog_info` or equivalent binlog coordinates;
- first and last archived binlog identifiers;
- database schema version;
- datapack/map revision and hashes;
- configuration revision with secrets redacted;
- encryption key identifier, not the key itself;
- SHA-256 checksums for every stored artifact;
- backup tool output and prepare result;
- last verified recoverable timestamp.

Do not store production passwords, encryption keys or tokens in the manifest.

## 4. Durability configuration baseline

A future pinned MariaDB deployment should begin from the following conservative durability intent and verify every option against the selected MariaDB version:

```ini
[mariadb]
server_id=1
log_bin=mariadb-bin
binlog_format=ROW
binlog_row_image=FULL
sync_binlog=1
innodb_flush_log_at_trx_commit=1
binlog_expire_logs_seconds=1209600
```

Notes:

- `1209600` seconds is 14 days;
- binlog expiry must exceed the maximum backup gap and any accepted replica lag;
- archived binlogs must be copied off-host before local expiry;
- `ROW` is selected for deterministic row-change replay and replication safety, accepting larger storage use;
- the final package must benchmark I/O latency before changing durability values;
- lowering `sync_binlog` or `innodb_flush_log_at_trx_commit` is an explicit RPO decision and cannot be a silent performance tweak.

GTID and replica settings are deferred to the replica/failover package. Do not enable them casually in the backup-only package.

## 5. Backup creation contract

A backup job must:

1. acquire a unique backup identifier;
2. verify the database is the expected production instance;
3. verify sufficient local and remote free space;
4. run `mariadb-backup --backup` with binlog coordinates enabled;
5. fail if the tool exits non-zero or expected metadata is missing;
6. generate checksums before upload;
7. encrypt before or during upload;
8. upload to off-host storage;
9. verify remote object size and checksum;
10. record success only after all required artifacts are durable remotely;
11. emit metrics and an alert on failure;
12. avoid deleting the previous known-good recovery set during the same run.

A job that only copies `/var/lib/mysql`, a Docker volume or a VPS snapshot is not accepted as the sole database backup mechanism.

## 6. Prepare and verification contract

MariaDB physical backups are not considered restore-ready merely because the copy command succeeded.

For each daily full chain:

1. restore or copy the chain into an isolated verification workspace;
2. apply incremental backups in order when present;
3. run `mariadb-backup --prepare`;
4. verify the prepared state exits successfully;
5. start an isolated MariaDB instance from a restored copy;
6. run schema/version checks and bounded Otheryn integrity queries;
7. record the exact recoverable binlog position/timestamp;
8. destroy the disposable verification database after retaining evidence.

Preparation and restore testing must never run against the production data directory.

## 7. Point-in-time recovery contract

PITR uses a prepared physical backup as the base and binary logs as the ordered change stream.

Required procedure:

1. select an incident-approved target timestamp or GTID/position;
2. preserve the damaged/current primary and all available binlogs;
3. restore the selected backup into a new isolated data directory;
4. start the isolated MariaDB instance;
5. replay binlogs from the backup coordinate to the selected stopping point;
6. stop replay exactly before the harmful event when recovering from operator error;
7. validate schema, account/player counts, sampled critical balances/items and application startup;
8. record the selected point, applied binlogs and validation results;
9. perform controlled cutover only after approval;
10. retain the former production data until the incident is closed.

Never replay binlogs directly into the damaged production instance as the first recovery attempt.

## 8. Retention and deletion

Deletion is allowed only when:

- at least one newer full recovery chain has passed prepare and isolated startup validation;
- required binlogs for all retained recovery points remain available;
- no active incident or legal/operational hold applies;
- remote immutable/versioned retention policy permits deletion;
- deletion is logged with artifact identifiers.

Do not use broad commands such as `docker system prune -a --volumes` in production maintenance. Database and backup volumes require explicit ownership and deletion procedures.

## 9. Encryption and access

Minimum controls:

- encryption in transit and at rest;
- separate backup credentials from database runtime credentials;
- write-only or limited-scope upload credentials where supported;
- restore credentials accessible only to designated operators;
- keys stored outside Git and outside the backup bucket;
- access logging and alerting for deletion or policy changes;
- object-lock/immutability or versioning for at least weekly recovery points;
- periodic key-recovery test.

## 10. Recovery drills

### Weekly automated verification

- prepare the newest full/incremental chain;
- start isolated MariaDB;
- run bounded integrity checks;
- verify expected binlog coordinates and archive continuity;
- record duration and result.

### Monthly operator drill

- choose a random retained recovery point;
- restore to an isolated host or namespace;
- replay binlogs to a specified timestamp;
- start the exact pinned Otheryn image against the restored database in non-public mode;
- validate login/schema/runtime smoke without production writes;
- record achieved RPO/RTO and discrepancies.

### Quarterly disaster drill

- assume the entire production VPS and local storage are gone;
- recover only from off-host artifacts and documented credentials;
- verify that no undocumented local file is required.

A failed drill invalidates the claim that the backup chain is production-ready until repaired and re-run.

## 11. Required alerts

Alert when:

- no successful full backup exists within 30 hours;
- no successful incremental backup exists within 2 hours, when incremental mode is enabled;
- binlog archive lag exceeds 10 minutes;
- remote checksum verification fails;
- prepare/restore verification fails;
- recoverable timestamp is older than the accepted RPO;
- local binlog or backup filesystem exceeds capacity thresholds;
- a backup retention deletion fails or deletes an unexpected artifact;
- the backup credential or encryption-key policy changes.

## 12. Acceptance gate for `PRS-001`

The backup foundation is complete only when all are proven on a disposable environment pinned to exact revisions:

- full backup succeeds;
- optional incremental chain succeeds;
- checksummed encrypted off-host upload succeeds;
- prepare succeeds;
- isolated database startup succeeds;
- PITR to an exact test timestamp succeeds;
- a known harmful test mutation is excluded by the selected recovery point;
- Otheryn starts against the recovered database in controlled smoke mode;
- failure injection produces alerts and a non-zero job result;
- no secret or production data is committed to Git.

## 13. Explicit nonclaims

This policy does not prove:

- that a current production backup exists;
- that every current table is semantically consistent after restore;
- that SQL and KV are atomic;
- that a replica can be promoted safely;
- that application checkpoint RPO is already 60 seconds;
- that automated failover is safe.
