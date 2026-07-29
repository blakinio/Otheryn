# PRS-003C-A login and handoff outage admission policy

## Disposition

`PRS-003 Slice C-A -> PURE POLICY IMPLEMENTED`

This package defines a deterministic admission decision only. It does not read global outage state and does not change live account login, game login or protocol-session handoff behavior.

## Contract

`DatabaseOutageAdmissionPolicy::evaluate()` receives an immutable `DatabaseOutageSnapshot`, an explicit operation, narrow caller capabilities and one `GameState_t`. It returns allow or reject, a fixed reason code and the evaluated input classes for a later adapter. It contains no caller-visible message.

## Outage table

Assuming `GAME_STATE_NORMAL`:

| Operation | Healthy | Degraded | Draining | Maintenance |
|---|---|---|---|---|
| account login | allow | reject | reject | reject |
| game login | allow | reject | reject | reject |
| protocol-session or channel handoff | allow | reject | reject | reject |
| explicit staff diagnostic operation with diagnostic capability | allow | reject | reject | allow |

The rejection reasons are fixed as `OutageDegraded`, `OutageDraining` and `OutageMaintenance`. A valid handoff hint, an already authenticated player or `canAlwaysLogin` does not bypass an outage state.

## Lifecycle table

Assuming outage `Healthy`:

| Lifecycle | Account login | Game login | Handoff | Staff diagnostic |
|---|---|---|---|---|
| `STARTUP` | reject | reject | reject | reject |
| `INIT` | allow | allow | allow | allow with capability |
| `NORMAL` | allow | allow | allow | allow with capability |
| `CLOSED` | allow | allow only with `canAlwaysLogin` | allow only with `canAlwaysLogin` | allow with capability |
| `SHUTDOWN` | reject | reject | reject | reject |
| `CLOSING` | allow | allow only with `canAlwaysLogin` | allow only with `canAlwaysLogin` | allow with capability |
| `MAINTAIN` | reject | reject | reject | allow with capability |

Unknown operation, lifecycle and outage values reject fail closed with dedicated reason codes.

## Staff assumptions

Current source behavior uses `PlayerFlags_t::CanAlwaysLogin` only for game login during `CLOSING` and `CLOSED`. The configured gamemaster, community-manager and god groups carry that flag, but it is not a lifecycle-maintenance or database-outage bypass. Diagnostic admission is therefore a separate operation requiring a separate capability; adding that capability to ordinary login or handoff does nothing.

## Pure-policy boundary

- supplied snapshots are read-only;
- identical inputs produce identical decisions;
- no clock, global state, database, protocol, session, player or channel object is queried;
- no reconnect, query, replay, retry, wait, disconnect or mutation occurs;
- handoff remains independently classified even where its lifecycle result matches game login.

## Later integration

A later PRS-003C package must obtain the immutable snapshot from the accepted owner, classify the exact entry point, map fixed reasons to existing protocol responses and prove gate placement before database-backed admission work or handoff ownership mutation. It must preserve shutdown ordering and must not invent a generic staff bypass.

This package does not settle snapshot ownership, caller-visible wording, the exact adapter insertion points or PRS-004 handoff fencing.
