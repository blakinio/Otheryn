# Dossier — `opentibiabr/canary#3549`

## Identity

```yaml
canonical_key: opentibiabr/canary#3549
predecessor_row: 30
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: gnomprona-hazard-tagging
research_status: COMPLETE
```

## Source claim

Ordinary Gnomprona monsters are counted inside the hazard zone but do not receive the monster hazard tag, so dodge/damage/defense and death-triggered primal pods or Plunder Patriarchs do not operate. Removing the `not monster:hazard()` guard makes death rewards trigger; scripted Primal Menace monsters work.

## Static evidence

Pinned Otheryn registers `HazardMonster.onSpawn` for every monster entering the zone, but `PrimalHazardDeath` immediately returns when `monster:hazard()` is false. The exact reporter guard and event path are present.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: every eligible ordinary monster spawned inside the registered Gnomprona hazard zone receives the active hazard state and participates in configured crit/dodge/damage/defense and death reward mechanics; excluded bosses/areas remain unaffected
version_boundary: hazard system enabled for Gnomprona at audited revisions
evidence_basis: [opentibiabr/canary#3549, Otheryn hazard_primal.lua]
conflicts: []
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | exact source reproduction and guard |
| CrystalServer | pinned | related hazard implementation | exact tagging parity pending |
| `blakinio/canary` | pinned | inherited hazard family | likely affected |
| Otheryn | pinned | exact onSpawn/death gate exists; whether `HazardMonster.onSpawn` sets the tag for normal spawns requires execution | target path affected/inconclusive mechanism |
| OTClient | pinned | observes effects only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: ordinary monster spawn in hazard zone -> hazard tag/modifiers -> death pod/patriarch probabilities
preconditions:
  - isolated hazard zone with deterministic RNG and player hazard levels 0/1/12
steps:
  - spawn ordinary, scripted Primal Menace and reward-boss controls inside/outside zone
  - record `monster:hazard()`, combat modifiers and registered death event
  - force probability thresholds and kill each monster
  - verify exclusion rectangles and hazard-disabled configuration
expected_observations:
  - eligible ordinary monsters are tagged and mechanics scale with points; controls remain excluded
artifacts: [hazard-spawn-matrix.jsonl, combat-modifiers.json, death-rewards.jsonl]
cleanup: [discard monsters/player]
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
static_conclusion: TARGET_AFFECTED
runtime_conclusion: PENDING
owner_action: OPEN_FIX_PROGRAM
confidence: high
rationale: Otheryn contains the exact death guard and zone-spawn hook implicated by a detailed cross-version reproduction; deterministic tag and probability tests can isolate the missing assignment
```

## Drift and unresolved questions

- Determine whether the tag omission is in `HazardMonster.onSpawn`, spawn ordering or monster-type eligibility.
- Product fixes made by this audit: **none**.
