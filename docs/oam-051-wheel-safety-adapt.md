# OAM-051 Wheel safety adaptation

## Disposition

`wheel-of-destiny → ADAPT`

OAM-051A is limited to server-side safety and state-integrity corrections selected by Canary OAM-051 preflight and reviewed in Canary PR #220. It preserves Otheryn architecture and does not claim current Tibia 15.25 parity.

## Delivered boundary

- parse and validate the complete Wheel allocation before committing slot or active-gem state;
- reject point decreases outside an eligible temple;
- saturate invalid spent-point state instead of allowing unsigned underflow;
- validate modifier positions, grade values, gem indexes, affinity and stale active-gem state;
- enforce the revealed-gem cap and restore reserved gems/fragments if a later money mutation fails;
- clear and validate in-memory/KV/DB Wheel state during load;
- load permanent point sources before validating the persisted allocation;
- reject truncated or invalid current-protocol Wheel gem actions without changing opcodes or payload layouts;
- add deterministic behavior and source-boundary tests.

## Target-specific integration

The donor was pinned to Canary PR #220 squash `35ff51ac022e36d215db9d0fa86053b326a0bdf0`. Ordinary Wheel files accepted the selected safety hunks directly. `player_wheel.cpp` required semantic rebasing because the target had drifted from the donor parent.

The initial three-way application failed only on `player_wheel.cpp`. Selective application accepted 23 of 25 hunks. The remaining lifecycle hunk was adapted against current Otheryn to remove destroyed gems from KV, clear stale active copies by UUID, persist rotated affinity and reload bonuses. The other rejected donor hunk required no target change because current Otheryn already returned on an invalid active-gem index without clearing existing state.

Temporary materialization workflow and helper files were removed before review. The final PR contains only eight implementation/test paths plus this report and the task checkpoint.

## Preserved exclusions

- Hunting Task Shop Promotion Points and its persistence/client contract;
- Wheel balance constants, formulas, areas and effect ordering;
- full Vessel Resonance damage/healing bonuses;
- Gift of Life mana, Ballistic Mastery, Healing Link, Battle Healing and Blessing changes;
- critical healing, stances, replacement spells and Strong Ice Wave geometry;
- legacy protocol parser changes in `src/game/game.cpp`;
- maintained-client, generated Lua API, map, schema and deployment changes.

The existing Supreme Grade II value of `12000000` remains unchanged. No `WheelBalance` dependency or full-resonance bonus helper was imported.

## Immutable baselines

- Otheryn target: `ff90e93d872b6b47720f711483a9832203d5258d`;
- Canary governance: `a4a35495d4a8dc047bd3315b95c9fb577ac597af`;
- selected donor: `35ff51ac022e36d215db9d0fa86053b326a0bdf0`;
- target PR: `#115`.

## Validation evidence

- exact source-path and exclusion audit: pass;
- materializer exact-scope audit: pass for the eight approved implementation/test paths;
- temporary-helper removal audit: pass;
- draft-head lightweight CI and Required on `6fe767137b22e055df17c9024881b84577bd9f17`: pass, but build/test jobs were skipped because the PR remained draft;
- full exact-final-head affected CI: pending.

Static/source assertions prove the selected integration and exclusions. They do not claim physical-client gameplay, DB failure injection, Task Shop transaction durability or full Wheel parity.
