# OAM-004C — World save failure propagation

Status: active bounded target adaptation

Parent: `OAM-004 — database and persistence foundation revalidation`

Target issue: `blakinio/Otheryn#9`

Task-start target:

```text
blakinio/Otheryn@1fe44d165fd8637e29ece62b261b7caa33895c65
```

Dependencies:

```text
OAM-004A: merged as 45ffe6afb915746c69125c9e74f5513c0cecdec4
OAM-004B: merged as 1fe44d165fd8637e29ece62b261b7caa33895c65
```

## Goal

Make bounded world-save failures observable and fail closed without introducing a single transaction across players, guilds, houses, map and KV persistence.

## PROVEN task-start evidence

- `IOMapSerialize::saveHouseItems()` reports replacement failure through a `false` transaction callback.
- OAM-004A changed the shared transaction helper so `false` rolls back. Therefore OAM-004C must prove the house path now rolls back; it must not duplicate DB-core transaction logic.
- `IOGuild::saveGuild()` returns `void` and discards the result of its database `UPDATE`.
- `SaveManager::saveAll()` returns `void`, waits for player save futures, logs individual failures and continues through guild/map/KV saves without an aggregate success result.
- `SaveManager::saveGuild()`, `saveMap()` and `saveKV()` expose no status to `saveAll()`.
- `scheduleAll()` may execute `saveAll()` asynchronously, so asynchronous orchestration cannot return a result to the caller but must make aggregate failure visible in logs.

## Intended bounded adaptation

1. Change `IOGuild::saveGuild()` to return `bool` from the database write.
2. Make synchronous `SaveManager::saveAll()` return an aggregate `bool` while preserving best-effort continuation across independent save domains.
3. Make guild/map/KV helper methods return success status to the aggregate.
4. Preserve player save transaction ownership and existing per-player failure handling; OAM-004D owns player child-save propagation.
5. Make asynchronous `scheduleAll()` log if the aggregate save result is false.
6. Add focused proof that a `false` callback rolls back the house-save transaction under the OAM-004A DB contract.
7. Add focused tests for aggregate save-result semantics where existing test seams allow deterministic injection without production DB mutation.

## Explicit non-goals

- no giant cross-domain transaction;
- no player-persistence/OAM-004D implementation;
- no static OTBM or map migration;
- no backup/restore subsystem redesign;
- no production database access;
- no change to DB retry/reconnect semantics established by OAM-004A;
- no change to schema migration semantics established by OAM-004B.

## Acceptance

- failed guild DB write is observable;
- synchronous global save returns false when any bounded save domain fails;
- successful domains continue to be attempted after an independent domain failure;
- asynchronous scheduled save logs aggregate failure;
- house-item replacement false-callback rollback is covered by focused test evidence;
- exact-head Fast Checks, full build/runtime/database tests and `Required` pass before merge.
