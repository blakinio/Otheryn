# OAM-024 sanctions adaptation

## Disposition

```text
sanctions → ADAPT
```

## Immutable task-start baselines

- legacy / governance Canary: `3fe0130a408d201d0ca846f86a37b0ab20479932`
- Otheryn: `bcc3e9f7e3e704f3c012bda8693648d52741630f`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Canonical boundary

Canonical production ownership is limited to:

```text
src/creatures/players/management/ban.cpp
src/creatures/players/management/ban.hpp
```

The package depends only on the completed OAM-004 `database-connection` boundary. Protocol entry points, account authentication, generic security analytics, maintained-client code, PvP sanction rules and proof that every sanction is enforced at every possible entry point remain outside OAM-024.

## Evidence-driven classification

At task start, `ban.cpp` and `ban.hpp` were blob-identical across legacy, target and fresh upstream. That identity was not accepted as sufficient `REUSE` evidence.

Semantic review confirmed the intended narrow core:

- connection-attempt throttling is consumed by `ServicePort::onAccept`;
- IP-ban lookup is consumed by the login protocol;
- account-ban and namelock lookup are consumed by game login;
- active and permanent account bans remain read-only enforcement lookups;
- expired account bans are moved from `account_bans` to `account_ban_history`.

The reviewed target/upstream/legacy implementation performed the expired account-ban history `INSERT` and active-ban `DELETE` as two independent asynchronous database tasks. A process failure between those writes could leave duplicate/retry-prone history or stale active state, and the pair had no transaction rollback boundary. No stronger independent legacy donor for canonical `ban.*` was identified.

OAM-004 already delivered the target's bounded `DBTransaction` primitive, so the smallest valid disposition is `ADAPT`: reuse the existing sanctions behavior while moving only the expired account-ban handoff onto that existing transaction boundary.

## Target adaptation

`IOBan::isAccountBanned` now performs its account-ban read under `SELECT ... FOR UPDATE` inside one `DBTransaction`:

- no ban: commit and return not banned;
- active/permanent ban: populate `BanInfo`, commit and preserve existing enforcement behavior;
- expired ban: insert the history row and delete the active row in the same transaction;
- either write failure: rollback the pair and leave the active expired row available for a later retry.

Expired IP-ban cleanup is made synchronous so the lookup no longer queues an unobserved background delete. No schema, protocol, client, map, asset or deployment change is included.

## Focused proof

`SanctionsRepositoryDBTest` exercises the real test database and proves:

1. an active account ban remains enforced and is not archived;
2. an expired account ban moves to history exactly once, including a repeated lookup;
3. a forced database `DELETE` failure rolls back the preceding history `INSERT`, after which a retry succeeds once the failure trigger is removed.

The final target merge gate must use the exact final PR head and include changed-file, CI, review/comment/thread and target-main drift audits before expected-head squash merge.

## Explicit non-claims

OAM-024 does not claim exhaustive sanction enforcement across every entry point, generic authentication security, protocol compatibility, distributed/multi-database sanctions replication, moderation policy, security analytics, AI investigation, PvP skull/frag parity, physical-client sanctions E2E closure, generic persistence redesign, or changes to maintained OTClient, maps, OTBM, `items.otb`, assets, schema or deployment.
