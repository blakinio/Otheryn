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
plan_status: READY
system_boundary: completed market sales -> statistics aggregation/cache -> Cyclopedia packet/UI classification
preconditions: [isolated market database and known item IDs/thresholds]
steps:
  - create open offers without sale and assert no average change
  - complete controlled sales at fixed prices/quantities and calculate expected rolling average
  - trigger scheduled/manual refresh, relog and restart
  - decode Cyclopedia values/colors for items with zero, one and multiple transactions
expected_observations:
  - only completed sales affect the deterministic average and every layer exposes the same value/classification
artifacts: [market-transactions.csv, expected-averages.json, cyclopedia-packets.jsonl, cache-state.json]
cleanup: [discard market/account database]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: official window/weight/threshold rules must be sourced before implementation; data-flow reproduction is feasible
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
rationale: source separates open offers from completed sales and reports persistent absence after real transactions; a controlled database/packet test can isolate recording, aggregation, cache or serialization
```

## Drift and unresolved questions

- Source exact official averaging window, weighting and color thresholds.
- Product fixes made by this audit: **none**.
