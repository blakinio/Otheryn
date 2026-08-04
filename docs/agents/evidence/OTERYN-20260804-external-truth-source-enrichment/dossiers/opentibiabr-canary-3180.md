# Dossier — `opentibiabr/canary#3180`

## Identity

```yaml
canonical_key: opentibiabr/canary#3180
predecessor_row: 59
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: corpse-tile-stack-use
research_status: COMPLETE
```

## Source claim

A corpse on a particular map square cannot be opened by direct use, while Browse Field can open the same corpse. This isolates a tile-stack/top-use-object or map item ordering problem rather than container permissions.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: direct use resolves the visible corpse/container on the selected tile according to client stack position and opens it under the same permissions as Browse Field; static ground/decorative items must not shadow the corpse incorrectly
version_boundary: audited map stack/use-item protocol
evidence_basis: [opentibiabr/canary#3180]
conflicts:
  - screenshots do not provide coordinate or item IDs
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | direct-use versus Browse Field divergence reported |
| CrystalServer | pinned | related tile stack/use path | inconclusive |
| `blakinio/canary` | pinned | inherited path/map | potentially affected |
| Otheryn | pinned | stack-position resolution and map tile flags require a fixture; no coordinate supplied | static inconclusive |
| OTClient | pinned | encodes clicked stack position and Browse Field request | protocol-critical control |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: tile stack + clicked stack position -> server item resolution -> corpse container open
preconditions:
  - fixtures with corpse over/under representative decorative, hangable, splash and blocking items
steps:
  - capture tile description and client click stack position for each fixture
  - direct-open corpse and repeat through Browse Field
  - vary corpse insertion order, decay/transform and multiple corpses
  - verify ownership/loot-window controls
expected_observations:
  - direct click resolves the same corpse/container as the corresponding Browse Field selection
artifacts: [corpse-stack-matrix.json, use-packets.jsonl, tile-descriptions.jsonl]
cleanup: [remove corpses/fixtures]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: original coordinate is missing, but a bounded stack-class matrix is feasible
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
truth_status: PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: PENDING
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: Browse Field success proves the corpse is valid and accessible; direct-use stack resolution can be isolated with controlled tile fixtures
```

## Drift and unresolved questions

- Recover the original screenshot tile IDs if possible, but do not block the generalized stack-resolution test.
- Product fixes made by this audit: **none**.
