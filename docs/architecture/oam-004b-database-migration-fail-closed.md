# OAM-004B Database Migration Fail-Closed Contract

Status: bounded target adaptation for `OAM-004B`

Parent governance: `blakinio/canary#420`

Target issue: `blakinio/Otheryn#8`

Pinned task-start target:

```text
blakinio/Otheryn@45ffe6afb915746c69125c9e74f5513c0cecdec4
```

Upstream evidence baseline:

```text
opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
```

Legacy evidence baseline:

```text
blakinio/canary@63e45afe684e5f923bc004a59687a5adcaac6f01
```

## Proven problem

At task start, `DatabaseManager::updateDatabase()` sorts migration files and processes versions above `db_version`, but it continues to later files after a migration script load failure or `onUpdateDatabase` runtime failure. It also requests one Lua return value without checking its semantic success value. Therefore a later successful migration can advance persisted `db_version` beyond an earlier failed step.

## Contract for this slice

For every migration step selected in ascending version order:

1. failure to reserve the script environment stops the chain;
2. failure to load/execute the migration file stops the chain;
3. `onUpdateDatabase` must exist as a callable function;
4. `onUpdateDatabase` must complete without Lua error;
5. its single return value must be boolean `true`;
6. only after those conditions pass may the corresponding `db_version` be persisted;
7. failure to persist `db_version` is itself a chain failure.

No later migration may run after the first failed step.

## Explicit non-claims

This slice does not claim that arbitrary migration DDL is transactionally reversible. MySQL/MariaDB DDL atomicity and rollback behavior remain migration-specific and must not be inferred from a fail-closed orchestration loop.

This slice also does not:

- execute migrations against production or user databases;
- add reverse migrations;
- redesign feature-table ownership;
- change existing migration SQL/Lua semantics beyond requiring explicit boolean success;
- modify player or world persistence serializers.

## Validation target

The merge gate is the exact-head ready-for-review CI/Required cycle after the implementation is complete, including clean schema import/runtime smoke where selected by the repository CI. Focused migration orchestration tests should be added where the current test harness can exercise the ordering/stop/version-advance contract deterministically without production data.
