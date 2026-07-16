# OAM-004B — Fail-closed database migration chain

Status: implementation slice

Parent coordination: `OAM-004` in `blakinio/canary#420`

Task issue: `blakinio/Otheryn#8`

Dependency satisfied by OAM-004A:

```text
blakinio/Otheryn@45ffe6afb915746c69125c9e74f5513c0cecdec4
```

Evidence baselines:

```text
opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01
```

## Goal

Make the ordered Lua database migration chain fail closed so persisted `db_version` cannot advance past a failed or explicitly rejected migration step.

## Proven task-start behavior

`DatabaseManager::updateDatabase()` currently:

- continues after migration-file load failure;
- continues after `onUpdateDatabase` runtime failure;
- asks Lua for one return value but does not enforce that value as migration success;
- can therefore execute a later migration and persist a higher `db_version` after an earlier migration failed;
- has no generic DDL rollback or reversibility guarantee.

Legacy has the same manager behavior and is not a ready fix source.

## Shipped migration compatibility

The pinned upstream/target migration lineage contains two success conventions:

- older shipped migrations, including versions 1, 2 and 52, return no value (`nil`) after their statements;
- newer migrations, beginning with the observed version 53 pattern, may return explicit boolean `true` or `false`.

Requiring every historical migration to return boolean `true` would break upgrades from older database versions and would force a broad rewrite of historical migration files. OAM-004B therefore defines a backward-compatible acceptance contract at the manager boundary.

## Migration result contract

After `onUpdateDatabase` returns successfully:

- `nil` means **legacy success**;
- boolean `true` means **explicit success**;
- boolean `false` means **explicit failure** and stops the chain;
- any non-boolean, non-nil result means **invalid migration result** and stops the chain.

This contract preserves existing historical migrations while allowing newer migrations to fail explicitly. It does not prove that an older migration checked every `db.query` result internally.

## Bounded implementation

1. Stop the migration chain immediately on migration-file load failure.
2. Require `onUpdateDatabase` to exist and be callable; stop when it is missing/non-callable.
3. Stop immediately when `onUpdateDatabase` raises a Lua error.
4. Apply the migration result contract above and stop on explicit/invalid failure.
5. Persist `db_version` only after the corresponding migration step is accepted.
6. Stop the chain if persisting `db_version` fails.
7. Preserve ordered numeric migration discovery.
8. Keep generic DDL rollback/reverse migration explicitly out of scope.

## Explicit non-goals

- no production/user database access;
- no reverse migration framework;
- no unrelated schema changes;
- no bulk rewrite of historical migration files;
- no player/world persistence changes;
- no feature migration;
- no broad Lua runtime changes.

## Validation

- exact-head full target CI and `Required`;
- clean schema import on temporary MariaDB;
- focused evidence that the manager stops at first failure and does not advance `db_version` after a failed step;
- backward compatibility with legacy `nil`-returning shipped migrations preserved;
- DDL rollback/reversibility remains explicitly unproven.
