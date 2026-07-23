# OAM-038 World Zones reuse proof

## Disposition

`world-zones → REUSE`

## Immutable baselines

- Otheryn target task-start main: `651ff1c6261eb25bd0992d7530e50e3690c2b5de`
- Canary OAM-038 preflight merge: `615648ae0b17c18ee58c3f118b38f78607316a2d`
- canonical target/upstream `src/game/zones/zone.cpp` blob: `f80af238eb2b4b10193a9b5961652591d9dafeb5`
- canonical target/upstream `src/game/zones/zone.hpp` blob: `d413dccc690d37dc1a24af6c5d2e630b14b087d1`

Canonical `world-zones` owns the zone registry by name, id and position, static and dynamic zone lifecycle, area and position indexing, creature/player/monster/NPC/item membership caches, remove destinations and bulk removal, refresh, monster-variant metadata and XML zone loading. Tile protection/PvP flag semantics, quest/event scripting inside zones, instance region allocation, generic map runtime, protocol/client, physical-client orchestration, map content, assets, schema and deployment remain outside this boundary.

## Reuse decision

Task-start Otheryn already contains the same canonical `zone.cpp` and `zone.hpp` roots as the reviewed fresh upstream baseline. The older legacy Canary donor is not stronger as a whole-module source because the target retains mutex protection around weak membership-cache reads, writes, removals and refresh, plus safer typed weak-pointer erasure behavior.

Identity alone is not the proof. The bounded source-contract regression below verifies the owned registry, indexing, synchronized cache and cleanup surfaces. No production runtime or data path is changed.

The smallest valid target package is therefore `REUSE`: preserve production code unchanged and add one focused source-contract proof registered in the unit-test build.

## Proof boundary

The OAM-038 regression test verifies that the target retains:

- zone registration by name and id, including linking pre-existing static ids and rejecting the reserved `default` name;
- area addition/subtraction and position index/unindex lifecycle, including removal of empty position-index entries;
- lookup by position and global zone enumeration;
- mutex-protected weak membership-cache reads and mutations for creatures, players, monsters, NPCs and items;
- typed weak-pointer removal and synchronized cache reset during refresh;
- dynamic-zone cleanup while preserving map-loaded static zones;
- remove-destination fallback and bulk player/monster/NPC removal surfaces;
- monster-variant propagation and monster cleanup;
- XML zone loading with shifted zone ids.

## Nonclaims

OAM-038 does not claim exhaustive zone membership or eviction correctness under every movement/reload/concurrency schedule, tile protection/PvP flag correctness, quest/event behavior inside zones, instance isolation, exact monster-variant gameplay semantics, map-content parity, persistence guarantees, protocol/client compatibility, physical-client E2E closure or full Real Tibia parity.
