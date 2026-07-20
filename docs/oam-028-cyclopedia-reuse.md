# OAM-028 Cyclopedia Umbrella Reuse

## Disposition

```text
cyclopedia REUSE
```

## Immutable task-start inputs

- legacy/governance Canary: `85b26b41510101259f6138f2c864bf0c4a473f2a`
- Otheryn target: `2a008f1c8cfa679c9b70281e4c8c16120a7567fa`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `cyclopedia` depends only on completed `protocol` and `player-persistence`. TSD-004 deliberately preserves it as a broad compatibility/discovery umbrella because navigation and request/response surfaces cross tabs, while narrow durable implementation roots remain separately owned by `bestiary`, `bosstiary`, `cyclopedia-character`, `titles`, `charms` and `houses`.

## Reuse evidence

Task-start Otheryn and fresh upstream share exact `src/server/network/protocol/protocolgame.hpp` blob `082d66596a424fc44143298c41fe01ff4007a439`. Task-start Otheryn, fresh upstream and legacy share exact `src/enums/player_cyclopedia.hpp` blob `45fed9ad2f3b7e35bdc7afd9dbd52d5d1b736311`. Identity is supporting evidence only, not the disposition by itself.

Delivered legacy Cyclopedia remediation was reviewed semantically:

- PR #188 fixes Bestiary arithmetic/null safety, Charm rules/registration, Bosstiary bootstrap and Cyclopedia Character recent-PvP pagination. TSD-004 assigns those production roots to `bestiary`, `charms`, `bosstiary` and `cyclopedia-character`; PR #188 explicitly changes no protocol or maintained OTClient path.
- PR #192 repairs Bestiary/Bosstiary monster data and validator allowlists; it explicitly changes no protocol or maintained OTClient path.
- PR #243 hardens the existing Cyclopedia validation gate and is validation/workflow control, not an umbrella runtime donor.

No reviewed delivered legacy change requires replacing the pinned target/upstream umbrella protocol surface. OAM-028 therefore keeps the clean target's existing OAM-006 protocol architecture and does not partially import child fixes before their own canonical OAM packages.

## Proof

The focused OAM-028 source-contract proof verifies that the existing `ProtocolGame` interface still exposes representative cross-tab Cyclopedia requests/responses for Character, Map, Bestiary, Bosstiary and Houses, and that each TSD-004 child implementation root exists independently in the clean target. This is a boundary/provenance proof, not a claim of packet-byte parity or child correctness.

## Explicit non-claims

OAM-028 does not claim Bestiary, Bosstiary, Charm, Cyclopedia Character, Titles or Houses child correctness; exact packet-byte compatibility; maintained-client parsing/rendering correctness; item/map/house presentation correctness; persistence completeness; runtime behavior; physical-client Cyclopedia E2E; or full Real Tibia parity. It changes no production runtime, protocol, data, schema, map, asset, deployment or maintained OTClient path.
