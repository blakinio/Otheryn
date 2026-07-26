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
- target draft PR: `#128`.

## Validation contract

Focused tests cover:

- storage-backed Wheel accounting and clamp;
- representative costs for points 1, 2, 49 and 50;
- exact storage reservation;
- exact Shop response fields and statuses;
- wrong-offer, insufficient-balance, cap and rollback source boundaries;
- missing/truncated/trailing packet rejection;
- Bounty and Weekly non-regression;
- storage load before Wheel slot validation;
- no Wheel KV mirror;
- official Wheel payload reporting;
- Task Hunting and PlayerStorage SQL transaction ownership before separate KV staging.

Final acceptance additionally requires exact-head affected repository builds/tests and `Required`.

## Preserved exclusions

- no maintained-client Taskboard UI or assets;
- no Bounty, Weekly, Soulpit or other Task Shop offer;
- no Wheel balance constants, formulas, effects, spells, stances, areas or geometry;
- no legacy parser transfer;
- no schema migration, map, deployment or production action;
- no physical-client acceptance claim until separately exercised.
