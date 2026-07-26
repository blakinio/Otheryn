# OAM-051 Wheel safety adaptation

## Disposition

`wheel-of-destiny → ADAPT`

OAM-051A is limited to server-side safety and state-integrity corrections already reviewed in Canary PR #220. It preserves Otheryn architecture and does not claim current Tibia 15.25 parity.

## Included boundary

- atomic Wheel allocation proposal validation before mutation;
- server-side temple-only decrease enforcement;
- saturating spent/available point accounting and safe below-level formulas;
- validated modifier positions, grade arrays, gem indexes and active-gem state;
- revealed-gem capacity and failure-safe item/money ordering;
- persisted Wheel blob, grade and in-memory state reset/validation;
- permanent point-source load ordering before allocation validation;
- malformed current-protocol Wheel action rejection;
- deterministic focused tests and explicit source-boundary assertions.

## Excluded boundary

- Hunting Task Shop Promotion Points and its persistence/client contract;
- Wheel balance constants, formulas, areas and effect ordering;
- full Vessel Resonance damage/healing bonuses;
- Gift of Life mana, Ballistic Mastery, Healing Link, Battle Healing and Blessing changes;
- critical healing, stances, replacement spells and Strong Ice Wave geometry;
- legacy protocol parser changes in `src/game/game.cpp`;
- maintained-client, generated Lua API, map, schema and deployment changes.

## Immutable baselines

- Otheryn target: `ff90e93d872b6b47720f711483a9832203d5258d`;
- Canary governance: `a4a35495d4a8dc047bd3315b95c9fb577ac597af`;
- selected donor: Canary PR #220 squash `35ff51ac022e36d215db9d0fa86053b326a0bdf0`.

## Validation boundary

Final acceptance requires the focused OAM-051A test, repository formatting/generated checks, full affected CI and exact-final-head Required success. Static/source assertions prove the selected integration and exclusions but do not claim physical-client gameplay, DB failure injection, Task Shop transactions or full Wheel parity.
