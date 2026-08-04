# Dossier — `zimbadev/crystalserver#852`

## Identity

```yaml
canonical_key: zimbadev/crystalserver#852
predecessor_row: 95
source_type: issue
prior_bucket: REPRO
prior_truth_status: PARTIALLY_PROVEN
family: live-map-swap-client-state
research_status: COMPLETE
```

## Source claim

- Current title: `Game.loadMap fails to reload .otbm correctly, causing client crash`
- Source URL: `https://github.com/zimbadev/crystalserver/issues/852`
- Exact claim: a live map swap over an area occupied by a player leaves the map/client state inconsistent, and moving after the Cults of Tibia Misguided swap crashes the client.
- Claimed affected version/protocol: CrystalServer main immediately before 2026-08-03; client version is not stated.
- Claimed reproduction: GOD at `(32562, 32377, 10)`, equip item `25297`, use it on Misguided Bully/Thief, then move after the map swap.
- Claimed expected behavior: the illusion/reality OTBM replacement becomes authoritative for occupied tiles and the connected client can continue moving without a crash.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue | `zimbadev/crystalserver` | Issue `#852`, open | 2026-08-04 | exact coordinate, item, creature and post-swap movement sequence | primary claim | no crash dump, packet capture or run artifact; client version omitted |
| S2 | repository code | all four server repositories | pinned audit revisions | 2026-08-04 | Misguided action removes map items and calls `Game.loadMap` for illusion/reality while the player may remain in the replaced area | primary static evidence | identical script does not prove the runtime failure |
| S3 | repository code | `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | 2026-08-04 | `Map::loadMap` calls `load`/`IOMap::loadMap`; map cache retains basic tiles and materializes replacements lazily | target implementation evidence | static review alone does not prove stale client state or retained-memory growth |
| S4 | related donor PR | `zimbadev/crystalserver#785` | head `54fd1ddaf7f78bbc9a34297e6f391664d5645746` | 2026-08-04 | proposes explicit area/cache clearing before map replacement and describes Ebb and Flow retention | corroborating hypothesis | author says the fix is not 100% and testing is ongoing |
| S5 | maintained client code | `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | 2026-08-04 | maintained client consumes server map/tile/movement packet streams | comparison boundary | no source-side proof that its behavior matches the unnamed client from the Issue |

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: after a live OTBM replacement, server tile/cache state and every connected client's known map state must describe one coherent map before subsequent movement is processed
version_boundary: applies to scripts that invoke Game.loadMap over occupied coordinates; exact client/protocol susceptibility is unknown
evidence_basis:
  - S1
  - S2
  - S3
conflicts:
  - the Issue attributes failure to incomplete OTBM loading, while PR 785 emphasizes stale tile/cache retention; neither includes a packet trace proving the immediate client-crash mechanism
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | `data-otservbr-global/scripts/quests/cults_of_tibia/actions_misguided.lua`; `Map::loadMap`; `MapCache` | same live replacement script and no explicit rectangular clear API in the audited path | potentially affected | medium |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | `data-global/.../actions_misguided.lua`; `Map::loadMap`; `MapCache` | same script; source Issue was filed against this line; PR 785 is still open and absent from pinned base | affected claim, static mechanism incomplete | medium-high |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | corresponding action and map/cache paths | action blob is identical to upstream/Otheryn and no donor clearArea change is present | potentially affected | medium |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | corresponding action; `src/map/map.cpp`; `src/map/mapcache.cpp` | exact action blob matches; live map load and retained cache path remain | target path present, runtime required | medium-high |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | map/tile/movement parsing family | client is relevant to desynchronization but no exact failing packet sequence is available | inconclusive | low-medium |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: Misguided item action -> live OTBM replacement with player in area -> server map/cache and packet stream
  -> client movement result
preconditions:
- isolated Otheryn world and database
- both Misguided OTBM variants present
- GOD test player at or near 32562,32377,10
- item 25297 and Misguided Bully/Thief fixture
- maintained OTClient instrumented for packet and crash capture
steps:
- record baseline tile IDs/checksums around the player and process RSS/cache counters
- trigger the exact action while the player remains in the replaced area
- record server tile IDs/checksums immediately after Game.loadMap and after lazy tile access
- move one square in each valid direction and record client/server outcome
- repeat the illusion/reality cycle 50 times to distinguish immediate desync from accumulation
- run a control with the player outside the replaced rectangle
expected_observations:
- a defect is reproduced if occupied-area swaps produce stale tile identity, movement/client failure, or monotonic retained-state
  growth not present in the outside-area control
- a safe implementation keeps map checksums coherent, movement succeeds and memory stabilizes after warm-up
artifacts:
- misguided-fixture.md
- map-checksums.jsonl
- packet-trace.jsonl
- client-results.json
- rss-series.csv
- server.log
- client-crash/
- runtime-feasibility.md
cleanup:
- stop isolated processes and discard fixture database/map state
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: the repository can start the server and validate the seeded HTTP login response, but it has no deterministic game-protocol/client
  driver and no isolated per-scenario world fixture for map, quest, combat, store, boss, persistence or client-rendering actions;
  adding that infrastructure would be implementation outside this audit-only authorization
```

## Runtime execution

```yaml
execution_status: BLOCKED
exact_otheryn_head: not applicable
run_ids: []
observations:
- Docker quickstart validates server startup and the seeded HTTP login response only
- no deterministic game-protocol/client driver or per-scenario world fixture exists in the repository
artifacts:
- runtime-feasibility.md
cleanup_result: not started; no state created
```

## Conclusions

```yaml
truth_status: PARTIALLY_PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: NOT_RUN_INFEASIBLE
owner_action: RESEARCH_REQUIRED
confidence: medium-high
rationale: 'Otheryn contains the exact live-swap action and map/cache architecture implicated by the source, but neither the
  Issue nor static code proves the immediate client-crash mechanism; the supplied steps support a deterministic isolated reproduction
  Runtime execution is infrastructure-blocked: the repository has no deterministic game/client driver and adding one is outside
  audit-only authority.'
```

## Drift and unresolved questions

- Drift after pinned revision: Crystal PR `#785` remains an open candidate rather than accepted upstream truth.
- Unresolved questions:
  - Is the immediate failure caused by stale server tile/cache state, missing remove/add tile packets, a creature remaining on a replaced tile, or a client-version parser assumption?
  - Does the 15-second automatic return to illusion compound the failure?
  - Which map rectangle and cache counters should be exposed by an audit-only harness without product changes?
- Product fixes made by this audit: **none**.
