# OAM-051B Hunting Task Shop adaptation

## Disposition

`wheel-of-destiny / hunting-task-shop → ADAPT`

This package implements only the Hunting Task Shop Bonus Promotion points authorized by Canary OAM-051B preflight PR #959. OAM-051A remains the completed Wheel safety foundation. No broader Taskboard or Wheel parity claim is introduced.

## Delivered boundary

- reserve SQL-backed PlayerStorage key `1000006` as `wheel.hunting_task_shop_points`;
- expose one Task Shop offer, id `0` and type `4`;
- support purchased points `0..50` and next-point display values `1..51`;
- calculate next-point cost as `100 * (1 + n * (n - 1) / 2)`;
- emit maintained-client statuses `0` available, `2` insufficient points and `4` bought/capped;
- reject missing, truncated, trailing and wrong-offer Shop Buy requests without mutation;
- mutate storage before debiting Hunting Task Points and restore storage if the debit unexpectedly fails;
- persist both mutations through the existing player SQL transaction;
- keep Wheel KV outside the purchase contract;
- clamp storage-derived Wheel points to `0..50` and include them in `PlayerWheel::getExtraPoints()`;
- report the purchased count in the official Wheel payload field consumed by `GameTaskboard` clients;
- preserve the existing empty Bounty and Weekly response shims.

## Transaction model

The purchase count uses PlayerStorage rather than Wheel KV. Existing Otheryn persistence already saves Task Hunting state and PlayerStorage inside `DBTransaction::executeWithinTransaction(savePlayerGuard)`. Wheel KV is staged only after that SQL transaction commits.

Consequences:

- validation completes before mutation;
- an in-process debit failure restores the prior purchased count;
- an SQL save failure rolls back both Task Hunting balance and PlayerStorage;
- a successful SQL commit persists both;
- replayed requests recalculate the current point, cost and cap;
- no separate KV write can survive an SQL rollback.

## Protocol contract

Taskboard Shop response:

```text
0x5B
U8 subtype = 0x02
U8 offer_count = 1
U8 offer_type = 0x04
U16 display_value = purchased_points + 1
U32 next_cost
U8 status
```

Shop Buy request:

```text
0x5F
U8 action = 0x0B
U16 offer_id = 0
no trailing bytes
```

For official Wheel payloads, the existing Monk quest flag remains a byte and the following `U16` now carries the clamped Hunting Task Shop purchased count, matching maintained OTClient parsing.

## Immutable evidence

- Canary OAM-051B preflight merge: `9e865b68b9197b28450002412ca1720683cf1f64`;
- Otheryn task base: `38bb62192d25984d63f96c2637348b4adc82f6cd`;
- maintained OTClient baseline: `ce4329ee13b39576915240605c2fe6657096c517`;
- exact final feature head: `a507abc5d6b9aa3158f9b009a715d5aee0b4c43c`;
- target PR: `#128`;
- target squash merge: `546eac0a00ec620e7293d0548e30662024464084`.

## Final validation evidence

- exact source-path and exclusion audit: pass for seven declared paths;
- temporary workflow and helper removal audit: pass;
- Repository Audit run `30206237389`: pass on exact head `a507abc5d6b9aa3158f9b009a715d5aee0b4c43c`;
- `autofix.ci` run `30206237391`: pass without moving the final head;
- full CI run `30206237518`: pass on the same exact head;
- Fast Checks and Lua Tests: pass;
- Linux debug: compile, Canary runtime smoke, schema import and all C++ tests pass;
- Linux release: compile plus Canary and Global runtime smoke pass;
- macOS compile and runtime smoke: pass;
- Windows CMake compile/runtime smoke and Windows Solution build: pass;
- Docker image build/export/validation: pass;
- Required run `30206237406`: pass on the same exact head;
- final comments, reviews and review-thread audit: clean;
- target-main comparison: `behind_by: 0` before expected-head squash merge.

## Preserved exclusions

- no maintained-client Taskboard UI or assets;
- no Bounty, Weekly, Soulpit or other Task Shop offer;
- no Wheel balance constants, formulas, effects, spells, stances, areas or geometry;
- no legacy parser transfer;
- no schema migration, map, deployment or production action;
- no physical-client acceptance claim until separately exercised.

Static/source assertions and the full repository gates prove the bounded server integration and exclusions. The maintained client has no complete shipped Taskboard UI, so physical-client acceptance remains a separate evidence boundary.
