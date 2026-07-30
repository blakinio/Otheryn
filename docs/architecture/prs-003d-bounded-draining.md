# PRS-003D-C bounded draining and final checkpoints

## Disposition

`PRS-003 Slice D-C -> BOUNDED RUNTIME DRAINING AND FINAL CHECKPOINT ORCHESTRATION`

This slice advances accepted outage deadlines, drains one fixed online-player generation through existing logout/removal, records the existing bounded final-save result and enters maintenance. It does not implement recovery or resume.

## Control-event serialization

`DatabaseOutageEventPublisher` remains the single serialized owner of event sequencing. It adds explicit methods for:

- degraded deadline expiry;
- drain completion;
- drain deadline expiry.

Each generated control event:

- holds the existing publisher mutex;
- receives one monotonic event sequence;
- clamps caller time to the state owner's last accepted event time;
- delegates validation and state changes to `DatabaseOutageStateMachine`;
- returns the complete `DatabaseOutageEventResult`.

No control event reconnects, pings, retries or replays SQL.

## Finite drain generation

On first observation of a new `Draining` transition count, runtime captures the current online player IDs. `DatabaseOutageDrainOrchestrator::begin` sorts and deduplicates that finite vector before admitting work.

The generation owns:

- the immutable outage transition count;
- the finite drain deadline from the immutable snapshot;
- one fixed player-ID vector;
- an attempt limit exactly equal to the unique vector size;
- at most one pending player ID;
- counters for missing players, removal failures, missing final-save observation and final-save failures.

The vector never grows. A player result is accepted only for the exact pending ID. Every accepted result advances the cursor once. A duplicate or mismatched result fails closed instead of retrying.

## Bounded runtime chain

The first classified database failure schedules one maintenance-lane dispatcher event. Runtime maintains at most one scheduled drain event.

Each event performs one bounded state action:

1. `Degraded` before its deadline schedules one event at the remaining finite delay.
2. Expired `Degraded` publishes `DegradedDeadlineExpired` and schedules the next bounded step.
3. `Draining` starts or resumes the matching fixed generation.
4. Before the drain deadline, at most one captured player is attempted per event.
5. Empty or exhausted generation publishes `DrainCompleted`.
6. Deadline expiry publishes `DrainDeadlineExpired` before cleanup continues and enters `GAME_STATE_MAINTAIN`.
7. Under outage `Maintenance`, remaining IDs from the already-captured generation receive at most one cleanup attempt each.
8. Unknown, malformed or rejected runtime state fails closed to game maintenance with explicit evidence.

Completion and deadline expiry are distinct state-machine reasons. No deadline is extended by a save failure, removal failure, timeout or scheduling rejection. The implementation adds no periodic `cycleEvent`, unbounded loop or detached save.

## Existing-save observation

`SaveManager::removePlayerForDatabaseOutageDrain` calls the existing forced `Player::removePlayer(true, true)` exactly once. That synchronous path already reaches `Player::onRemoveCreature(..., true)`, which calls `SaveManager::savePlayer` exactly once after logout state is finalized.

A thread-local scoped observer records only that existing `savePlayer` result for the exact `Player` pointer. It is cleared after success or exception. The drain method does not call `savePlayerFinal`, `doSavePlayer` or another persistence operation.

The returned result contains:

- whether the player object was removed;
- whether the existing final-save call was observed;
- whether that bounded final save succeeded.

A missing observation is explicit failure, never success. Ordinary logout behavior remains unchanged outside the active scoped observer.

## Failure evidence

Each player attempt produces one explicit classification:

- player missing;
- removal failed;
- final save not observed;
- final save failed;
- removed and final save succeeded.

Failures use fixed low-cardinality reasons, are logged and counted, and appear in the finite generation summary. They do not trigger another orchestrator attempt, deadline extension, SQL replay or automatic recovery.

## Explicit exclusions

- recovery probes and operator resume;
- automatic maintenance exit;
- reconnect, ping, SQL retry or replay;
- broad economy or additional mutation-domain gating;
- schema, migration, durable fencing or idempotency/ledger;
- production deployment or production operation.
