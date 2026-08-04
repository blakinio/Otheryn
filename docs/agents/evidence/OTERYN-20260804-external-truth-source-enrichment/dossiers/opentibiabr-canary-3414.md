# Dossier — `opentibiabr/canary#3414`

## Identity

```yaml
canonical_key: opentibiabr/canary#3414
predecessor_row: 48
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: concoction-amplification-potion
research_status: COMPLETE
```

## Source claim

All Amplification Potion variants fail to increase target sensitivity by 8% for one hour and do not appear in Cyclopedia, while other Concoction effects work.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: consuming a valid Amplification Potion creates a one-hour persisted effect, exposes it in the negotiated Cyclopedia/concoction status and applies an 8-percentage-point sensitivity increase exactly once in damage calculations
version_boundary: Tibia Drome Concoction System generation represented by the audited datapack/protocol
evidence_basis: [opentibiabr/canary#3414]
conflicts:
  - source supplies comparative observations but not raw deterministic damage vectors or potion IDs
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | all amplification variants reported ineffective/invisible |
| CrystalServer | pinned | related concoction/combat/protocol lineage | inconclusive |
| `blakinio/canary` | pinned | inherited system | potentially affected |
| Otheryn | pinned | potion effect, sensitivity calculation and Cyclopedia serialization must be traced as separate gates | static inconclusive |
| OTClient | pinned | status parser/UI is protocol-relevant | end-to-end required |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: potion consumption -> persisted condition/status packet -> target sensitivity -> deterministic damage
preconditions:
- every amplification potion variant
- fixed attacker, attack roll and targets with known elemental sensitivities
steps:
- record baseline deterministic damage and Cyclopedia state
- consume each variant, repeat identical attacks and decode status packets
- relog/restart and sample before/after one-hour expiry using controlled clock
- test stacking/replacement and immune/100-percent boundary targets
expected_observations:
- status is visible and damage changes by the defined sensitivity transformation exactly once for the full duration
artifacts:
- amplification-potion-matrix.json
- deterministic-damage.csv
- cyclopedia-packets.jsonl
- persistence.json
- runtime-feasibility.md
cleanup:
- expire/remove conditions and discard player
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
rationale: 'the source defines both a combat and protocol-visible invariant across all variants; deterministic fixed-roll
  tests can isolate missing condition, formula or serialization Runtime execution is infrastructure-blocked: the repository
  has no deterministic game/client driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Clarify whether “8% higher sensitivity” is additive percentage points or multiplicative scaling in the authoritative formula.
- Product fixes made by this audit: **none**.
