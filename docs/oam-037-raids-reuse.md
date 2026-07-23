# OAM-037 Raids reuse proof

## Disposition

`raids → REUSE`

## Immutable baselines

- Otheryn target task-start main: `3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e`
- Canary OAM-037 preflight merge: `8bdeb2747356727df80a3b95073aa29a4dca7818`
- Canary bounded target-proof plan merge: `817da293a141880f7090194699a4ac38e567a2fb`
- canonical target/upstream `src/lua/creature/raids.cpp` blob: `d46a549a341e0872474bd723b10d1208fa22da8c`
- canonical target/upstream `src/lua/creature/raids.hpp` blob: `777558e3e199816bb596636fc7487c38c29224ee`

Canonical `raids` owns legacy raid registry loading, interval/margin/repeat metadata, periodic raid selection, single-running-raid state, ordered raid-event execution, lifecycle reset/cleanup, and announce/single-spawn/area-spawn/script event dispatch. Boss encounter reward lifecycle, generic creature AI and definitions, static/dynamic spawn scheduling outside raids, Bosstiary, quest access/cooldowns, protocol/client, map, assets, schema and deployment remain outside this boundary.

## Reuse decision

Task-start Otheryn already contains the same canonical `raids.cpp` and `raids.hpp` roots as the reviewed fresh upstream baseline. The older legacy Canary donor is not stronger as a whole-module source because the target retains maintenance-lane dispatcher scheduling and explicit scheduling-failure safeguards for periodic checks and raid-event execution.

Identity alone is not the proof. The bounded source-contract regression below verifies the owned registry, scheduler and event lifecycle surfaces. No production runtime or data path is changed.

The smallest valid target package is therefore `REUSE`: preserve production code unchanged and add one focused source-contract proof registered in the unit-test build.

## Proof boundary

The OAM-037 regression test verifies that the target retains:

- legacy-raid registry loading and reload lifecycle, including `interval2`, `margin` and `repeat` metadata handling;
- periodic raid selection and single-running-raid state;
- non-repeat raid removal after selection;
- `DispatcherLane::Maintenance` scheduling for periodic checks and raid events;
- explicit failure handling when initial, subsequent or periodic scheduling cannot be created;
- ordered event progression and reset to idle state after completion or failure;
- event-stop and full registry cleanup behavior;
- canonical announce, single-spawn, area-spawn and script raid-event dispatch surfaces.

## Nonclaims

OAM-037 does not claim exact official raid probability or timing parity, exact event timing under scheduler load, raid XML/data-definition completeness, restart/crash recovery semantics, distributed or multichannel raid coordination, exact spawn placement parity, webhook delivery guarantees, physical-client E2E closure or full Real Tibia parity.
