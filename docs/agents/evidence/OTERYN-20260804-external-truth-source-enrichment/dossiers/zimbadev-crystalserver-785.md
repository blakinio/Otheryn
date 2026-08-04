# Dossier — `zimbadev/crystalserver#785`

## Identity

```yaml
canonical_key: zimbadev/crystalserver#785
predecessor_row: 87
source_type: pull_request
prior_bucket: REPRO
prior_truth_status: PARTIALLY_PROVEN
family: live-map-swap-cache-retention
research_status: COMPLETE
```

## Source claim

- Current title: `fix: Add clearArea handler and Lua binding (Map Change Clear Cache)`
- Source URL: `https://github.com/zimbadev/crystalserver/pull/785`
- Exact claim: repeated live map swaps retain obsolete tile/cache objects because only coordinates present in the new OTBM are overwritten; adding an explicit rectangular clear operation prevents stale cache accumulation.
- Claimed affected version/protocol: CrystalServer base `c00fd4b0910ce4fca28dd158c5a304a999507eb5`; no client protocol boundary claimed.
- Claimed reproduction: Ebb and Flow/Soul War map switching over long uptime; no exact command, iteration count or measured series supplied.
- Claimed expected behavior: replacing a bounded map area releases obsolete tile/cache state and does not grow retained map memory across equivalent swap cycles.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream PR | `zimbadev/crystalserver` | PR `#785`, head `54fd1ddaf7f78bbc9a34297e6f391664d5645746` | 2026-08-04 | proposed `Map::clearArea`, `Game.clearArea` Lua binding and stated retained-cache mechanism | primary claim/candidate patch | draft-quality statement says not 100% and ongoing tests; no measurements |
| S2 | PR patch | `zimbadev/crystalserver` | same head | 2026-08-04 | clears `Floor` tile and tile-cache pointers in a rectangular XYZ loop | exact change evidence | patch does not update callers in the shown diff to invoke clearArea before each relevant loadMap operation |
| S3 | repository code | `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | 2026-08-04 | `MapCache` owns `retainedBasicTiles`; `setBasicTile` replaces coordinates loaded from the new OTBM, while no matching rectangular clear API is present | target mechanism evidence | ownership retention may be intentional deduplication; growth rate and reachability require measurement |
| S4 | related Issue | `zimbadev/crystalserver#852` | open 2026-08-03 | occupied live swaps can also cause immediate client failure | corroborating symptom | does not prove memory leak and may have a separate packet-state cause |

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: repeated replacement of the same bounded map region should converge to stable retained tile/cache memory after warm-up and should remove coordinates absent from the newly loaded OTBM
version_boundary: applies to live partial-map loading through Game.loadMap/IOMap over an already populated region; independent of application packet version but potentially visible to connected clients
evidence_basis:
  - S1
  - S2
  - S3
conflicts:
  - PR author explicitly states the candidate is not complete and supplies no before/after memory evidence
  - clearArea nulls floor entries but the patch alone does not demonstrate release of every globally deduplicated or retained BasicTile object
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | `src/map/map.cpp`, `mapcache.cpp/.hpp`, `Game::loadMap` | shared cache architecture; no PR 785 rectangular clear API | potentially affected | medium |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | same paths | pinned base lacks open PR 785 changes | potentially affected | medium-high |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | same paths | inherited cache/load architecture and no donor clear API | potentially affected | medium |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | `src/map/map.cpp`; `src/map/mapcache.cpp/.hpp`; Lua Game functions | retains BasicTile ownership and lazily replaces loaded coordinates; no explicit bounded clear API | target path present, measurement required | medium-high |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | client map state | server heap-retention claim is not a client implementation concern; client is relevant only to separate desync symptoms | irrelevant to memory claim | high |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: repeated deterministic partial-map swaps -> MapCache retained objects and process memory -> convergence or monotonic growth
preconditions:
  - isolated Otheryn build with audit-only counters obtainable without changing production behavior
  - two small OTBM fixtures with overlapping rectangle and intentionally absent coordinates in alternating variants
  - fixed player/creature occupancy matrix, including an empty-area control
steps:
  - capture baseline RSS, heap allocation summary, map sector/floor/tile/cache counts and retainedBasicTiles count
  - alternate fixture A and B for 10 warm-up cycles and 500 measured cycles
  - after every cycle force all fixture coordinates through the same bounded read path and capture counters
  - repeat with the source Misguided and Ebb/Flow maps if fixture result is positive
  - run an identical no-swap control for elapsed-time allocation drift
expected_observations:
  - confirmed defect: retained tile/cache count or leak-attributed heap grows with swap count and absent coordinates remain materializable from stale state
  - not reproduced: counters and RSS plateau after warm-up and absent coordinates remain absent
artifacts:
  - fixture-a.otbm
  - fixture-b.otbm
  - map-cache-counters.csv
  - rss-heap-series.csv
  - absent-coordinate-checks.jsonl
  - no-swap-control.csv
  - sanitizer-or-heap-report.txt
cleanup:
  - remove fixtures and terminate isolated process; discard audit-only state
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: execution requires an audit harness or temporary CI workflow exposing counters; no product fix is authorized
```

## Runtime execution

```yaml
execution_status: NOT_RUN
exact_otheryn_head: not applicable
run_ids: []
observations: []
artifacts: []
cleanup_result: not run
```

## Conclusions

```yaml
truth_status: PARTIALLY_PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: PENDING
owner_action: RESEARCH_REQUIRED
confidence: medium
rationale: the target contains the same retained map-cache architecture and lacks the proposed clear API, but the PR provides neither complete caller integration nor quantitative proof; a bounded swap soak is required before authorizing a fix programme
```

## Drift and unresolved questions

- Drift after pinned revision: PR `#785` remains open, mergeable false, with one commit and an explicit warning that testing is ongoing.
- Unresolved questions:
  - Which retained object family actually grows: floor tile pointers, tile-cache pointers, globally deduplicated BasicTiles, creatures/items, or allocator high-water mark only?
  - Is clearing all objects in the rectangle safe for players, houses, zones and persistent items?
  - Must connected clients be evacuated or fully re-described before any server-side clear/load sequence?
- Product fixes made by this audit: **none**.
