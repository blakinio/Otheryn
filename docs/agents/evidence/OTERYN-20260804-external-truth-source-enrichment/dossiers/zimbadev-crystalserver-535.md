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
plan_status: READY
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
artifacts: [goroma-spawn-inventory.json, world-change-timeline.jsonl, route-results.json]
cleanup: [discard isolated world]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: authoritative schedule and exact event population must be sourced before implementation; unconditional-versus-controlled state is testable
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
confidence: medium-high
rationale: the symptom and missing-controller hypothesis are coherent, but exact world-change data and scheduler semantics are absent; an on/off inventory test can separate unconditional spawns from controller failure
```

## Drift and unresolved questions

- Source official activation duration/probability and exact monster/map delta before repair.
- Product fixes made by this audit: **none**.
