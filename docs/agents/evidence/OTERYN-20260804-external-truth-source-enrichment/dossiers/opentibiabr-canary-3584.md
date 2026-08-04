# Dossier — `opentibiabr/canary#3584`

## Identity

```yaml
canonical_key: opentibiabr/canary#3584
predecessor_row: 29
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: field-rune-initial-damage
research_status: COMPLETE
```

## Source claim

Fire, energy and poison field runes create fields but deal no initial damage when cast at a monster. A later comment demonstrates damage after adding an explicit combat formula callback and condition to the rune.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: casting each offensive field rune on a valid monster applies the intended immediate hit/attribution and creates the field with its configured periodic condition; ownership/tags are preserved for bosses and loot credit
version_boundary: audited field-rune and combat-condition system
evidence_basis: [opentibiabr/canary#3584, issue workaround]
conflicts:
  - community workaround hardcodes damage and may not match official formulas
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reproduces no initial damage |
| CrystalServer | pinned | related combat/field rune family; exact formulas differ |
| `blakinio/canary` | pinned | inherited path; inconclusive |
| Otheryn | pinned | field creation and combat-condition paths exist; bounded search did not establish an initial formula callback for all three runes | potentially affected |
| OTClient | pinned | displays damage/effects only; no fix target |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: field-rune cast -> immediate combat result + created field/condition -> monster health and attribution
preconditions:
  - deterministic caster and neutral monsters with known resistances
steps:
  - cast fire, energy and poison field runes directly on a monster and on an empty tile later entered by a monster
  - record immediate HP delta, periodic ticks, field item, attacker attribution and loot/raid tag
  - compare PvP/non-PvP field variants and immune target controls
expected_observations:
  - direct cast follows authoritative immediate-damage rule and periodic condition remains correct
artifacts: [field-rune-matrix.jsonl, combat-events.jsonl, server.log]
cleanup: [remove fields and discard actors]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: official initial-damage formula remains to be sourced; reproduction of zero/nonzero behavior is feasible
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
confidence: medium-high
rationale: the source supplies a simple cross-element reproduction and a working but non-authoritative workaround; run the target and source the intended damage formula before opening a fix
```

## Drift and unresolved questions

- Separate immediate damage from delayed field condition and attacker attribution.
- Product fixes made by this audit: **none**.
