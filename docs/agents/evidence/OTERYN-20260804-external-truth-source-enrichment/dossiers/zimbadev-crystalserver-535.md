# Dossier — `zimbadev/crystalserver#535`

## Identity

```yaml
canonical_key: zimbadev/crystalserver#535
predecessor_row: 103
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: goroma-fire-from-earth-world-change
research_status: COMPLETE
```

## Source claim

Goroma Volcano permanently contains the Fire from the Earth monster population, making low-level missions harder. Discussion states the likely cause is absence of the mini world-change controller, leaving event monsters as unconditional map spawns.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: Fire from the Earth monsters and map state are active only while the mini world change is selected, initialize and reset atomically, and remain absent during the normal Goroma mission state
version_boundary: Goroma world map/content generation containing Fire from the Earth
evidence_basis: [zimbadev/crystalserver#535, issue discussion]
conflicts:
  - source does not define activation probability, duration, exact monsters, tiles or reset schedule
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | event monsters exist; exact world-change controller/spawn separation requires inventory |
| CrystalServer | pinned | source suggests event controller absent and monsters unconditional |
| `blakinio/canary` | pinned | inherited map/spawn lineage | potentially affected |
| Otheryn | pinned | bounded search finds event monster types but not a named controller; map/spawn/world-change inventory is required | static inconclusive |
| OTClient | pinned | observes world state only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: world-change scheduler/state -> Goroma map/spawn activation -> mission-area creature inventory
preconditions:
- extracted normal/event polygons, spawn entries and world-change registry
steps:
- start clean worlds with event forced off/on and enumerate monsters/map tiles
- advance scheduler across activation, expiry and restart boundaries
- verify low-level mission route in normal state and event population only in active state
- test duplicate activation and stale persisted state
expected_observations:
- event monsters are absent when off, appear once when on and are fully removed/reset on expiry/restart according to policy
artifacts:
- goroma-spawn-inventory.json
- world-change-timeline.jsonl
- route-results.json
- runtime-feasibility.md
cleanup:
- discard isolated world
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
rationale: 'the symptom and missing-controller hypothesis are coherent, but exact world-change data and scheduler semantics
  are absent; an on/off inventory test can separate unconditional spawns from controller failure Runtime execution is infrastructure-blocked:
  the repository has no deterministic game/client driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Source official activation duration/probability and exact monster/map delta before repair.
- Product fixes made by this audit: **none**.
