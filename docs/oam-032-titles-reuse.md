# OAM-032 Titles reuse proof

## Disposition

`titles → REUSE`

## Immutable baselines

- Otheryn target: `ad2bd2f187df057c47d05c121351159ce30cc457`
- Canary legacy/governance: `db7cf6af480285ad4a87c3be2981a873f175eab6`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

Canonical `titles` owns the narrow server root `src/creatures/players/components/player_title.*` and depends only on completed `cyclopedia-character` and `player-persistence`. Bestiary, Bosstiary, character progression, houses and protocol are interactions; appearance lifecycles and maintained-client rendering remain outside this package.

## Reuse decision

Task-start target, legacy and fresh upstream share exact `player_title.cpp` blob `c885d5ee55970d8ce93a80bb477bc317fb9faa98` and exact `player_title.hpp` blob `118806fee9ca6d939d73067af14c63c59d291f25`. Blob identity is supporting evidence only.

TSD-004 establishes Titles as an independent definition, unlock, current-selection and KV-persistence lifecycle rooted in `player_title.*`. The reviewed Cyclopedia runtime remediation PR #188 contains Bestiary, Bosstiary, Charm and Cyclopedia Character corrections but no Titles path; PR #192 is Bestiary/Bosstiary monster-data remediation; PR #243 is validator/workflow control. The final Cyclopedia audit reached zero scanner findings, but that result is not treated as proof of title thresholds, permanence, persistence, protocol, runtime behavior or maintained-client correctness.

No accepted legacy donor delta was found inside the canonical Titles root, and current open PR ownership does not overlap `player_title.*` or the OAM-032 proof paths. The smallest valid disposition is therefore `REUSE`: preserve the clean target implementation and add focused proof only, with no production, protocol, data, schema, map, asset, deployment or maintained-OTClient mutation.

Focused proof guards the independent `PlayerTitle` lifecycle surface, current-title unlock gate, and the scoped KV contracts for current and unlocked titles.

## Nonclaims

OAM-032 does not claim title-definition or unlock-threshold parity, completeness of every cross-domain eligibility check, map/Drome/Goshnar or other TODO-backed title conditions, persistence atomicity or crash recovery, exact protocol compatibility, maintained-client parsing/rendering correctness, physical-client Titles E2E closure, or full Real Tibia parity.
