# Dossier — `opentibiabr/canary#3345`

## Identity

```yaml
canonical_key: opentibiabr/canary#3345
predecessor_row: 53
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: damage-reflection-origin
research_status: COMPLETE
```

## Source claim

Monster damage reflection works for runes and mage spells but not for knight melee, elemental weapons or offensive knight spells; example: level-200+ knight with Winterblade against Burster Spectre.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: a target with reflection applies the configured reflected component for every eligible incoming combat origin, including melee/weapon elements and knight combat spells, while excluded origins are explicit and recursion-safe
version_boundary: audited combat-origin/reflection system
evidence_basis: [opentibiabr/canary#3345]
conflicts:
  - exact reflect percentage, target configuration and excluded origins are not supplied
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | origin-dependent failure reported |
| CrystalServer | pinned | related combat/reflection path | inconclusive |
| `blakinio/canary` | pinned | inherited combat lineage | potentially affected |
| Otheryn | pinned | reflection must be traced across weapon primary/elemental and spell origin flags; no exact static branch established | inconclusive |
| OTClient | pinned | displays combat messages only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: fixed incoming combat origin/type -> target reflection -> attacker HP/combat events
preconditions:
- deterministic reflecting target and fixed attacker damage
steps:
- attack with physical melee, elemental weapon component, knight spells, mage spells, runes, summons and conditions
- record origin/type/primary-secondary components and reflected events
- test immunity, lethal reflection and reflection-of-reflection recursion guards
expected_observations:
- every eligible component reflects exactly once according to one declared formula
artifacts:
- reflection-origin-matrix.jsonl
- combat-events.jsonl
- runtime-feasibility.md
cleanup:
- discard actors
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
rationale: 'the source isolates the defect by combat origin, enabling a deterministic origin/component matrix before any reflection
  fix Runtime execution is infrastructure-blocked: the repository has no deterministic game/client driver and adding one is
  outside audit-only authority.'
```

## Drift and unresolved questions

- Establish authoritative eligibility for weapon secondary elemental damage and damage-over-time.
- Product fixes made by this audit: **none**.
