# Dossier — `opentibiabr/canary#3251`

## Identity

```yaml
canonical_key: opentibiabr/canary#3251
predecessor_row: 58
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: forge-transfer-eligibility
research_status: COMPLETE
```

## Source claim

A normal non-convergence Forge transfer incorrectly requires source and target items from the same equipment slot; official eligibility should require the same Forge class, as convergence transfer does.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: non-convergence transfer accepts compatible source/target items based on Forge class and tier/rule constraints, not matching equipment slot; invalid class/tier combinations fail without consuming resources
version_boundary: audited Exaltation Forge transfer rules
evidence_basis: [opentibiabr/canary#3251]
conflicts: []
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | same-slot validation defect reported |
| CrystalServer | pinned | related Forge validation path | inconclusive |
| `blakinio/canary` | pinned | inherited implementation | potentially affected |
| Otheryn | pinned | normal/convergence transfer predicates and item class/slot data must be compared | static inconclusive |
| OTClient | pinned | Forge UI filters may mirror server eligibility but server remains authoritative | end-to-end control |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: source/target class-slot-tier pair + transfer mode -> validation/cost -> resulting tiers/resources
preconditions: [fixture items spanning same/different class, slot and tier]
steps:
  - execute full pair matrix for normal and convergence transfer
  - record validation reason, costs, consumed items and resulting tiers
  - test cancellation, insufficient resources and replay/duplicate requests
expected_observations:
  - normal transfer accepts same-class cross-slot pairs allowed by rules and conserves resources on every rejection
artifacts: [forge-transfer-matrix.json, resource-ledger.jsonl, protocol-results.json]
cleanup: [discard player/items/database]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: none
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
rationale: the source provides a clear eligibility invariant; a class/slot pair matrix can identify whether target validation incorrectly reuses equipment-slot equality
```

## Drift and unresolved questions

- Source version-specific class/tier restrictions before implementation.
- Product fixes made by this audit: **none**.
