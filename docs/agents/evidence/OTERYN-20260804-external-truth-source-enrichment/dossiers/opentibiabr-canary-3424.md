# Dossier — `opentibiabr/canary#3424`

## Identity

```yaml
canonical_key: opentibiabr/canary#3424
predecessor_row: 47
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: soul-war-taint-lifecycle
research_status: COMPLETE
```

## Source claim

Flickering Soul removes current taints, but subsequent Soul War boss kills no longer grant taints, indicating that removal clears or advances a persistent eligibility state incorrectly.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: NPC removal clears active taint effects/storage without permanently disabling future boss-earned taints; each qualifying boss kill applies the correct next taint exactly once and persists across relog
version_boundary: Soul War taint/NPC lifecycle at audited revisions
evidence_basis: [opentibiabr/canary#3424]
conflicts: []
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reports persistent eligibility corruption |
| CrystalServer | pinned | same `soul_war_mechanics.lua` family | potentially affected |
| `blakinio/canary` | pinned | inherited lifecycle | likely affected |
| Otheryn | pinned | Soul War mechanics/NPC/storage paths exist; exact remove-versus-progress storage writes require trace | static inconclusive |
| OTClient | pinned | displays effects only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: boss completion + NPC taint removal -> active/progress storages -> future boss taint
preconditions:
- isolated players at every taint count/state
steps:
- earn one taint, remove it, relog and kill each eligible boss
- repeat after multiple taints and completed quest variants
- record active taints, progression counters and boss completion storages before/after each transaction
- test duplicate boss kills and NPC dialogue cancellation
expected_observations:
- removal affects only active taints and future qualifying kills grant the correct next state exactly once
artifacts:
- taint-state-matrix.json
- storage-transitions.jsonl
- runtime-feasibility.md
cleanup:
- discard players
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
truth_status: PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: NOT_RUN_INFEASIBLE
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: 'the report defines a precise persistence sequence, but the responsible active/progress storage cannot be selected
  without tracing NPC and boss writes Runtime execution is infrastructure-blocked: the repository has no deterministic game/client
  driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Separate reversible active-taint state from permanent boss/quest progression in the repair design.
- Product fixes made by this audit: **none**.
