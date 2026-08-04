# Dossier — `opentibiabr/canary#2083`

## Identity

```yaml
canonical_key: opentibiabr/canary#2083
predecessor_row: 68
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: cyclopedia-market-average
research_status: COMPLETE
```

## Source claim

Cyclopedia item values and color outlines do not update from completed market transactions, even for items sold during the current week. Discussion correctly distinguishes completed transactions from open offers.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: only completed market transactions contribute to the configured rolling average; the resulting item value/tier is persisted, recalculated on schedule and serialized to Cyclopedia consistently after transaction, restart and cache refresh
version_boundary: audited market statistics and Cyclopedia item classification protocol
evidence_basis: [opentibiabr/canary#2083, issue discussion]
conflicts:
  - source does not define rolling window, quantity weighting, outlier policy or color thresholds
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | completed-sale averages reported absent |
| CrystalServer | pinned | related market/Cyclopedia lineage | inconclusive |
| `blakinio/canary` | pinned | inherited implementation | potentially affected |
| Otheryn | pinned | transaction recording, average query/cache and Cyclopedia serialization are three separate gates requiring trace | static inconclusive |
| OTClient | pinned | parses value/classification and renders outlines | protocol/UI control |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: completed market sales -> statistics aggregation/cache -> Cyclopedia packet/UI classification
preconditions:
- isolated market database and known item IDs/thresholds
steps:
- create open offers without sale and assert no average change
- complete controlled sales at fixed prices/quantities and calculate expected rolling average
- trigger scheduled/manual refresh, relog and restart
- decode Cyclopedia values/colors for items with zero, one and multiple transactions
expected_observations:
- only completed sales affect the deterministic average and every layer exposes the same value/classification
artifacts:
- market-transactions.csv
- expected-averages.json
- cyclopedia-packets.jsonl
- cache-state.json
- runtime-feasibility.md
cleanup:
- discard market/account database
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
rationale: 'source separates open offers from completed sales and reports persistent absence after real transactions; a controlled
  database/packet test can isolate recording, aggregation, cache or serialization Runtime execution is infrastructure-blocked:
  the repository has no deterministic game/client driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Source exact official averaging window, weighting and color thresholds.
- Product fixes made by this audit: **none**.
