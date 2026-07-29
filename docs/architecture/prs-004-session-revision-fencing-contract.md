# PRS-004 session/revision fencing contract

## Disposition

`PRS-004 player/session revision fencing → SLICE A PURE MODEL`

PRS-004A defines one deterministic, database-independent fencing state object and focused tests. It does not modify the database schema, player-save SQL, live session ownership, login protocol, channel switching or production persistence behavior.

Pure in-memory evidence alone does not prove durable fencing across process restart, database failover or concurrent writers in different processes. Production stale-writer safety remains unestablished until a later package enforces this contract atomically in the authoritative database.

## Current proven baseline

- `PlayerPersistenceState` owns dirty, acknowledged and in-flight generations for one exact live `Player` object. It prevents stale checkpoint acknowledgement inside that object lifecycle, but it is not a durable session fence shared by channels or process generations.
- PRS-002 final save is bounded and generation-safe for one live object. A delayed worker from another object, process or channel is not database-fenced by that contract.
- Player SQL commit and later KV persistence are not one atomic transaction.
- PRS-003A provides only process-local outage policy state. It does not authorize or fence player writers.
- No current schema column or conditional player-save update proves ownership generation plus persistence revision at the durable write boundary.

## Threat model

The protected subject is one stable durable player identity. Threats include:

1. a paused, disconnected or delayed old channel completing a save after a newer channel owns the player;
2. an asynchronous save worker completing after logout, crash recovery or handoff transferred authority;
3. a lower persistence revision overwriting a higher revision;
4. duplicate acquire, transfer, release or persist events racing inside one process;
5. stale or reordered event delivery;
6. malformed or missing subject, generation, writer-token, revision or sequence context being treated as authorization;
7. a crash leaving an old writer alive long enough to submit a delayed durable update;
8. both sides of a channel handoff believing they can write concurrently.

PRS-004A assumes callers and future durable adapters preserve the stable subject identity and issue monotonic ownership generations and event sequences. It does not assume a correct wall clock and defines no time lease.

## Terminology

| Term | Meaning |
|---|---|
| subject ID | Stable non-zero durable player identity protected by one fence. |
| ownership generation | Non-zero monotonic epoch identifying one authoritative ownership generation. It never moves backward. |
| writer token | Non-zero token identifying the writer authorized within the current ownership generation. |
| persistence revision | Monotonic durable-state revision. PRS-004A authorizes only the exact successor `current + 1`. |
| event sequence | Caller-supplied non-zero monotonic sequence used to reject stale and duplicate state transitions. |
| vacant | No ownership has yet been acquired. |
| owned | Exactly one generation/token pair is authorized. |
| released | The previous owner is invalidated. Reacquisition requires a strictly newer generation. |
| effective transition | An acquire, transfer, release or revision advance that changes fence authority or revision and increments the transition counter. |

The ownership generation is not the existing PRS-002 dirty generation. The dirty generation tracks mutation/checkpoint progress for one live object. The ownership generation fences whole writer epochs across session, handoff and restart boundaries.

## State model

`src/database/session_revision_fence.hpp` owns one `SessionRevisionFence` per stable subject and exposes immutable snapshots containing:

- subject ID;
- `VACANT`, `OWNED` or `RELEASED` status;
- current ownership generation;
- current persistence revision;
- current authorized writer token or zero when no writer is authorized;
- last accepted event sequence;
- fixed last transition reason;
- monotonic transition count.

All operations are internally serialized. The object acquires no time, starts no thread, sleeps nowhere and depends on no database, protocol, scheduler, player object or external service.

## Fixed events

### Acquire

`acquire(sequence, subject, generation, writer)` is effective only when:

- all values are non-zero;
- subject matches the fence;
- sequence is newer than the last accepted sequence;
- the fence is vacant or released;
- generation is strictly newer than every previously accepted generation.

An acquisition identical to the current owner is a deterministic duplicate no-op. A different writer cannot reuse the same generation. A newer generation cannot replace an active owner through acquire; active ownership requires explicit transfer.

### Transfer

