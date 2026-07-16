# OAM-004D — Player save failure propagation

Status: active bounded target adaptation

Parent: `OAM-004 — database and persistence foundation revalidation`

Target issue: `blakinio/Otheryn#10`

Task-start target:

```text
blakinio/Otheryn@4b5b94eced0f3c5d88b9a4293e849d888333e0cb
```

Dependencies:

```text
OAM-004A: 45ffe6afb915746c69125c9e74f5513c0cecdec4
OAM-004B: 1fe44d165fd8637e29ece62b261b7caa33895c65
OAM-004C: 4b5b94eced0f3c5d88b9a4293e849d888333e0cb
```

## Goal

Make the player persistence boundary explicit and fail closed where failure is actually observable, while preserving the distinction between player-owned SQL persistence and the independently flushed KV persistence domain.

## PROVEN task-start evidence

`IOLoginData::savePlayer()` owns one `DBTransaction` around `savePlayerGuard()`.

The visible SQL-backed/subsystem player saves already report failure and are converted to transaction failure through a false result or `DatabaseException`, including core player state, stash, spells, kills, bestiary, items, depot, rewards, inbox, prey, task hunting, forge history, online bosstiary, wheel slot-point SQL, weapon proficiency and player storage.

Four wheel calls executed from `saveOnlyDataForOnlinePlayer()` are different:

- `saveRevealedGems()`;
- `saveActiveGems()`;
- `saveKVModGrades()`;
- `saveKVScrolls()`.

They call `KV::set/remove`, which mutate the shared KV cache and expose no synchronous boolean result. Durable persistence is performed separately by `KVSQL::saveAll()` in its own DB transaction. OAM-004C propagates that durable KV flush result through `SaveManager::saveKV()` and aggregate `SaveManager::saveAll()`.

Because the KV cache mutations currently occur inside the player SQL transaction callback, a later SQL failure can roll back the player SQL transaction while leaving staged KV mutations in memory for later persistence.

## Bounded adaptation

1. Keep SQL-backed online player saves inside the existing single player DB transaction.
2. Move wheel KV cache staging out of the SQL transaction callback.
3. Stage those wheel KV mutations only after the player SQL transaction commits successfully.
4. Keep the KV APIs honest: do not manufacture boolean success for cache-only `set/remove` operations.
5. Keep durable KV failure reporting at `KVSQL::saveAll()` / OAM-004C aggregate world-save level.
6. Preserve player save return semantics for actual SQL transaction failure.

## Explicit unresolved boundary

Player SQL commit and later KV flush are not atomic. A process crash after player SQL commit but before a successful KV flush can still lose staged wheel KV changes. OAM-004D records this as an explicit unresolved crash/restart durability boundary rather than claiming cross-domain ACID semantics.

`KVStore::processEvictions()` may also persist cache evictions immediately while ignoring the backend `save()` boolean. That is a generic KV subsystem reliability concern and is not silently folded into this player-persistence slice.

## Non-goals

- no SQL+KV distributed transaction;
- no generic KV cache/eviction redesign;
- no cross-player/global transaction;
- no authentication redesign;
- no gameplay or protocol changes;
- no production database access.

## Acceptance

- wheel KV staging does not occur before the player SQL transaction succeeds;
- all existing SQL-backed player save failures remain fail closed;
- durable KV flush failure remains observable through OAM-004C aggregation;
- crash/restart and eviction limitations remain explicitly unresolved;
- exact-head Fast Checks, full build/runtime/database CI and `Required` pass before merge.
