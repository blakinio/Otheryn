# Dossier — `opentibiabr/canary#3534`

## Identity

```yaml
canonical_key: opentibiabr/canary#3534
predecessor_row: 31
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: beregar-pick-crack
research_status: COMPLETE
```

## Source claim

A Beregar crack does not teleport/open when used with a pick. Later discussion states that pick item `3456` works and suggests the report may use the wrong pick; it also identifies a separate `6298` + positive action ID hole-transform condition.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: using the canonical pick 3456 on the configured Beregar crack/hole target at the correct quest state transforms/opens the passage and permits progression; unrelated pick variants need not work
version_boundary: Hidden City of Beregar datapack at audited revisions
evidence_basis: [opentibiabr/canary#3534, issue discussion]
conflicts:
  - source does not state pick ID or exact crack coordinate/action ID
  - later tester reports canonical pick works
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | original report contradicted by later canonical-pick success |
| CrystalServer | pinned | corresponding pick/quest action family; exact map action IDs unknown |
| `blakinio/canary` | pinned | inherited action/map lineage | inconclusive |
| Otheryn | pinned | bounded search cannot map the underspecified screenshot to one target/action ID | inconclusive |
| OTClient | pinned | standard use-with input only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: pick item + exact crack/action ID + quest storage -> transform/teleport/progression
preconditions:
- tile dump of every Beregar item 6298/action ID and canonical pick 3456
steps:
- use pick 3456 on each configured crack at valid and invalid quest states
- repeat with common noncanonical pick variants
- record transform, decay, teleport, messages and storage
expected_observations:
- canonical configured target works; invalid items/states fail deterministically
artifacts:
- beregar-cracks.json
- pick-matrix.jsonl
- server.log
- runtime-feasibility.md
cleanup:
- restore/discard map and player state
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
rationale: 'the report omits the item and coordinate, while later evidence says the canonical pick works; a bounded map/action
  inventory can resolve whether any legitimate crack remains broken Runtime execution is infrastructure-blocked: the repository
  has no deterministic game/client driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Do not remove action-ID checks until every 6298 map use is inventoried.
- Product fixes made by this audit: **none**.
