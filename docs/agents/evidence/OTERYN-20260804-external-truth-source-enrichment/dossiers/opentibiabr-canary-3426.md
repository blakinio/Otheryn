# Dossier — `opentibiabr/canary#3426`

## Identity

```yaml
canonical_key: opentibiabr/canary#3426
predecessor_row: 46
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: bomb-field-monster-damage
research_status: COMPLETE
```

## Source claim

Monsters walk across bomb/field tiles without receiving damage.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: a susceptible monster entering or remaining on a player-owned damaging bomb/field receives the configured initial/periodic damage and attribution; immune monsters and exhausted field states remain unaffected
version_boundary: audited magic-field/bomb combat system
evidence_basis: [opentibiabr/canary#3426]
conflicts:
  - source screenshot does not identify field item, monster, immunity or ownership
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reports missing field-entry damage |
| CrystalServer | pinned | related field-condition path | inconclusive |
| `blakinio/canary` | pinned | inherited path | potentially affected |
| Otheryn | pinned | field movement/condition and monster immunity paths exist; exact item/monster vector absent | static inconclusive |
| OTClient | pinned | observes effects only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: field ownership/state + monster step-in/stay -> combat condition and damage attribution
preconditions: [representative fire/energy/poison bombs and susceptible/immune monsters]
steps:
  - create each field through player and environment sources
  - force monsters to enter, remain and re-enter
  - record HP, conditions, field decay and attacker attribution
  - compare immune, summon and boss controls
expected_observations:
  - susceptible monsters receive the defined damage sequence exactly once per trigger policy
artifacts: [bomb-field-matrix.jsonl, combat-events.jsonl]
cleanup: [remove fields and discard monsters]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: exact screenshot vector is missing, but representative matrix is feasible
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
rationale: the symptom is testable across a bounded field/immunity matrix, but the source omits the exact item and target
```

## Drift and unresolved questions

- Coordinate this run with item `#3584` to separate cast-time initial damage from step-in field damage.
- Product fixes made by this audit: **none**.
