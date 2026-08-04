# Dossier — `opentibiabr/canary#3506`

## Identity

```yaml
canonical_key: opentibiabr/canary#3506
predecessor_row: 33
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: grave-danger-bosses
research_status: COMPLETE
```

## Source claim

Multiple Grave Danger bosses lack encounter mechanics: Vlarkorth, Krule and Osam behave as basic melee targets; Azaram endlessly summons Condensed Sins; Baeloc never joins Nictrios.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: each boss executes its bounded phase/event mechanics, summon populations remain capped/consumable, linked twins enter and synchronize correctly, and completion/reset/reward states are exact
version_boundary: Grave Danger encounter generation in the audited datapack
evidence_basis: [opentibiabr/canary#3506]
conflicts:
  - no authoritative phase timings, thresholds or summon caps are supplied
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reports five encounter gaps |
| CrystalServer | pinned | related encounter lineage | inconclusive |
| `blakinio/canary` | pinned | inherited content | potentially affected |
| Otheryn | pinned | named boss scripts/monsters require event-registration and phase inventory; no source truth for numeric mechanics | static inconclusive |
| OTClient | pinned | observes encounter packets/effects only | no fix target |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: clean arena entry/combat -> boss events, summons, linked participation -> completion/reset
preconditions: [isolated party, resettable arenas, deterministic health/damage control]
steps:
  - run each boss through all health/time thresholds
  - enumerate registered events, summons and arena state every second
  - test wipe, timeout, repeat entry and summon-cap behavior
  - for twins, record activation/targetability and shared completion
expected_observations:
  - every named encounter performs defined mechanics and terminates all spawned state on completion/reset
artifacts: [grave-danger-timelines.jsonl, summons.csv, arena-state.jsonl]
cleanup: [reset arenas and discard party state]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: numeric official mechanics require a primary reference; structural reproduction is feasible
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
rationale: the source defines distinct observable failures across five bosses but does not provide versioned encounter specifications
```

## Drift and unresolved questions

- Source authoritative encounter traces before implementing timings/caps.
- Product fixes made by this audit: **none**.
