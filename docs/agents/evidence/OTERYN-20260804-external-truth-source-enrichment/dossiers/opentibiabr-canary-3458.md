# Dossier — `opentibiabr/canary#3458`

## Identity

```yaml
canonical_key: opentibiabr/canary#3458
predecessor_row: 39
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: soulpit-wave-clear
research_status: COMPLETE
```

## Source claim

A player summon or convinced creature remains counted as an arena monster, preventing Soulpit from recognizing a cleared wave and advancing until the player is removed.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: wave completion counts only hostile encounter-owned creatures; player summons, convinced creatures, familiars and other non-hostile actors do not block advancement, while surviving hostile summons still do
version_boundary: Soulpit encounter framework at audited revisions
evidence_basis: [opentibiabr/canary#3458]
conflicts: []
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | exact actor-classification failure reported |
| CrystalServer | pinned | related Soulpit/arena lineage | potentially affected |
| `blakinio/canary` | pinned | inherited encounter logic | likely affected |
| Otheryn | pinned | arena creature counting must distinguish ownership/hostility; runtime path not statically assigned | inconclusive |
| OTClient | pinned | summon input/visualization only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: arena actor set -> wave-clear predicate -> next-wave transition
preconditions:
- isolated Soulpit fixture with deterministic wave
steps:
- clear wave with no summon
- repeat with player summon, convinced creature, familiar, party summon and hostile encounter summon
- record actor ownership/type and wave predicate each tick
- verify exit/reset cleanup
expected_observations:
- only living hostile encounter-owned actors block advancement
artifacts:
- soulpit-actor-matrix.json
- wave-transitions.jsonl
- runtime-feasibility.md
cleanup:
- reset arena and discard actors
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
rationale: 'the source defines a deterministic actor-classification defect; execution will identify the exact arena-count
  predicate before repair Runtime execution is infrastructure-blocked: the repository has no deterministic game/client driver
  and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Define whether charmed/converted enemies should be ignored immediately or only after ownership changes fully propagate.
- Product fixes made by this audit: **none**.
