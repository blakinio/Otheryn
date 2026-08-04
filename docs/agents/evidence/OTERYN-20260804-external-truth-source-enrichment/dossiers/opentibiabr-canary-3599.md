# Dossier — `opentibiabr/canary#3599`

## Identity

```yaml
canonical_key: opentibiabr/canary#3599
predecessor_row: 28
source_type: issue
prior_bucket: INSUFFICIENT
prior_truth_status: UNPROVEN
family: raid-spawn-burst-performance
research_status: COMPLETE
```

## Source claim

- Current title: `Raid Startup Lag`
- Source URL: `https://github.com/opentibiabr/canary/issues/3599`
- Exact claim: large raid spawn bursts cause a server-wide latency spike; splitting Draptor dragons and Folda Yetis into staggered waves removes the observed ping spike.
- Claimed affected environment: Linux, 8 cores, 16 GB RAM; exact server revision, player count and latency measurements were not supplied.
- Claimed reproduction: start the existing Draptor and Yeti raids with their original large spawn groups.
- Claimed expected behavior: raid startup does not create a material game-loop or network-latency spike, while preserving intended total monster count and timing semantics.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue | `opentibiabr/canary` | Issue `#3599`, open | 2026-08-04 | reports subjective before/after latency and proposed wave configuration | primary claim | no metrics, run IDs, player load or exact revision |
| S2 | repository raid XML | `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | 2026-08-04 | Draptor schedules two 40-dragon areas at 10 s and one 70-dragon area at 20 s | primary target evidence | disproves the literal claim that all 150 dragons spawn in one timestamp, but confirms large bursts |
| S3 | repository raid XML | `blakinio/Otheryn` | same | 2026-08-04 | Yeti schedules 60 monsters in one area event at 60 s | primary target evidence | static count does not establish latency impact |
| S4 | repository raid XML | Crystal/fork lines | pinned audit revisions | 2026-08-04 | corresponding Draptor/Yeti files carry the same burst shapes | cross-repository evidence | shared configuration may reflect intended content, not necessarily a defect |

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: raid event processing remains within an explicitly measured scheduler/game-loop latency budget and preserves intended monster totals, areas, announcements and encounter pacing
version_boundary: content and runtime performance on the audited raid scheduler; hardware and concurrent player/monster load materially affect the result
evidence_basis:
  - S1
  - S2
  - S3
conflicts:
  - source prose says all 150 dragons spawn in the same tick, while audited XML schedules 80 at 10 seconds and 70 at 20 seconds
  - subjective stable ping after staggering does not prove that burst spawning is the sole bottleneck or that proposed timings preserve official encounter semantics
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | Draptor/Yeti raid XML and raid scheduler family | large burst configuration remains in the pinned content | performance risk present | high |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | `data-global/raids/farmine/draptor.xml`, Yeti equivalent | Draptor blob matches target/upstream; same inherited raid family | performance risk present | high |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | corresponding XML | Yeti blob matches target; inherited burst design | performance risk present | high |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | `data-otservbr-global/raids/farmine/draptor.xml`, `.../carlin/yeti.xml` | 80/70 dragon bursts and one 60-Yeti burst | static performance impact inconclusive | high |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | client packet/render path | client can amplify visible-area load but server-wide scheduler claim is not a client-code applicability item | irrelevant to primary static claim | high |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: deterministic raid start under controlled world load -> scheduler/game-loop/network latency and spawn completion
  metrics
preconditions:
- isolated Otheryn database/world and fixed machine/runner class
- scripted observer clients or protocol probes at fixed positions
- baseline population and monster counts recorded
- original and wave-staggered XML variants used only as audit fixtures
steps:
- warm the server and record five minutes of baseline scheduler delay, tick duration, CPU, RSS and probe RTT
- trigger original Draptor raid five times from a clean fixture and capture per-event spawn count/time plus p50/p95/p99/max
  delay
- repeat for Yeti
- repeat the same matrix with the source-proposed wave pattern
- run a no-raid control and verify total monsters/areas/announcements are equivalent between variants
expected_observations:
- reproduced defect: original bursts produce repeatable material tail-latency/tick spikes above the declared budget and staggered
    waves reduce them without content loss
- not reproduced: distributions overlap controls or proposed staggering changes encounter semantics without meaningful performance
    benefit
artifacts:
- raid-fixtures/
- scheduler-delay.csv
- game-loop-duration.csv
- probe-rtt.csv
- spawn-timeline.jsonl
- resource-series.csv
- semantic-parity.json
- runtime-feasibility.md
cleanup:
- terminate isolated server and discard raid fixture state
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
confidence: high
rationale: 'Otheryn undeniably contains large raid spawn bursts, but the source overstates the Draptor timing and provides
  no quantitative latency evidence; controlled performance reproduction is required before changing encounter data Runtime
  execution is infrastructure-blocked: the repository has no deterministic game/client driver and adding one is outside audit-only
  authority.'
```

## Drift and unresolved questions

- Drift after pinned revision: final exact-head XML and scheduler comparison remains required.
- Unresolved questions:
  - What scheduler/game-loop latency budget is acceptable for Otheryn production targets?
  - Are the proposed wave timings faithful to the intended raid experience?
  - Does spawn placement search, monster initialization, spectators, pathfinding or packet fan-out dominate the spike?
- Product fixes made by this audit: **none**.
