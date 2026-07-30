# PRS-003D-A mutation outage admission policy

## Disposition

`PRS-003 Slice D-A -> PURE POLICY IMPLEMENTED`

This package defines one deterministic mutation admission decision only. It does not read global outage state and does not change live gameplay, economy, checkpoint, player-removal or draining behavior.

## Contract

`DatabaseOutageMutationAdmissionPolicy::evaluate()` receives an immutable `DatabaseOutageSnapshot`, one explicit mutation operation class and the current `GameState_t`. It returns allow or reject, a fixed low-cardinality reason and the evaluated input classes for a later runtime adapter. It contains no caller-visible message.

The accepted operation classes are:

- `CriticalDurable`: critical transactional or economy state whose durable acknowledgement cannot be trusted during an outage;
- `OrdinaryDurable`: ordinary persistence-relevant player or world mutation that must remain checkpointable;
- `EphemeralNonDurable`: explicitly proven non-durable runtime state that may be reconstructed or lost;
- every unrecognized enum value is an unknown operation and rejects fail closed.

Classification is explicit at the future call site. The policy does not infer durability from a function name, object type, player capability or previous success.

## Outage table

Assuming lifecycle `GAME_STATE_NORMAL`:

| Operation | Healthy | Degraded | Draining | Maintenance |
|---|---|---|---|---|
| critical durable mutation | allow | reject: `OutageDegradedDurableMutation` | reject: `OutageDraining` | reject: `OutageMaintenance` |
| ordinary durable mutation | allow | reject: `OutageDegradedDurableMutation` | reject: `OutageDraining` | reject: `OutageMaintenance` |
| ephemeral/non-durable mutation | allow | allow during the finite grace | reject: `OutageDraining` | reject: `OutageMaintenance` |

The degraded allowance applies only to operations already classified as ephemeral/non-durable by an explicit future adapter. Unknown or merely unclassified gameplay is not ephemeral and remains fail closed.

## Lifecycle table

Assuming outage `Healthy`:

| Lifecycle | Critical durable | Ordinary durable | Ephemeral/non-durable |
|---|---|---|---|
| `STARTUP` | reject | reject | reject |
| `INIT` | allow | allow | allow |
| `NORMAL` | allow | allow | allow |
| `CLOSING` | reject | reject | reject |
| `CLOSED` | reject | reject | reject |
| `SHUTDOWN` | reject | reject | reject |
| `MAINTAIN` | reject | reject | reject |

Lifecycle restrictions are evaluated before outage admission. PRS-002 final checkpoints are a separate operation boundary and are not classified as gameplay mutations by this policy.

Unknown operation, lifecycle and outage values reject fail closed with dedicated reason codes.

## Pure-policy boundary

- supplied snapshots are read-only;
- identical inputs produce identical decisions;
- no clock, global state, database, gameplay object, player, scheduler or checkpoint owner is queried;
- no reconnect, ping, query, replay, retry, wait, disconnect, removal, save or mutation occurs;
- the policy is header-only, `constexpr` and `noexcept`;
- the decision carries only fixed enum values and evaluated inputs.

## Deferred PRS-003D work

PRS-003D-B must separately inventory exact live mutation entry points, declare exact non-overlapping ownership and insert runtime gates before unsafe side effects or acknowledgement. It must not infer `EphemeralNonDurable` by default.

PRS-003D-C must separately orchestrate bounded draining through the existing PRS-002 final-player-save boundary with a finite deadline, finite attempt budget, explicit timeout/failure results and unconditional transition to maintenance when the bound expires.

Telemetry or additional deterministic failure evidence belongs to PRS-003D-D only when required by the accepted runtime integration.

This package adds no recovery probe or resume behavior; those remain PRS-003E. It adds no durable fencing, idempotency/ledger, schema, migration or deployment work.
