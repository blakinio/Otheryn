# Dossier — `opentibiabr/canary#3288`

## Identity

```yaml
canonical_key: opentibiabr/canary#3288
predecessor_row: 56
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: wheel-sap-strength-area
research_status: COMPLETE
```

## Source claim

Unlocking stage 2 of Sap Strength in the Wheel should enlarge the spell area, but the cast still uses the base area.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: the server derives Sap Strength area from the player's committed Wheel stage; stage 0/1 uses its defined base/intermediate shape and stage 2 applies the larger shape consistently after relog and Wheel changes
version_boundary: Wheel generation containing two Sap Strength upgrade stages
evidence_basis: [opentibiabr/canary#3288]
conflicts:
  - exact tile mask for each stage is not supplied by the Issue
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | stage-2 area failure reported |
| CrystalServer | pinned | related Wheel/spell lineage | inconclusive |
| `blakinio/canary` | pinned | inherited implementation | potentially affected |
| Otheryn | pinned | Wheel perk resolution and spell area selection must be traced together; no exact stage mask proven | static inconclusive |
| OTClient | pinned | Wheel selection/UI and combat visualization are relevant controls | end-to-end required |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: committed Wheel stage -> spell area selection -> affected tile/creature set
preconditions: [identical players with stages 0, 1 and 2 and a grid of test targets]
steps:
  - cast from every facing direction for each stage
  - record selected area mask and hit targets
  - relog/restart and reallocate Wheel between stages
  - test insufficient points and stale client-layout controls
expected_observations:
  - stage-specific masks differ exactly as specified and persist across relog
artifacts: [sap-strength-area-masks.json, hit-grid.jsonl, wheel-state.json]
cleanup: [discard players/targets]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: authoritative masks must be sourced before implementation; stage differentiation is immediately testable
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
rationale: the source provides a direct stage-dependent invariant; a tile-grid test can distinguish missing perk lookup from incorrect area data
```

## Drift and unresolved questions

- Obtain the official stage-1/stage-2 area masks before repair.
- Product fixes made by this audit: **none**.