`transfer(sequence, current-owner, next-generation, next-writer)` is effective only when:

- current subject, generation and writer token exactly match the active owner;
- next generation is strictly greater than current generation;
- next writer token is non-zero;
- sequence is fresh.

Transfer changes generation and writer atomically in the model while preserving persistence revision. There is no intermediate snapshot in which both writers are authorized.

### Release

`release(sequence, current-owner)` is effective only for the exact active owner and a fresh sequence. It clears the authorized writer token, preserves generation and revision, and enters released state. The released writer cannot persist. Reacquisition requires a strictly newer generation.

### Persist / revision advance

`mayPersist(owner, proposed-revision)` answers the pure decision question. Authorization requires:

- complete non-zero context;
- matching subject;
- owned state;
- exact current ownership generation;
- exact current writer token;
- proposed revision equal to `current persistence revision + 1`.

`persist(sequence, owner, next-revision)` applies that decision to the process-local model under its mutex and advances the revision only when authorized. Lower revisions, equal revisions and revision gaps are rejected without advancing the model.

The non-mutating decision is not a production check-and-then-write primitive. A future database adapter must combine the same predicates and revision advance in one atomic conditional statement or transaction.

## Decision table

| Condition | Disposition | Fixed reason | Effective transition |
|---|---|---|---|
| zero/missing required value | rejected malformed | `MalformedContext` | no |
| wrong subject | rejected subject | `SubjectMismatch` | no |
| lower event sequence | rejected stale event | `StaleEventSequence` | no |
| equal event sequence | rejected duplicate event | `DuplicateEventSequence` | no |
| exact repeated active acquisition | accepted duplicate | `OwnershipAlreadyHeld` | no |
| active acquire with newer generation | rejected state | `TransferRequired` | no |
| exact valid first/reacquisition | applied | `OwnershipAcquired` | yes |
| transfer by stale generation | rejected generation | `StaleOwnershipGeneration` | no |
| generation reused for another writer | rejected generation | `OwnershipGenerationConflict` | no |
| wrong current writer token | rejected writer | `WriterMismatch` | no |
| exact valid handoff | applied | `OwnershipTransferred` | yes |
| exact valid release | applied | `OwnershipReleased` | yes |
| persist while vacant/released | rejected state | `FenceNotOwned` | no |
| proposed revision below current | rejected revision | `StalePersistenceRevision` | no |
| proposed revision equal current | rejected revision | `DuplicatePersistenceRevision` | no |
| proposed revision above next | rejected revision | `PersistenceRevisionGap` | no |
| exact next revision | applied/authorized | `PersistenceRevisionAdvanced` | yes |
| revision counter exhausted | rejected revision | `PersistenceRevisionExhausted` | no |

Equal-revision handling is fencing duplicate detection only. It does not establish PRS-005 business-operation idempotency and does not authorize another durable mutation.

## Safety invariants

1. **Older session fenced:** once generation `G+1` owns the subject, generation `G` cannot pass the exact-generation check.
2. **Older revision fenced:** a revision lower than the current revision cannot advance or overwrite the model.
3. **Duplicate determinism:** equal event sequence and repeated acquisition have fixed no-op outcomes.
4. **Stale sequence rejection:** event sequence cannot move backward or repeat.
5. **No ownership regression:** acquire and transfer require a strictly newer generation when authority changes.
6. **Release invalidates:** released state has no authorized writer and the previous token cannot persist.
7. **Single-authority handoff:** transfer exposes one atomic before/after authority change and preserves revision.
8. **Delayed completion fenced:** a delayed old owner fails generation or token matching after transfer/reacquisition.
9. **Zero invalid:** zero subject, generation, writer token, revision and event sequence are rejected where required.
10. **At-most-one effective duplicate transition:** mutex serialization plus sequence checks allow one effective transition for concurrent identical acquire/transfer events.
11. **Fail closed:** unknown, incomplete or mismatched context never maps to authorization.
12. **Transition counter integrity:** the counter increments only for effective ownership/revision changes.

## Channel-handoff contract

A future handoff integration must:

