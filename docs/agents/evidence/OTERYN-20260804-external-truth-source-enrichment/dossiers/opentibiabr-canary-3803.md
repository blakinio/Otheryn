# Dossier — `opentibiabr/canary#3803`

## Identity

```yaml
canonical_key: opentibiabr/canary#3803
predecessor_row: 21
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: modern-monster-spawns
research_status: COMPLETE
```

## Source claim

Podzilla, Nimmersatt's Breeding Ground/Wardragon, Inner Crypt and Stag Bastion spawn definitions are absent from the global monster spawn XML.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: every implemented hunting area has version-correct monster spawn coordinates, radii, counts and intervals and can repopulate after a clean start/kill cycle
version_boundary: content generation containing the four named areas
evidence_basis: [opentibiabr/canary#3803, issue discussion]
conflicts:
  - source does not provide official coordinates/counts or prove all four areas exist in the pinned map
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reports missing spawn entries |
| CrystalServer | pinned | map/content lineage may differ | inconclusive |
| `blakinio/canary` | pinned | inherited world spawn file | potentially affected |
| Otheryn | pinned | exact spawn/map inventory for the four names is required; source does not establish coordinates | static inconclusive |
| OTClient | pinned | no server spawn ownership | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: clean world load + named map regions -> spawned creature set -> respawn after kill
preconditions:
- map polygon/coordinates and authoritative monster roster for each named area
steps:
- search all map/spawn sources for each area/monster and emit coordinate inventory
- start isolated world, enumerate creatures in each polygon, kill them and observe respawn interval/count
- verify no duplicate or out-of-bounds spawns
expected_observations:
- each area contains its defined roster and repopulates deterministically
artifacts:
- spawn-inventory.json
- area-creatures.jsonl
- respawn-timeline.csv
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
confidence: medium
rationale: 'missing named entries are testable, but the source supplies neither map polygons nor versioned official spawn
  data Runtime execution is infrastructure-blocked: the repository has no deterministic game/client driver and adding one
  is outside audit-only authority.'
```

## Drift and unresolved questions

- Confirm whether each area is actually present in the pinned Otheryn map before classifying missing content.
- Product fixes made by this audit: **none**.
