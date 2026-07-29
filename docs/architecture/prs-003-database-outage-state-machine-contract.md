# PRS-003 database-outage state-machine contract

## Disposition

`PRS-003 database-outage handling → DISCOVERY CONTRACT`

This milestone records the live startup and runtime database-failure behavior and accepts one bounded fail-closed state-machine contract before runtime integration. It does not add database-health transitions, reconnect, query replay, gameplay gates, schema changes or production deployment.

## Proven current behavior

### Startup is already fail closed

- `CanaryServer::initializeDatabase()` throws when the initial database connection fails.
- Database setup and migration validation run before modules, maps and network infrastructure are started.
- A failed ordered migration throws and normal startup returns failure.
- Startup therefore does not publish a playable server when the configured database is unavailable or invalid.

### Runtime database calls expose local failure only

- `Database` owns one MySQL handle serialized by a recursive mutex.
- `MYSQL_OPT_RECONNECT` is explicitly disabled.
- `Database::retryQuery()` is a compatibility wrapper that executes a statement once; it does not reconnect or resend arbitrary SQL.
- `executeQuery()` logs the MySQL error and returns `false`.
- `storeQuery()` logs the MySQL error and returns `nullptr`.
- transaction begin, callback, commit and rollback failures propagate as `false` through `DBTransaction::executeWithinTransaction()`.
- `Database::isRecoverableError()` classifies connection-related error codes but is not connected to a process-level state transition.
- no `Database` path changes `GameState_t`, blocks admission or starts a drain.

### Asynchronous database tasks do not publish outage state

- `DatabaseTasks::execute()` runs one query on the shared thread pool and optionally returns its local boolean result on the dispatcher.
- `DatabaseTasks::store()` optionally invokes its callback with `true` even when `storeQuery()` returned `nullptr`; a null result can represent either failure or an empty result at this boundary.
- neither asynchronous path classifies a failure into a central database-health state.

### Existing game lifecycle is not a database-health model

`GameState_t` currently contains:

```text
STARTUP
INIT
NORMAL
CLOSED
SHUTDOWN
CLOSING
MAINTAIN
```

- there is no `DEGRADED` or `DRAINING` state;
- `Game::setGameState()` performs lifecycle side effects for shutdown and closed states, but has no database-failure event input;
- account login rejects startup, maintenance and shutdown;
- game login rejects startup and maintenance before authentication and rejects closing/closed later for ordinary players;
- no login gate reads a database-health signal;
- current lifecycle states must not be silently overloaded with undocumented outage semantics.

### Existing persistence safety must remain intact

- arbitrary SQL replay is forbidden because commit outcome may be unknown after connection loss;
- transaction callback failure rolls back;
- player save failure remains observable;
- PRS-002 dirty generations and bounded final saves remain the only accepted final-player checkpoint boundary;
- PRS-004 session/revision fencing and PRS-005 idempotency are not available to make stale or duplicate writes safe.

## Current risk statement

After startup, one runtime persistence failure can be visible only to the immediate caller. Other sessions and gameplay paths can continue accepting work because there is no shared database-health admission policy. A later query succeeding does not establish whether an earlier write committed, and reconnecting or replaying that write could duplicate value. Continuing indefinitely can accumulate unpersistable RAM state; disconnecting everyone immediately on the first error can also discard state before bounded final checkpoint attempts are made.

No runtime outage containment, degraded-time bound, drain guarantee or automatic recovery claim is accepted from the current implementation.

## Accepted PRS-003 target model

### State ownership

Introduce one database-independent process-level state machine. It owns only database-outage policy state; it does not own the MySQL connection, player objects or game lifecycle enum.

```text
HEALTHY
DEGRADED
DRAINING
MAINTENANCE
```

The implementation must expose immutable snapshots suitable for protocol, gameplay, persistence and metrics decisions. All transitions are serialized and deterministic.

### Classified event inputs

Transitions may be driven only by fixed event types, not by parsing log messages:

- `runtimeFailure(reason, outcome, now)`;
- `degradedDeadlineExpired(now)`;
- `drainCompleted(now)`;
- `drainDeadlineExpired(now)`;
- `recoveryEvidenceAccepted(now)`;
- `operatorEnterMaintenance(now)`;
- `operatorResume(now)`.

Failure reasons must be low-cardinality classifications such as connection lost, server gone, transaction begin failed, transaction commit failed, query failed or recovery probe failed. Player names, SQL text, credentials, IDs and arbitrary exception strings are forbidden as labels.

Commit outcome is classified as:

```text
KNOWN_NOT_COMMITTED
UNKNOWN
```

`UNKNOWN` means the application cannot prove whether a submitted write committed. It must never authorize replay.

### Transition invariants

1. The initial state is `HEALTHY`.
2. The first qualifying runtime persistence failure with a known-not-committed outcome enters `DEGRADED` and records one immutable first-failure timestamp and one finite degraded deadline.
3. A failure with unknown commit outcome enters `DRAINING` directly.
4. Any additional qualifying persistence failure while degraded enters `DRAINING`; repeated failures never extend or reset the original degraded deadline.
5. Expiry of the degraded deadline enters `DRAINING`.
6. Entry to `DRAINING` records one finite drain deadline. It cannot return directly to `HEALTHY`.
7. Drain completion or drain-deadline expiry enters `MAINTENANCE` with distinct fixed reasons.
8. Operator maintenance may be entered from any non-shutdown state and never auto-resumes.
9. Recovery evidence may make a degraded state eligible for explicit recovery, but one successful query is insufficient and does not itself change state.
10. `operatorResume` may enter `HEALTHY` only after accepted recovery evidence and only from `DEGRADED` or `MAINTENANCE`.
11. Returning to healthy clears the active failure interval only after emitting the transition snapshot; counters remain monotonic.
12. Shutdown remains owned by the existing game lifecycle and dominates further outage transitions.

