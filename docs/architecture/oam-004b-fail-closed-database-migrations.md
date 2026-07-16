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

Make the ordered Lua database migration chain fail closed so persisted `db_version` cannot advance past a failed or explicitly rejected migration step, and prevent normal server startup when the migration chain fails.

## Proven task-start behavior

`DatabaseManager::updateDatabase()` previously:

- continued after migration-file load failure;
- continued after `onUpdateDatabase` runtime failure;
- asked Lua for one return value but did not enforce that value as migration success;
- could therefore execute a later migration and persist a higher `db_version` after an earlier migration failed;
- returned `void`, so startup had no explicit migration-failure gate;
- had no generic DDL rollback or reversibility guarantee.

Legacy has the same manager behavior and is not a ready fix source.

## Shipped migration compatibility

The pinned target contains two proven success conventions:

- inspected historical migrations `1.lua` and `35.lua` return no value (`nil`) from `onUpdateDatabase`;
- inspected newer migrations `53.lua`, `54.lua`, `57.lua` and `58.lua` use explicit boolean `true`/`false` outcomes.

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
2. Clear the previous global `onUpdateDatabase` binding before loading each migration, then require the newly loaded migration to define a callable function.
3. Stop immediately when `onUpdateDatabase` raises a Lua error.
4. Apply the migration result contract above and stop on explicit/invalid failure.
5. Discard migration-chunk return values so only `onUpdateDatabase` defines acceptance.
6. Persist `db_version` only after the corresponding migration step is accepted.
7. Stop the chain if persisting `db_version` fails; do not advance the in-memory current version.
8. Return an explicit success/failure status from `DatabaseManager::updateDatabase()`.
9. Abort normal `CanaryServer` startup when the migration chain returns failure.
10. Preserve ordered numeric migration discovery and skip already-applied versions.
11. Keep generic DDL rollback/reverse migration explicitly out of scope.

## Tests

- unit tests exercise ordered execution, first migration failure, version-persistence failure and current-version advancement without a real database;
- integration tests on the repository test database create temporary high-numbered migration files and verify:
  - legacy `nil` success advances the version;
  - explicit `false` returns failure, leaves `db_version` unchanged and prevents the following migration from running;
  - Lua runtime failure returns failure and leaves `db_version` unchanged.

The integration fixture restores the original `db_version`, removes temporary migration files and drops its marker table during teardown.

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
- unit and integration migration-chain tests on the final exact head;
- backward compatibility with proven legacy `nil`-returning shipped migrations preserved;
- server startup aborts on migration-chain failure;
- DDL rollback/reversibility and recovery from side effects committed before a failing migration remain explicitly unproven.
