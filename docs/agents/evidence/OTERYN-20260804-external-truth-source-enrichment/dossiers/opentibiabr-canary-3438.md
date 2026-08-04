# Dossier — `opentibiabr/canary#3438`

## Identity

```yaml
canonical_key: opentibiabr/canary#3438
predecessor_row: 42
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: lions-rock-fountain-gems
research_status: COMPLETE
```

## Source claim

During Lion's Rock Quest, using the required gems on the fountain tiles produces no result. The source provides no gem IDs, coordinates, storage state, order or expected tile transformations.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: each required gem used on its matching configured tile at the correct quest state is consumed/registered exactly once, advances the puzzle state and unlocks the fountain progression after the complete set
version_boundary: Lion's Rock datapack/map at audited revisions
evidence_basis: [opentibiabr/canary#3438]
conflicts:
  - exact IDs, positions and order are absent from the source
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reports affected action/map integration |
| CrystalServer | pinned | corresponding quest lineage; exact parity unknown |
| `blakinio/canary` | pinned | inherited datapack/map | potentially affected |
| Otheryn | pinned | Lion's Rock content exists; bounded text search cannot map the source's unnamed tiles/gems to one action | inconclusive |
| OTClient | pinned | standard use-with input | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: quest storage + gem/item + exact fountain tile -> item consumption, tile/action state and quest progression
preconditions:
  - inventory of Lion's Rock action registrations, map action/unique IDs and required gem IDs
steps:
  - derive every valid gem/tile pair from target data and map dump
  - execute each pair at pre-quest, correct and completed states
  - test order, duplicate use and wrong-pair controls
  - verify final fountain/door/storage transition
expected_observations:
  - valid pairs advance exactly once and complete set unlocks progression
artifacts: [lions-rock-actions.json, gem-tile-matrix.jsonl, storage-transitions.json]
cleanup: [discard quest player/map state]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: none after generating the action/map inventory
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
rationale: the quest invariant is clear enough to build a bounded matrix, but the source omits every concrete identifier needed to assign a static defect
```

## Drift and unresolved questions

- Generate source-of-truth IDs/positions from Otheryn data/map before testing; do not infer them from screenshots.
- Product fixes made by this audit: **none**.
