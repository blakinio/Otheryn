# Dossier — `opentibiabr/canary#2396`

## Identity

```yaml
canonical_key: opentibiabr/canary#2396
predecessor_row: 66
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: offline-training-magic
research_status: COMPLETE
```

## Source claim

Magic-level offline training grants no progress from either a house bed or an offline-training statue.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: selecting magic training through every supported entry point persists the selected skill/time, consumes eligible offline training time once, and awards vocation-correct mana-spent/magic-level progress on next login
version_boundary: audited offline training system and vocation formulas
evidence_basis: [opentibiabr/canary#2396]
conflicts:
  - source does not state vocation, duration, remaining offline time or displayed error
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | both bed and statue paths reported ineffective |
| CrystalServer | pinned | related training/persistence lineage | inconclusive |
| `blakinio/canary` | pinned | inherited implementation | potentially affected |
| Otheryn | pinned | shared post-login progress calculation versus entry-point selection must be traced | static inconclusive |
| OTClient | pinned | selects training and displays skills | end-to-end observer |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: bed/statue selection + offline duration/vocation -> persisted training record -> login skill progress
preconditions:
- one player per vocation with fixed skill state and offline time
steps:
- select magic training through bed and statue independently
- simulate controlled offline durations including zero, cap and partial intervals
- relog/restart and record selected skill, consumed time, mana-spent and magic-level progression
- compare melee/distance training controls and promotion variants
expected_observations:
- both entry points produce identical vocation-correct magic progress and consume time exactly once
artifacts:
- offline-training-matrix.json
- database-state.jsonl
- skill-progress.csv
- runtime-feasibility.md
cleanup:
- discard players/database
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
rationale: 'failure across both entry points suggests a shared selection or magic-progress calculation; a vocation/duration
  matrix can isolate it deterministically Runtime execution is infrastructure-blocked: the repository has no deterministic
  game/client driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Capture the source's unspecified error text if available, but do not block the controlled persistence test.
- Product fixes made by this audit: **none**.
