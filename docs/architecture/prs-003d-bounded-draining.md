# PRS-003D-C bounded draining and final checkpoints

## Disposition

`PRS-003 Slice D-C -> BOUNDED RUNTIME DRAINING AND FINAL CHECKPOINT ORCHESTRATION`

This slice advances accepted outage deadlines, drains one fixed online-player generation through existing logout/removal, records final-save evidence and enters maintenance. It does not implement recovery or resume.

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

On first observation of a new `Draining` transition count, runtime captures the current online player IDs, sorts them and starts one `DatabaseOutageDrainOrchestrator` generation.

The generation owns:

- the immutable outage transition count;
- the finite drain deadline from the immutable snapshot;
- one fixed player-ID vector;
- an attempt limit exactly equal to that vector size;
- counters for missing players, removal failures and final-save failures.

The vector never grows. Every index advances after one result. No player ID is retried by the orchestrator.

## Runtime tick

A periodic dispatcher tick performs bounded work:

1. `Degraded` with an expired deadline publishes degraded-deadline expiry and returns.
2. `Draining` starts or resumes the matching fixed generation.
3. Before the deadline, at most one captured player is attempted per tick.
4. Empty or exhausted generation publishes drain completion.
5. Deadline expiry publishes drain-deadline expiry before cleanup continues and sets `GAME_STATE_MAINTAIN`.
6. Under outage `Maintenance`, remaining IDs from the already-captured generation receive at most one cleanup attempt each.
7. Unknown or malformed runtime state fails closed by setting game lifecycle maintenance and logging explicit evidence.

Completion and deadline expiry are distinct state-machine reasons. No deadline is extended by a save failure, removal failure or timeout.

## Player removal result

`Player::removePlayerForDatabaseOutageDrain()` reuses forced `removePlayer()` and the normal synchronous removal callback. `Player::onRemoveCreature()` continues to call `SaveManager::savePlayer()` exactly once after logout state is finalized, while recording its boolean result only for an active database-outage drain removal.

The returned result contains:

- whether the player object is removed;
- whether the bounded final save was observed and succeeded.

A missing result is failure, never success. Ordinary logout behavior is unchanged.

## Failure evidence

Each player attempt produces one explicit classification:

- missing player;
- removal failed;
- final save failed;
- removed and final save succeeded.

Failures are logged and counted. They do not trigger another orchestrator attempt, deadline extension, SQL replay or automatic recovery.

## Explicit exclusions

- recovery probes and operator resume;
- automatic maintenance exit;
- reconnect, ping, SQL retry or replay;
- broad economy or additional mutation-domain gating;
- schema, migration, durable fencing or idempotency/ledger;
- production deployment or production operation.
