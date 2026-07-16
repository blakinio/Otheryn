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

## Bounded implementation

1. Stop the migration chain immediately on migration-file load failure.
2. Stop immediately when `onUpdateDatabase` is missing or raises a Lua error.
3. Define the migration success contract as an explicit boolean `true` returned by `onUpdateDatabase`.
4. Treat missing/non-boolean/false results as migration failure.
5. Persist `db_version` only after the corresponding migration step returns explicit success.
6. Preserve ordered numeric migration discovery.
7. Keep generic DDL rollback/reverse migration explicitly out of scope.

## Compatibility gate

Before changing migration-manager semantics, inspect the currently shipped migration files used by the configured `DATA_DIRECTORY` and confirm that successful migrations already return boolean `true`. If a shipped migration uses a different success convention, adapt only that migration contract in this bounded PR and record it explicitly; do not silently reinterpret arbitrary Lua truthiness.

## Explicit non-goals

- no production/user database access;
- no reverse migration framework;
- no unrelated schema changes;
- no player/world persistence changes;
- no feature migration;
- no broad Lua runtime changes.

## Validation

- exact-head full target CI and `Required`;
- clean schema import on temporary MariaDB;
- focused evidence that the manager stops at first failure and does not advance `db_version` after a failed step;
- current shipped migration success contract verified before merge;
- DDL rollback/reversibility remains explicitly unproven.
