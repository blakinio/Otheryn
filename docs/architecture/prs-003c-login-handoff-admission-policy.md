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

## Live PRS-003C-B integration

The live adapter obtains exactly one immutable snapshot from `getDatabaseOutageSnapshot()` at each accepted protocol boundary and invokes only the existing pure policy:

- account login evaluates the live snapshot after the existing startup, shutdown and lifecycle-maintenance responses, but before IP-ban lookup, account load or authentication work;
- game login captures its snapshot before IP-ban lookup and game-world authentication, evaluates that same snapshot with the exact `GameLogin` operation and `GAME_STATE_NORMAL` to reject every non-healthy or unknown outage state before database work, then carries the immutable snapshot into the dispatcher;
- new-character game login performs only the existing minimal player preload needed to expose `PlayerFlags_t::CanAlwaysLogin`, then re-evaluates the same snapshot with the real lifecycle and capability before name-lock, account-ban, waiting-list, full player load or placement work;
- reconnect/session handoff evaluates a fresh live snapshot with the exact `ChannelHandoff` operation and the resolved player's existing `CanAlwaysLogin` capability before assigning the protocol player, removing channel membership, clearing modal state or replacing `player->client` ownership.

Lifecycle-specific caller responses remain the existing startup, shutdown, closing and closed behavior. Database-outage and fail-closed unknown rejections use the existing maintenance response rather than introducing a new protocol error framework. Account login and the pre-database game-login outage check supply no staff capability. The post-preload game-login decision and handoff supply only the already-present `CanAlwaysLogin` flag, which never bypasses a non-healthy outage snapshot.

The integration does not add a diagnostic route, reconnect, SQL retry or replay, draining/disconnect orchestration, deadline scheduling, schema work, deployment change or durable PRS-004 fencing.
