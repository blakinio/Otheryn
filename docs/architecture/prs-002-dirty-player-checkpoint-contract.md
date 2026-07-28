# PRS-002 dirty-player checkpoint contract

## Disposition

`PRS-002 dirty-player checkpoints → DISCOVERY CONTRACT`

This milestone records the live player-save behavior and the minimum generation-safe checkpoint contract before runtime implementation. It does not add a checkpoint scheduler, retry policy, outage state machine, session fencing, schema migration or production deployment.

## Proven current behavior

### Scheduling and object ownership

- `SaveManager::savePlayer()` schedules online players while the game is not shutting down and returns `true` after accepting the scheduling request; the eventual persistence result is not returned to that caller.
- The scheduled work captures a `weak_ptr<Player>`, locks that exact object, and skips if the object disappeared. It deliberately does not re-resolve a GUID to a later session object.
- Async scheduling stores one timestamp per player GUID. A newer request makes an older detached task skip, but the timestamp is not a persistence generation and does not prove that every later mutation requested another save.
- Offline and shutdown saves use `doSavePlayer()` synchronously.
- `saveAll()` may save different players in parallel.

### Serialization and persistence domains

- `doSavePlayer()` acquires `Player::PlayerLock` for the duration of `IOLoginData::savePlayer()`.
- Representative gameplay mutation code such as `Player::addSkillAdvance()` mutates persisted fields without acquiring `PlayerLock`. The save-side lock alone therefore does not prove a consistent snapshot while async saving is enabled.
- `IOLoginData::savePlayer()` commits the SQL-backed player domains inside one `DBTransaction`.
- Wheel KV data is staged only after the SQL transaction commits. A post-commit KV staging exception returns a failed save after SQL may already be durable, so SQL/KV acknowledgement remains a separate reconciliation problem.
- Save failure is logged and returned by `doSavePlayer()`, but `SaveManager` has no dirty generation, saved generation, retry ownership or oldest-dirty-age state.

## Current risk statement

The current timestamp coalescing prevents some duplicate queued saves, but it is not a dirty-state protocol. A mutation that occurs during or after a save can be missed when no later save request is guaranteed. A successful save cannot safely clear an unversioned dirty flag because it cannot distinguish the captured state from mutations that happened during serialization. A failed async save has no durable in-memory marker that requires another bounded attempt.

No 60-second RPO, crash-loss bound or cross-domain atomicity claim is accepted from the current implementation.

## Accepted PRS-002 target contract

The first runtime implementation must provide a small, unit-testable player persistence state with these invariants:

1. Every persistence-relevant mutation advances a monotonic dirty generation.
2. A checkpoint request captures one generation and owns at most one in-flight save for one `Player` object generation.
3. The save result acknowledges only the captured generation.
4. Success clears dirty state only when no newer generation exists.
5. A mutation during save remains dirty and schedules or preserves one later bounded attempt.
6. SQL failure, exception and post-commit KV failure never acknowledge the captured generation.
7. Queue coalescing is based on generation, not wall-clock timestamps.
8. Queue capacity, oldest dirty age, attempts and failures are observable.
9. One repeatedly failing player cannot block checkpoint progress for all players.
10. Logout, handoff and graceful shutdown request a bounded final save and expose failure.
11. Ordinary game crashes do not trigger automatic whole-world rollback.
12. Session/revision fencing remains PRS-004 and is not implemented here.

## Implementation sequence

### Slice A — pure state machine

Add a database-independent `PlayerPersistenceState` value/state object with deterministic tests for:

- clean → dirty generation;
- coalesced checkpoint request;
- mutation during in-flight save;
- success acknowledgement of an unchanged generation;
- success with a newer generation remaining dirty;
- failure preserving dirty state;
- stale acknowledgement rejection;
- bounded retry eligibility.

### Slice B — SaveManager integration

Replace timestamp-only ownership with generation-aware request/in-flight state while preserving exact `Player` object ownership. Keep one in-flight save per player object and surface result metrics.

