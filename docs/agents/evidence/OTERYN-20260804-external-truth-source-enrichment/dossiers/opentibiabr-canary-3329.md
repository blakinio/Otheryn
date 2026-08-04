# Dossier — `opentibiabr/canary#3329`

## Identity

```yaml
canonical_key: opentibiabr/canary#3329
predecessor_row: 54
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: wall-item-diagonal-use
research_status: COMPLETE
```

## Source claim

Wall lamps cannot be toggled from diagonal/north positions; a commenter reports they work only from the southeast. The report suggests asymmetry in use-position validation.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: a reachable adjacent player can use an interactive wall lamp according to the same wall-side/facing rules in every symmetric orientation; equivalent rotations must not produce southeast-only behavior
version_boundary: audited item-use and wall-item position rules
evidence_basis: [opentibiabr/canary#3329, issue comment]
conflicts:
  - lamp item IDs and exact wall orientations are only visible in screenshots
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reports orientation-asymmetric use validation |
| CrystalServer | pinned | corresponding item-use/throw-range path | inconclusive |
| `blakinio/canary` | pinned | inherited path | potentially affected |
| Otheryn | pinned | generic use-with distance/position and wall-item metadata paths exist; no named item static vector | inconclusive |
| OTClient | pinned | submits source/target positions; relevant packet control, not authoritative validation |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: player position around wall lamp -> use request -> item transform/state
preconditions:
- inventory of all wall-lamp item pairs and wall orientation metadata
steps:
- build north/south/east/west wall fixtures and test all eight adjacent player offsets
- rotate identical geometry and compare return values/transforms
- record blocked line-of-sight and distance controls
expected_observations:
- rotationally equivalent valid positions succeed and invalid wall-side positions fail consistently
artifacts:
- wall-lamp-orientation-matrix.json
- use-packets.jsonl
- runtime-feasibility.md
cleanup:
- discard fixtures
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
rationale: 'the orientation asymmetry is precise enough for a rotational test matrix, but item metadata and failing validation
  layer are not identified statically Runtime execution is infrastructure-blocked: the repository has no deterministic game/client
  driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Distinguish server use-distance/facing checks from incorrect wall orientation metadata.
- Product fixes made by this audit: **none**.
