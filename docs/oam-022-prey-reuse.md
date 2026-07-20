# OAM-022 Prey target reuse proof

Canonical module: `prey`

Disposition: `REUSE`

Task-start target: `blakinio/Otheryn@b90e287a40413102c87e8c7fa3d5c01ad401cb6d`

Fresh upstream comparison: `opentibiabr/canary@71a0f92b4da3f550b292fa7536a0e35c2769f1ae`

Legacy evidence baseline: `blakinio/canary@800142e65c2975e57647bf34128ab468532218f0`

Maintained client: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

## Why REUSE

The reviewed Prey and classic Task Hunting core has no stronger independent legacy donor than the clean target/upstream implementation.

Exact source identity at the task-start baselines:

- `src/io/ioprey.cpp` blob `b0e335f5a4f7f9d8a3da75196dedf0d49242ef17` in target, fresh upstream and legacy Canary;
- `src/io/ioprey.hpp` blob `52b5ebf36037e2c9eee8b24741075e24b1680410` in target, fresh upstream and legacy Canary;
- `src/io/functions/iologindata_save_player.cpp` blob `5bb44a2f2e15c33b39a5b24206440057ded4ab5b` in target, fresh upstream and legacy Canary;
- the reviewed `loadPlayerPreyClass` and `loadPlayerTaskHuntingClass` implementations are functionally identical across the three baselines.

The maintained OTClient already contains `modules/game_prey/prey.lua` with the standard Prey action/options and UI event contract, so OAM-022 requires no client write or packet-layout change.

## Taskboard / Wheel boundary

Target and fresh upstream share the minimal official 15.25 Taskboard packet shim at blob `23ec7e00121695d4fb35941921a05478d7476cea`.

Legacy Canary differs at `data/modules/scripts/taskboard/taskboard.lua` because merged Wheel work added a Bonus Promotion Shop offer that consumes Hunting Task points but persists and applies purchased **Wheel of Destiny** promotion points under the `wheel-of-destiny` KV scope. That is an explicit Prey↔Wheel interaction, not a stronger independent Prey-core implementation.

OAM-022 therefore does not copy the Wheel-coupled Taskboard Shop implementation. The separately active Wheel parity program remains authoritative for that integration boundary.

## Target proof

This PR changes no production runtime, persistence, protocol, schema, data or client code. It adds only focused target tests that lock the existing deterministic Prey/Task Hunting data-model and wire-enum boundaries used by the maintained client.

## Explicit exclusions

OAM-022 does not claim:

- full modern official Hunting Task/Taskboard parity;
- Wheel Bonus Promotion Shop migration or Wheel allocation ownership;
- exhaustive Prey formula, rarity, reroll-price or monster-pool parity;
- physical-client Prey or Taskboard E2E closure;
- generic player-persistence or protocol redesign;
- maps, OTBM, `items.otb`, assets, schema or deployment changes.

These exclusions are deliberate boundaries and do not weaken the `REUSE` disposition for the reviewed classic Prey/Task Hunting core.