### Slice C — bounded mutation coverage

Instrument a small, explicitly owned set of representative SQL-backed player mutations first. Do not attempt whole-repository mutation instrumentation in one PR.

### Slice D — controlled failure and crash proof

Add deterministic SQL failure, mutation-during-save, commit-before-ack and queue-overload tests. Production RPO remains unknown until a controlled crash drill measures it.

### Implemented bounded PRS-002D evidence

The first bounded PRS-002D package extracts the result and exact-generation acknowledgement decision for one asynchronous player persistence attempt into a database-independent helper used by `SaveManager`. Controlled tests inject a `false` result and an exception, prove that matching failure acknowledgement leaves the state dirty and requests no follow-up, prove a later explicit generation may retry, prove a newer mutation requests follow-up only after success, and prove one held failing exact-owner state does not prevent an independent exact-owner state from succeeding.

### Implemented bounded PRS-002E evidence

The bounded PRS-002E package uses the disposable integration-test MariaDB instance and a dedicated InnoDB probe table. A valid update followed by a deliberately invalid SQL statement inside `DBTransaction::executeWithinTransaction` must return failure and roll back the earlier update. Routing that real transaction result through the checkpoint-attempt boundary proves that the captured generation remains dirty, the in-flight generation is released, no implicit follow-up is requested and a later explicit generation can commit successfully and clear the state.

### Implemented bounded PRS-002F evidence

The bounded PRS-002F package uses a standalone `KVSQL` in the disposable integration database. A dedicated SQL-domain probe commits first, then the test temporarily renames `kv_store` so the real KV batch transaction fails. The probe remains committed while the dedicated KV key is absent, and routing the combined result through the checkpoint-attempt boundary leaves the generation dirty with no implicit follow-up. Restoring `kv_store` and issuing one later explicit generation persists the still-staged key and clears the checkpoint state.

This is SQL/KV boundary evidence, not generic reconciliation or an end-to-end wheel serialization drill.

### Implemented bounded PRS-002G evidence

The bounded PRS-002G package uses a GoogleTest threadsafe death-test child with a fresh disposable-MariaDB connection. The child starts one dirty checkpoint generation, enters `executePlayerCheckpointAttempt`, commits a dedicated InnoDB probe update and calls `std::_Exit` from inside the save callback before the helper can invoke success acknowledgement. The surviving parent observes the committed value, while a newly constructed `PlayerPersistenceState` starts clean with no dirty, in-flight or acknowledged generation.

This proves the commit-before-ack process window and its ambiguity: durable SQL can survive while the dirty-generation ownership dies with the process. It does not prove a complete player SQL/KV checkpoint, automatic retry, durable checkpoint metadata, restart reconciliation or any measured RPO.

### Implemented bounded PRS-002H behavior

The bounded PRS-002H package adds an atomic admission counter around asynchronous player checkpoint submissions, with a named default runtime capacity of `1024` and smaller injectable capacities for deterministic tests. `SaveManager` acquires one slot before detaching work to the shared thread pool. A full queue abandons only the matching in-flight generation, preserves dirty state, consumes no save-failure budget and requires a later explicit scheduling request. Every admitted task releases its slot on exit, and a successful attempt releases the current slot before scheduling a newer dirty generation so capacity `1` remains live.

This bounds only asynchronous player-checkpoint admission; it does not bound unrelated users of the shared thread pool. The local capacity/outstanding accessors support deterministic proof, while Prometheus/ostream export, oldest-dirty-age tracking, attempt/failure counters, alerts, automatic retry and measured RPO remain separate work.

## Explicit non-goals

- PRS-003 database-outage state transitions;
- PRS-004 durable session/revision fencing;
- PRS-005 economic idempotency or ledger/outbox;
- generic SQL/KV reconciliation;
- unbounded retries or silent query replay;
- production scheduler, deployment, credentials or database access;
- a claimed checkpoint interval or RPO before controlled evidence.
