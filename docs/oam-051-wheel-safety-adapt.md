# OAM-051 Wheel safety and Task Shop adaptation

## Disposition

`wheel-of-destiny → ADAPT`

OAM-051 is complete as two bounded server-side packages selected through Canary governance:

- OAM-051A integrates Wheel safety and state-integrity corrections;
- OAM-051B integrates only the Hunting Task Shop Bonus Promotion points contract.

Together they preserve Otheryn architecture and maintained current-protocol shapes without claiming complete Tibia 15.25 Wheel or Taskboard parity.

## Delivered boundary

### OAM-051A — Wheel safety

- parse and validate the complete Wheel allocation before committing slot or active-gem state;
- reject point decreases outside an eligible temple;
- saturate invalid spent-point state instead of allowing unsigned underflow;
- validate modifier positions, grade values, gem indexes, affinity and stale active-gem state;
- enforce the revealed-gem cap and restore reserved gems/fragments if a later money mutation fails;
- clear and validate in-memory/KV/DB Wheel state during load;
- load permanent point sources before validating the persisted allocation;
- reject truncated or invalid current-protocol Wheel gem actions without changing opcodes or payload layouts.

### OAM-051B — Bonus Promotion points

- reserve SQL-backed PlayerStorage key `1000006` as `wheel.hunting_task_shop_points`;
- expose exactly one Shop offer, id `0`, type `4`, bounded to `0..50` purchased points;
- preserve the accepted cost progression, display offset and statuses `0`, `2` and `4`;
- reject malformed, trailing and wrong-offer Shop Buy packets before mutation;
- persist the Hunting Task balance and purchased count through the same player SQL transaction;
- keep Wheel KV outside the purchase contract;
- include the clamped purchased count in Wheel extra-point accounting and the official Wheel Task Shop points field;
- preserve empty Bounty and Weekly response shims.

## Target-specific integration

The OAM-051A donor was pinned to Canary PR #220 squash `35ff51ac022e36d215db9d0fa86053b326a0bdf0`. Ordinary Wheel files accepted the selected safety hunks directly. `player_wheel.cpp` required semantic rebasing because the target had drifted from the donor parent.

OAM-051B was selected by Canary preflight PR #959 merge `9e865b68b9197b28450002412ca1720683cf1f64`. The maintained OTClient baseline `ce4329ee13b39576915240605c2fe6657096c517` confirmed the bounded Shop and Wheel field shapes. Target persistence analysis selected PlayerStorage instead of Wheel KV so the purchased count and Hunting Task balance remain in the same SQL transaction.

No whole legacy file was copied. Temporary materialization and branch-synchronization helpers were removed before each package's final validation.

## Preserved exclusions

- maintained-client Taskboard UI and assets;
- Bounty, Weekly, Soulpit and other Task Shop offers;
- Wheel balance constants, formulas, areas and effect ordering;
- full Vessel Resonance damage/healing bonuses;
- Gift of Life mana, Ballistic Mastery, Healing Link, Battle Healing and Blessing changes;
- critical healing, stances, replacement spells and Strong Ice Wave geometry;
- legacy protocol parser changes in `src/game/game.cpp`;
- generated Lua API, map, schema and deployment changes.

The existing Supreme Grade II value of `12000000` remains unchanged. No `WheelBalance` dependency or full-resonance bonus helper was imported.

## Immutable baselines and merges

### OAM-051A

- task-start target: `ff90e93d872b6b47720f711483a9832203d5258d`;
- Canary governance: `a4a35495d4a8dc047bd3315b95c9fb577ac597af`;
- selected donor: `35ff51ac022e36d215db9d0fa86053b326a0bdf0`;
- exact final feature head: `1f4ce3c11f6acf292775daac886e9dace7e8280f`;
- target PR `#115`, squash merge `47863ce250bce73c1b9af3077f82e9bf6e99e3d1`.

### OAM-051B

- Canary preflight: `9e865b68b9197b28450002412ca1720683cf1f64`;
- maintained OTClient baseline: `ce4329ee13b39576915240605c2fe6657096c517`;
- exact final feature head: `a507abc5d6b9aa3158f9b009a715d5aee0b4c43c`;
- target PR `#128`, squash merge `546eac0a00ec620e7293d0548e30662024464084`.

## Final validation evidence

### OAM-051A

- `autofix.ci` run `30193154587`: pass;
- full CI run `30193154684`: pass;
- Required run `30193154608`: pass;
- final discussion and target-main drift audits: clean.

### OAM-051B

- Repository Audit run `30206237389`: pass;
- `autofix.ci` run `30206237391`: pass;
- full CI run `30206237518`: pass;
- Required run `30206237406`: pass;
- Linux debug full C++ tests, schema import and Canary smoke: pass;
- Linux release Canary and Global smoke: pass;
- macOS, both Windows variants and Docker validation: pass;
- final discussion audit: clean;
- exact seven-path audit and `behind_by: 0` target-main comparison: pass before expected-head merge.

Static/source assertions and full repository gates prove the selected integrations and exclusions. They do not claim physical maintained-client Taskboard acceptance or deferred Wheel/Taskboard parity behavior.
