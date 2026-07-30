# PRS-003D-B runtime bank mutation gate

## Disposition

`PRS-003 Slice D-B -> ONE CRITICAL-DURABLE RUNTIME GATE`

This slice wires the accepted PRS-003D-A policy into one existing live mutation seam only: bank balance changes routed through `Bank::balance(uint64_t)`. It does not claim complete economy or gameplay mutation coverage.

## Runtime contract

`DatabaseOutageMutationGate::executeLive()`:

1. captures exactly one immutable `DatabaseOutageSnapshot` from a caller-supplied provider;
2. evaluates the accepted pure policy using an explicit operation class and current `GameState_t`;
3. returns immediately without invoking the mutation when rejected;
4. invokes the supplied boolean mutation exactly once when allowed;
5. preserves the mutation's caller-visible boolean result.

The execution result carries the fixed policy decision, whether the mutation executed and the mutation's boolean result. The adapter performs no database query, wait, retry, replay, logging, scheduling or state transition.

## Bank classification

`Bank::balance(uint64_t)` is explicitly classified as `CriticalDurable` because it changes value-bearing player or guild state that must not be acknowledged while durability cannot be trusted.

The gate is evaluated before `Bankable::setBankBalance()`. Rejection returns `false`; the setter is not called. Existing `Bank::credit`, `debit`, `transferTo`, `withdraw` and `deposit` paths continue to converge on this seam.

No operation is inferred as ephemeral. This package adds no default classification for other gameplay, storage, item, market or Lua mutation boundaries.

## Snapshot and lifecycle

The live bank integration uses:

- `getDatabaseOutageSnapshot()` as the accepted process-level immutable snapshot seam;
- `Game::getGameState()` as the current lifecycle input;
- `DatabaseOutageMutationOperation::CriticalDurable` as the explicit operation class.

One bank-balance attempt captures one snapshot. The same snapshot is used for the complete decision and is never mutated.

## Rejection behavior

The existing pure-policy reasons remain authoritative:

- degraded durable mutation;
- draining;
- outage maintenance;
- lifecycle startup, closing, closed, shutdown or maintenance;
- unknown operation, lifecycle or outage state.

Every rejection prevents the setter call and returns the existing caller-visible failure value. The adapter does not create a success response, error message framework or silent fallback.

## Explicit exclusions

- broad economy or market gating;
- player-storage or generic Lua mutation gating;
- item, forge, house, guild or world mutation coverage beyond the shared bank-balance seam;
- draining, disconnect, removal, checkpoint or final-save orchestration;
- recovery probes, reconnect, ping, SQL retry/replay or resume;
- schema, migration, durable fencing, idempotency/ledger or deployment changes.

PRS-003D-C separately owns bounded draining and final-checkpoint orchestration after terminal D-B. Additional mutation domains require separately bounded ownership and evidence rather than expansion of this PR.
