# Dossier — `opentibiabr/canary#3875`

## Identity

```yaml
canonical_key: opentibiabr/canary#3875
predecessor_row: 19
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: pale-worm-encounter
research_status: COMPLETE
```

## Source claim

The Pale Worm encounter lacks the Greed/Hunger Worm transition, second-stage Weak Spot, Hex damage-over-time mechanic and lamp mitigation described by quest guides.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: the encounter progresses through its add-driven phase transition, exposes a killable Weak Spot, applies the intended Hex effect and lets the quest lamp mitigate the defined damage while preserving completion/reward rules
version_boundary: Feaster of Souls/Pale Worm encounter at the audited datapack generation
evidence_basis: [opentibiabr/canary#3875]
conflicts:
  - source cites unspecified guides and gives no authoritative timing, counters, damage values or lamp formula
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reports encounter materially incomplete |
| CrystalServer | pinned | related Feaster content lineage; exact mechanics not established |
| `blakinio/canary` | pinned | inherited encounter content | potentially affected |
| Otheryn | pinned | bounded symbol search did not locate the named phase/add/Weak Spot mechanics, supporting an incomplete-path hypothesis but not exact behavior | potentially affected |
| OTClient | pinned | observes creatures/effects only | no direct fix target |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: clean Pale Worm encounter -> add spawns/phase state/Hex/lamp input -> boss completion and rewards
preconditions:
  - isolated party and resettable encounter
  - lamp item and known quest storages
steps:
  - run without lamp and record every spawn, state transition, damage source and completion condition
  - repeat with lamp use at each plausible phase
  - kill Greed/Hunger adds in controlled orders and test Weak Spot availability
  - compare wipe/reset and repeated-entry behavior
expected_observations:
  - named phases and mechanics occur exactly once with deterministic transitions and no shortcut to final kill
artifacts: [pale-worm-timeline.jsonl, creature-spawns.jsonl, combat-effects.jsonl, quest-state.json]
cleanup: [reset encounter and discard party state]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: exact numeric truth values require a primary reference before implementation; structural reproduction is feasible
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
rationale: the source identifies a coherent missing-mechanics set and target search did not locate it, but authoritative phase timings and formulas are absent
```

## Drift and unresolved questions

- Obtain a versioned official/reference encounter trace before defining numeric mechanics.
- Product fixes made by this audit: **none**.