1. stop the source channel from initiating new persistence work for the subject;
2. obtain a new monotonic ownership generation from the durable authority owner;
3. atomically transfer the database fence from source generation/token to destination generation/token;
4. publish destination ownership only after the durable transfer succeeds;
5. treat zero affected rows as stale-owner rejection;
6. preserve the latest persistence revision across transfer;
7. allow the destination to write only with the new generation/token;
8. keep delayed source work fenced even when it completes after handoff.

No protocol handler or channel-switch path is modified by PRS-004A.

## Future database enforcement point

The eventual authoritative write must condition on subject, ownership generation, writer token and current revision in the same durable operation. The target shape is conceptually:

```sql
UPDATE player_state
SET state_revision = state_revision + 1,
    ...
WHERE player_id = ?
  AND session_generation = ?
  AND writer_token = ?
  AND state_revision = ?;
```

A zero-row update is stale-writer or stale-revision rejection, never success. Acquisition, transfer and release also require database-enforced compare-and-swap semantics. Exact table placement, token representation, migration and transaction ownership belong to a later PRS-004 package.

Redis, process memory or a channel-local mutex alone is insufficient for durable shared-state fencing.

## Crash and delayed-writer scenarios

### Previous process pauses then resumes

Process A owns generation 10. After failover or handoff, process B durably owns generation 11. A delayed write carrying generation 10 is rejected even when its revision would otherwise be next.

### Old save completes after transfer

A source save worker captures generation 20 and revision 8. Transfer publishes generation 21 while preserving revision 8. The old worker cannot commit revision 9 because its generation/token no longer match. The destination may commit revision 9 with generation 21.

### Released owner retries

Release preserves generation/revision but clears writer authority. Any post-release completion fails `FenceNotOwned`. Reacquisition at the same generation is rejected; a newer generation is required.

### Process restart

A new process-local `SessionRevisionFence` starts vacant and has no durable knowledge. It must not infer authority from an empty in-memory object. A later adapter must load or acquire the durable fence before enabling writes.

### Database failover

PRS-004A does not prevent split brain or prove that a promoted database contains the latest fence row. Failover requires separate topology, promotion and fencing evidence.

## Deterministic evidence

`tests/unit/database/session_revision_fence_test.cpp` covers:

- invalid subject and missing context;
- first acquisition;
- deterministic duplicate acquisition;
- explicit transfer to newer generation;
- stale previous owner rejection;
- current owner acceptance;
- lower, equal, skipped and exact-next revisions;
- release/invalidation;
- reacquisition with newer generation;
- stale transfer and release rejection;
- stale and duplicate event sequences;
- wrong-subject and malformed context failing closed;
- immutable before/after snapshots;
- transition counter behavior;
- concurrent duplicate acquisition and transfer with at most one effective transition.

These tests prove the process-local contract and linearized outcomes only. They do not prove cross-process atomicity or durable enforcement.

## Explicit non-goals

- database schema or migration;
- SQL conditional-update wiring;
- production player-save integration;
- login, protocol or channel-switch runtime changes;
- distributed lock service or external consensus;
- wall-clock lease or automatic expiry;
- automatic reconnect, arbitrary SQL replay or retry loop;
- database failover or split-brain prevention;
- PRS-005 operation idempotency;
- PRS-006 SQL/KV reconciliation;
- production RPO/RTO claims.

## Next bounded implementation slices

1. **Durable fence schema and repository adapter:** add one explicit schema contract and database compare-and-swap operations for acquire, transfer, release and revision advance, with disposable-database tests.
2. **Player persistence integration:** pass durable fence context into the selected player-save transaction and treat zero-row updates as stale-write failure without replay.
3. **Channel-handoff integration:** serialize source quiesce, durable transfer and destination activation.
4. **Crash/restart evidence:** prove delayed old workers and restarted processes fail closed against the durable fence.
5. **Observability:** expose low-cardinality stale-generation, stale-token and stale-revision rejection metrics.

Each slice requires a separate issue, task record, owned paths, focused failure evidence and exact-head validation.