Durations are finite constructor/configuration inputs with deterministic test values. Production values remain unknown until controlled runtime evidence measures final-save and disconnect behavior.

## Admission contract

| Operation class | HEALTHY | DEGRADED | DRAINING | MAINTENANCE |
|---|---|---|---|---|
| new account/game login | existing policy | reject | reject | reject except explicit staff diagnostic path |
| channel switch/handoff | existing policy | reject | reject | reject |
| critical economy mutation | existing policy | reject | reject | reject |
| ordinary persistence-relevant gameplay mutation | existing policy | reject unless explicitly proven safe and non-durable | reject | reject |
| read-only/mutation-free activity | existing policy | may continue during finite grace | bounded teardown only | operator diagnostics only |
| PRS-002 final player checkpoint | existing policy | allowed when requested | bounded attempt during drain | operator-directed only |
| health/recovery probe | observe | bounded cadence | bounded cadence without auto-resume | operator-directed |

Until a call site has an explicit operation classification, the fail-closed classification is persistence-relevant mutation.

## Drain contract

- entry to draining closes new login and channel-switch admission before disconnect work begins;
- critical and ordinary persistence-relevant mutations are rejected before their durable side effect is acknowledged;
- each online player is removed through the existing lifecycle so PRS-002 can attempt its bounded synchronous final save;
- final-save failure is logged and metered but never extends the finite drain deadline;
- drain deadline expiry proceeds to maintenance even when some final saves failed or timed out;
- no automatic whole-world rollback follows drain failure;
- drain ordering and concurrency limits belong to a dedicated implementation slice and require deterministic tests.

## Recovery contract

A recovery candidate requires all of the following:

1. the underlying connection/session was explicitly re-established by a bounded owner;
2. at least one read probe succeeds;
3. one dedicated transactional write/rollback probe succeeds without touching gameplay data;
4. no qualifying failure occurs during the required consecutive probe window;
5. an explicit recovery decision is issued.

A successful ordinary gameplay query is not a health probe. Recovery never retries an operation with unknown commit outcome. Maintenance never auto-resumes merely because probes succeed.

## Observability contract

Expose low-cardinality current values and monotonic events for:

- current outage state;
- fixed transition reason;
- first-failure Unix timestamp;
- degraded deadline and drain deadline;
- transition count by fixed from/to/reason;
- qualifying failures by fixed reason and outcome;
- recovery probe attempts and failures;
- drain starts, completions and deadline expiries;
- final-save failures observed during draining.

Logs must include state, fixed reason and transition time. They must not include credentials, full SQL statements, player-private payloads or unbounded labels.

## Bounded implementation sequence

### Slice A — pure state machine

Add one database-independent state object with injectable clock/durations and deterministic tests for every accepted transition, deadline, stale event and recovery-eligibility invariant. Do not wire it into `Database`, protocols or gameplay in the same slice.

### Slice B — failure classification and telemetry

Classify runtime database results into fixed reasons/outcomes and publish events to the state owner without reconnect or replay. Preserve all existing caller-visible `false`/`nullptr` behavior.

### Slice C — login and handoff admission

Gate account/game login and channel-switch entry points from immutable outage snapshots. Keep existing staff/lifecycle behavior explicit and tested.

### Slice D — mutation admission and draining

Introduce explicit bounded operation classes, reject unclassified durable mutations fail closed, and orchestrate PRS-002 final-save removal under one finite drain deadline.

### Slice E — recovery probes and controlled outage evidence

Add disposable-database failure injection for connection loss, unknown commit outcome, probe recovery, repeated failure, grace expiry, drain completion and drain timeout. Production RTO/RPO remains unknown until controlled deployment evidence exists.

## Discovery failure-injection requirements

Future implementation tests must prove:

- startup connection and migration failure remain fail closed;
- first known-not-committed failure enters degraded exactly once;
- unknown commit outcome enters draining without replay;
- repeated degraded failures do not reset the deadline;
- degraded deadline expiry enters draining;
- successful probes do not auto-resume;
- drain completion and timeout enter maintenance with different reasons;
- final-save failure cannot create an unbounded drain;
- one stale or duplicate transition event cannot reverse state;
- no state transition depends on parsing a database error string.

## Explicit non-goals

- runtime implementation in this discovery milestone;
- implicit reconnect or arbitrary query replay;
- connection pooling;
- automatic process restart, automatic database promotion or whole-world rollback;
- schema, migration, credential or production deployment changes;
- PRS-004 session/revision fencing;
- PRS-005 operation idempotency or economic ledger/outbox;
- PRS-006 SQL/KV reconciliation;
- PRS-007 replica/failover;
- PRS-008 production Compose hardening;
- production RPO/RTO claims before controlled evidence.
