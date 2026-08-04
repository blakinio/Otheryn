# Dossier — `opentibiabr/canary#2553`

## Identity

```yaml
canonical_key: opentibiabr/canary#2553
predecessor_row: 64
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: gnomprona-death-rewards
research_status: COMPLETE
```

## Source claim

Eligible Garden monster kills no longer spawn Primal Pods/Fungisaurs or eventually a Plunder Patriarch. This is the player-visible consequence of the hazard tagging/death-event path analyzed in `#3549`.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: eligible hazard-zone kills advance deterministic/probabilistic reward counters, spawn at most the configured Primal Pods and Plunder Patriarch, transform pods into Fungisaurs, and reset/cool down without duplicate rewards
version_boundary: Gnomprona hazard system at audited revisions
evidence_basis: [opentibiabr/canary#2553, opentibiabr/canary#3549]
conflicts:
  - source does not provide exact kill thresholds/probabilities; #3549 exposes the stronger tag-gate mechanism
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | reward spawn failure reported |
| CrystalServer | pinned | related hazard/reward lineage | inconclusive |
| `blakinio/canary` | pinned | inherited system | likely affected |
| Otheryn | pinned | exact death reward guard depends on `monster:hazard()` as documented in #3549 | target affected path |
| OTClient | pinned | observes spawns/effects only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: NOT_APPLICABLE
system_boundary: tagged eligible kills + controlled RNG/counters -> pod/fungisaur/patriarch spawns and cooldown state
preconditions:
- isolated Garden zone
- deterministic RNG
- hazard levels 0/1/12
steps:
- reuse
- record spawn count/location, pod transform, patriarch uniqueness and reset/cooldown
- test excluded areas, untagged monsters, simultaneous kills and restart persistence
expected_observations:
- eligible tagged kills trigger bounded rewards according to configured rules; no duplicates or permanent disablement
artifacts:
- gnomprona-reward-events.jsonl
- counters.json
- spawn-state.jsonl
- runtime-feasibility.md
cleanup:
- remove rewards and discard player/monsters
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
rationale: the target's hazard-dependent death gate directly controls the rewards named here; one deterministic hazard/reward
  run can prove both canonical items without conflating their decisions Runtime execution is not applicable because the pinned
  static comparison already determines the target disposition.
```

## Drift and unresolved questions

- Source exact official thresholds/probabilities before implementation.
- Product fixes made by this audit: **none**.
