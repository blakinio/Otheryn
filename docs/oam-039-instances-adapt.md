# OAM-039 Instances target adaptation

## Final candidate disposition

`instances → ADAPT`

## Immutable baselines

- Otheryn target task-start main: `a275f1d788b50164ffc79b6f6143e13b9150c82e`
- Canary OAM-039 preflight merge: `5c0613fd853e85421a89f661e9b3774c4dd730ff`
- fresh upstream Canary baseline: `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- maintained OTClient baseline: `1e5305395159142634f182d9e888e5f9164228c6`

Clean Otheryn and fresh upstream did not contain the canonical `InstanceManager` roots, so OAM-039 cannot be `REUSE`. The behavioral donor is legacy Canary's staged `src/game/instance/**` subsystem.

## Canonical ownership

OAM-039 owns only the instance subsystem itself:

- strong instance and slot identifiers;
- configured non-overlapping map-region pool and reservation/reuse;
- `Creating → Active → Closing → Destroyed` lifecycle;
- exactly-once cleanup and fail-closed quarantine of dirty regions;
- stable runtime creature-id ownership and fail-closed instance relations;
- summon ownership inheritance and compensating binder transactions;
- lazy instance-scoped event liveness;
- bounded `InstanceArenaService` consumer.

Cross-module `Game` ownership, `Creature::setMaster`, ordinary spawn/NPC instance-scoping, spectator/target/combat filtering, scheduler-wide task ownership, generic Lua/admin UI, physical-client orchestration, map content and persistence are interaction boundaries and are not migrated by this package.

## Target adaptations

The donor was not copied wholesale.

1. Canonical `src/game/instance/**` is introduced as constructor-owned components with no new global singleton.
2. Unit coverage is introduced directly in `tests/unit/game/instance/**` and registered in the existing target test build.
3. The production source build registers only the three instance translation units.
4. `InstanceArenaService::configuredRegions()` intentionally returns an empty region list in clean Otheryn. The donor's hard-coded `data-canary` coordinates are map-owned evidence and cannot be imported into the clean target without an explicit target-map proof. The consumer remains available against an explicitly configured `InstanceManager`, while default target behavior is fail-closed.
5. No `Game`, `Creature`, Lua, talkaction, protocol or client integration is added in OAM-039.

## Validation boundary

The target unit tests cover:

- region validation, 3D overlap rules, deterministic reservation/release/reuse and concurrent unique reservations;
- instance creation, activation, idempotent close, region reuse, cleanup quarantine and timeout sweeping;
- stable creature ownership, cross-instance rejection, fail-closed relations and summon inheritance;
- runtime-id binder bind/unbind, relation checks and rollback of newly inherited ownership when a master mutation fails;
- instance-scoped callbacks executing only while the instance remains Active, including fail-closed behavior during Closing cleanup;
- clean-target arena default configuration rejecting creation with zero regions, while the bounded consumer operates correctly when an explicit target region is supplied.

## Nonclaims

OAM-039 does not claim runtime activation through `Game`, ordinary spawn/NPC ownership, full spectator/target/combat isolation, logout/death/reconnect handling, generic scheduler cancellation, production target-map arena coordinates, admin Lua/talkaction reachability, complete cleanup/recovery, two-parallel-instance physical E2E, persistence semantics, multiworld/multichannel support or full Real Tibia instance parity.
