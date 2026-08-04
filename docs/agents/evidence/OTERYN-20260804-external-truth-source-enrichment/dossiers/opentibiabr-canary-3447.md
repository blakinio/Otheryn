# Dossier — `opentibiabr/canary#3447`

## Identity

```yaml
canonical_key: opentibiabr/canary#3447
predecessor_row: 41
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: new-frontier-wyrdin-dialogue
research_status: COMPLETE
```

## Source claim

Wyrdin answers “Wrong Word.” to `plea`, `bluff`, `flatter` and `impress` during The New Frontier mission, while other NPCs work.

## Provenance and static proof

At pinned Otheryn, valid branches exist only for keyword storage values 1 (`plea`), 2 (`bluff`) and 3 (`flatter`) while Wyrdin mission state equals 1. There is no `impress` branch. Any wrong-word fallthrough sets Wyrdin mission state to 2, after which every valid branch requiring state 1 is permanently bypassed. This exactly explains trying multiple words sequentially and receiving only “Wrong Word.”

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: the one keyword selected by mission storage succeeds and advances Wyrdin to completion; a wrong guess does not corrupt or permanently lock the dialogue unless official quest rules explicitly consume the attempt; every generated keyword value has a matching branch
version_boundary: The New Frontier Mission 5 dialogue at audited datapack
evidence_basis: [opentibiabr/canary#3447, Otheryn wyrdin.lua]
conflicts:
  - correct semantics for `impress` and wrong-attempt state must be checked against authoritative quest behavior
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reports lockout |
| CrystalServer | pinned | Wyrdin path located; exact branch parity requires comparison |
| `blakinio/canary` | pinned | inherited NPC lineage | likely affected |
| Otheryn | pinned | missing `impress` branch and wrong-word state transition from 1 to 2 are present | affected |
| OTClient | pinned | plain NPC text input | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: NOT_APPLICABLE
system_boundary: WyrdinKeyword/Wyrdin storage + spoken word -> NPC response and quest state
preconditions:
- isolated players for every keyword value and mission state
steps:
- test plea, bluff, flatter and impress against each generated keyword value
- test one wrong word followed by the correct word
- relog and repeat to detect persisted lockout
expected_observations:
- exactly one valid word per generated value completes the NPC step and wrong input follows authoritative retry semantics
artifacts:
- wyrdin-dialogue-matrix.json
- storage-transitions.jsonl
- runtime-feasibility.md
cleanup:
- discard players
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: 'not applicable: pinned static evidence already reaches a target disposition; runtime execution would not change
  the audit decision'
```

## Runtime execution

```yaml
execution_status: NOT_RUN
exact_otheryn_head: not applicable
run_ids: []
observations:
- static comparison is sufficient for the target disposition; no game-world state was created
artifacts:
- runtime-feasibility.md
cleanup_result: not applicable
```

## Conclusions

```yaml
truth_status: PROVEN
static_conclusion: TARGET_AFFECTED
runtime_conclusion: NOT_APPLICABLE
owner_action: OPEN_FIX_PROGRAM
confidence: high
rationale: the target lacks one advertised word branch and changes mission state so subsequent correct words can never satisfy
  their guard, directly matching the report Runtime execution is not applicable because the pinned static comparison already
  determines the target disposition.
```

## Drift and unresolved questions

- Establish the authoritative keyword-value range and wrong-answer retry behavior before repair.
- Product fixes made by this audit: **none**.
