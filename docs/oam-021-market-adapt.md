# OAM-021 Market target adaptation proof

Canonical module: `market`

Disposition: `ADAPT`

Task-start target: `blakinio/Otheryn@d59207d05ab6dd9450b05d0a6b4d9122fda60489`

Fresh upstream comparison: `opentibiabr/canary@71a0f92b4da3f550b292fa7536a0e35c2769f1ae`

Legacy evidence baseline: `blakinio/canary@183d7224cb5de57585294d72631f37783b93dc89`

Maintained client: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Why ADAPT

The task-start Otheryn and fresh upstream market core are content-identical for `src/io/iomarket.cpp` and the reviewed market section of `src/game/game.cpp`. Whole-module legacy `REUSE` is rejected because current legacy differences are coupled to the separately owned multichannel runtime: selected expiry/cancel paths use `EconomicLedgerStore` and market expiry is leader-gated. Those additions are incomplete as a generic exactly-once market design and must not be imported as hidden cluster architecture.

Open Canary security evidence also records a proven concurrent partial-fill race for a multiwriter market and a stale remote-player save hazard in the multichannel legacy deployment. Otheryn does not currently adopt that multichannel ownership model. Its game actions and asynchronous database callbacks return to the single dispatcher before gameplay callbacks execute, so the legacy cross-process proof is not promoted into a claim that the current clean target already has an equivalent multiwriter runtime.

The retained upstream-based market still has unresolved crash/restart atomicity boundaries between durable offer/history mutation and in-memory or persisted item/balance effects. This package does not claim to solve those generic recovery problems. They remain explicit known gaps and block an unconditional `REUSE` disposition.

## Bounded target adaptation

OAM-021 adds one small server-side validation helper and wires it into `IOMarket`:

- deterministic 16-bit offer-counter derivation is centralized instead of repeated;
- client timestamps that would underflow the configured offer-duration window fail closed before SQL lookup;
- market tier values are parsed strictly with `std::from_chars` and rejected when malformed, above `uint8_t`, or above the configured Forge tier ceiling, avoiding the previous parse-then-truncate behavior.

The maintained OTClient wire contract is unchanged. At the pinned client SHA it sends market create as `(type, itemId, optional tier, amount, price, anonymous)`, cancel as `(timestamp, counter)`, and accept as `(timestamp, counter, amount)` and already parses the existing MarketEnter/Detail/Browse responses. No client write is required.

## Explicit exclusions and known gaps

This package does not import generic multichannel leader election, Redis/session ownership, `economic_ledger`, schema changes, market operation recovery tables, generic bank/account transaction redesign, NPC shops, store products, direct player trade, maps, OTBM, `items.otb`, assets or deployment changes.

It does not claim crash-safe exactly-once create/cancel/accept/expiry, cross-process market safety, atomic SQL/KV/player-state composition, remote-player ownership routing, exhaustive Real Tibia market parity or physical-client Market E2E closure. Future introduction of multiwriter/multichannel market execution requires a separate atomic claim/recovery contract rather than relying on this package.

## Focused proof

`Oam021MarketAdaptTest` covers the accepted deterministic server-side boundary:

- offer-counter identity;
- timestamp-window underflow/negative-duration rejection;
- strict tier parsing and configured/range rejection.

Full target CI remains authoritative for integration/build/runtime compatibility.
