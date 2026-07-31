# PRS-004B durable writer-fence schema

## Disposition

`PRS-004B durable schema -> IMPLEMENTED PENDING EXACT-HEAD VALIDATION`

This slice defines only the MariaDB authority representation required by later PRS-004 compare-and-swap work. It does not implement ownership acquisition, transfer, release, protected save statements or channel handoff.

## Durable authority object

`player_writer_fence` is a dedicated one-row-per-player authority table.

| Column | Representation | Meaning |
| --- | --- | --- |
| `player_id` | `INT(11)` primary key and foreign key | Stable fenced subject identity. |
| `ownership_generation` | unsigned `BIGINT`, default `0` | Monotonic authority generation; `0` means no active writer. |
| `writer_token` | nullable `BINARY(16)` with global uniqueness | Exact opaque writer identity; `NULL` means no active writer. |
| `state_revision` | unsigned `BIGINT`, default `0` | Durable persistence revision later protected by CAS. |

The subject primary key is sufficient for later exact-subject lookup. Global token uniqueness prevents two authority rows from naming the same active writer token.

## Fail-closed constraint

The database admits exactly two authority shapes:

```text
inactive: ownership_generation = 0 AND writer_token IS NULL
active:   ownership_generation > 0 AND writer_token IS NOT NULL
```

A zero generation with a token and a positive generation without a token are rejected. Revision remains independent because later PRS-004C/D slices define its transition rules.

## Subject lifecycle

Migration 59 creates the table, inserts one inactive row for every existing player and creates `oncreate_player_writer_fence`, an `AFTER INSERT` trigger that creates the same inactive authority row for later players.

The foreign key uses `ON DELETE CASCADE`, so deleting the stable player subject also removes its authority record. Process memory and Redis are not authoritative.

## Migration 58 to 59

The ordered migration performs three bounded operations:

1. create the authority table;
2. backfill current players as inactive;
3. create the later-player trigger.

MariaDB DDL auto-commits, so one transaction cannot make the three DDL/data operations atomic. If backfill or trigger creation fails, migration 59 performs bounded compensating cleanup of only its trigger and table and returns failure. The repository migration manager therefore does not advance `db_version`.

An already-existing authority table while the configured version is below 59 is rejected rather than treated as success. A partial or unknown schema is never silently accepted.

## Clean schema

The canonical `schema.sql` declares version 59 and contains the same table, backfill and trigger contract. Clean imports start at the current representation instead of replaying migration 59.

## Explicit rollback evidence

Rollback is an explicit disposable/operator procedure, not an automatic framework:

1. verify version 59 and the expected trigger/table;
2. drop `oncreate_player_writer_fence`;
3. drop `player_writer_fence`;
4. restore `server_config.db_version` from 59 to 58;
5. verify both objects are absent;
6. rerun the repository migration chain and verify deterministic restoration to version 59.

The focused fixture performs this cycle only against disposable databases and never uses production credentials or data.

## Later boundaries

PRS-004C may define typed acquire/transfer/release/revision compare-and-swap operations against this exact row. PRS-004D may fence protected persistence. PRS-004E may transfer authority during handoff. PRS-004F may prove stale-writer rejection.

None of those operations are implemented by PRS-004B.

## Safety exclusions

This slice adds no repository CAS API, affected-row result type, save/update SQL fencing, login or handoff wiring, Redis authority, stale-write retry/replay, generic rollback automation, production access, deployment change, later package behavior or RPO/RTO claim.

## Code rollback

Revert the feature merge only after applying the explicit schema rollback to an authorized environment that already reached version 59. Reverting repository files alone does not remove durable database objects.
