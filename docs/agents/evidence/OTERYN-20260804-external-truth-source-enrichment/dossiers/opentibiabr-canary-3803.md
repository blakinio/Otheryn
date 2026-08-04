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
plan_status: READY
system_boundary: clean world load + named map regions -> spawned creature set -> respawn after kill
preconditions:
  - map polygon/coordinates and authoritative monster roster for each named area
steps:
  - search all map/spawn sources for each area/monster and emit coordinate inventory
  - start isolated world, enumerate creatures in each polygon, kill them and observe respawn interval/count
  - verify no duplicate or out-of-bounds spawns
expected_observations:
  - each area contains its defined roster and repopulates deterministically
artifacts: [spawn-inventory.json, area-creatures.jsonl, respawn-timeline.csv]
cleanup: [discard isolated world]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: authoritative area polygons and official spawn values are still required for a repair decision
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
rationale: missing named entries are testable, but the source supplies neither map polygons nor versioned official spawn data
```

## Drift and unresolved questions

- Confirm whether each area is actually present in the pinned Otheryn map before classifying missing content.
- Product fixes made by this audit: **none**.
