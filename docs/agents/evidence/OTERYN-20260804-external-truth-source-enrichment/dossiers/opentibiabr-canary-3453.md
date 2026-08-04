# Dossier — `opentibiabr/canary#3453`

## Identity

```yaml
canonical_key: opentibiabr/canary#3453
predecessor_row: 40
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: ancient-oasis-door
research_status: COMPLETE
```

## Source claim

At Oasis Tomb, winning the carrot/hat lever transforms door item `1662` at `(33122,32765,14)` to `1663`, but the player still cannot pass to the boss. The source supplies the exact action code and action ID `12107`.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: a successful lever roll creates the carrot, changes the blocking door into a walkable/open state for the intended window, permits passage, then restores the complete puzzle state deterministically
version_boundary: Ancient Oasis Tomb datapack/map at audited revisions
evidence_basis: [opentibiabr/canary#3453]
conflicts:
  - supplied revert function resets lever/carrot but does not restore the door, indicating an additional lifecycle defect beyond walkability
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | exact source action/map claim |
| CrystalServer | pinned | corresponding tomb action/map lineage | inconclusive |
| `blakinio/canary` | pinned | inherited global datapack | likely affected |
| Otheryn | pinned | relevant action/map path exists; map tile stack and item-type walkability require runtime/tile dump | static inconclusive |
| OTClient | pinned | standard tile movement/use display | no fix target |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: forced winning lever roll -> door tile state/collision -> passage and timed reset
preconditions:
- isolated map at 33122,32765,14 and deterministic RNG
steps:
- dump full tile stack before, during and after the four-second event
- force success, assert door transform and attempt movement through both directions
- wait for reset and verify lever, carrot and door restoration
- run failure control
expected_observations:
- success creates a temporarily walkable path and restores every puzzle object exactly once
artifacts:
- oasis-door-timeline.jsonl
- tile-dumps.json
- movement-results.json
- runtime-feasibility.md
cleanup:
- restore/discard map/player state
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
truth_status: PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: NOT_RUN_INFEASIBLE
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: 'exact coordinates, IDs and code make the puzzle falsifiable; tile collision and missing door reset must be observed
  before defining the repair Runtime execution is infrastructure-blocked: the repository has no deterministic game/client
  driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Determine the correct open/closed item IDs and whether map contains an additional blocking object.
- Product fixes made by this audit: **none**.
