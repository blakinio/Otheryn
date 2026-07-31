# PRS-003E-C explicit operator resume control

## Disposition

`PRS-003E-C operator resume -> IMPLEMENTED PENDING EXACT-HEAD VALIDATION`

This slice adds one typed, database-independent C++ operator API and deterministic command-contract evidence. It completes the explicit PRS-003 recovery decision boundary without adding automatic resume, reconnect, SQL replay, a production Lua/HTTP/console transport or direct game-lifecycle mutation.

## Existing accepted boundaries

The existing PRS-003 state owner already provides `operatorResume(sequence, now)`. It accepts only `DEGRADED` or `MAINTENANCE`, requires previously accepted recovery evidence, rejects stale sequence/time and enters `HEALTHY` only on an explicit call. A later qualifying failure clears recovery evidence.

Terminal PRS-003E-B supplies the bounded evidence decision. E-B does not call operator resume and does not expose a production transport.

## Typed operator request

`DatabaseOutageOperatorControl` receives one existing `DatabaseOutageStateMachine` by reference and owns no clock, scheduler, thread, database connection, permission store, transport or game lifecycle.

A resume request contains:

- an authorization decision supplied by the caller;
- explicit operator confirmation;
- the exact expected outage state;
- the exact observed transition count;
- the exact observed last event sequence;
- one new caller-supplied monotonic event sequence;
- one caller-supplied monotonic event time.

The expected state, transition count and last event sequence form a generation precondition. An operator cannot inspect one outage generation and blindly resume a later one.

## Evaluation order

One request is evaluated once in fixed order:

1. authorization;
2. explicit confirmation;
3. non-zero fresh event sequence and non-regressing time;
4. exact expected state;
5. exact expected transition count;
6. exact expected last event sequence;
7. eligible `DEGRADED` or `MAINTENANCE` state;
8. accepted recovery evidence;
9. one call to the existing state owner's `operatorResume`.

Precondition rejections do not call the state owner and therefore do not consume its event sequence. A race after the initial snapshot remains fail closed because the state owner independently validates sequence, time, state and accepted evidence.

## Result contract

Every result contains fixed low-cardinality disposition and action enums plus immutable before/after snapshots. Rejected requests emit `None`.

Only an applied owner event whose transition snapshot and final owner snapshot are both `HEALTHY` emits:

```text
ResumeGameLifecycle
```

This action is an explicit instruction to the caller. The API itself does not call `Game::setGameState`, schedule work or change protocol admission. A future transport must authenticate the operator and route the emitted action through the existing lifecycle owner.

## Deterministic evidence

The standalone C++ probe proves:

- repeated status inspection is read-only;
- healthy state rejects resume without consuming state-owner sequence;
- unauthorized and unconfirmed requests reject;
- wrong expected state, transition generation or event generation rejects;
- duplicate and regressing events reject;
- ordinary runtime state without accepted evidence is insufficient;
- degraded resume succeeds only after accepted evidence;
- maintenance resume succeeds only after accepted evidence;
- accepted evidence never auto-resumes before the explicit request;
- successful resume clears the active failure interval in the final owner snapshot;
- duplicate explicit requests do not emit a second lifecycle action;
- a later qualifying failure invalidates evidence and blocks resume;
- concurrent explicit requests produce exactly one applied resume and one lifecycle action.

The runner compiles with C++20 warnings-as-errors, executes the concurrent evidence repeatedly under a finite timeout and verifies source boundaries.

## Safety boundaries

This slice adds no:

- automatic recovery or automatic game-state change;
- connection establishment, reconnect, ping or database operation;
- retry or replay of a failed or unknown-outcome operation;
- production Lua, HTTP, console or UI transport;
- production permission or credential store;
- login, handoff, mutation, drain, final-save or recovery-probe change;
- schema, migration, deployment or production credential change;
- PRS-004+ implementation or RPO/RTO claim.

## Rollback

Revert the feature merge. All feature paths are new and E-C-specific. No persistent production state, schema, credential, migration, transport or deployment surface is created.
