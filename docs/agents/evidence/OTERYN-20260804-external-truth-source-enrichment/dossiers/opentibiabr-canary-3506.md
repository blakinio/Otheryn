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
plan_status: BLOCKED_INFEASIBLE
system_boundary: clean arena entry/combat -> boss events, summons, linked participation -> completion/reset
preconditions:
- isolated party
- resettable arenas
- deterministic health/damage control
steps:
- run each boss through all health/time thresholds
- enumerate registered events, summons and arena state every second
- test wipe, timeout, repeat entry and summon-cap behavior
- for twins, record activation/targetability and shared completion
expected_observations:
- every named encounter performs defined mechanics and terminates all spawned state on completion/reset
artifacts:
- grave-danger-timelines.jsonl
- summons.csv
- arena-state.jsonl
- runtime-feasibility.md
cleanup:
- reset arenas and discard party state
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
confidence: medium
rationale: 'the source defines distinct observable failures across five bosses but does not provide versioned encounter specifications
  Runtime execution is infrastructure-blocked: the repository has no deterministic game/client driver and adding one is outside
  audit-only authority.'
```

## Drift and unresolved questions

- Source authoritative encounter traces before implementing timings/caps.
- Product fixes made by this audit: **none**.
