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
plan_status: READY
system_boundary: arena actor set -> wave-clear predicate -> next-wave transition
preconditions: [isolated Soulpit fixture with deterministic wave]
steps:
  - clear wave with no summon
  - repeat with player summon, convinced creature, familiar, party summon and hostile encounter summon
  - record actor ownership/type and wave predicate each tick
  - verify exit/reset cleanup
expected_observations:
  - only living hostile encounter-owned actors block advancement
artifacts: [soulpit-actor-matrix.json, wave-transitions.jsonl]
cleanup: [reset arena and discard actors]
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
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: PENDING
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: the source defines a deterministic actor-classification defect; execution will identify the exact arena-count predicate before repair
```

## Drift and unresolved questions

- Define whether charmed/converted enemies should be ignored immediately or only after ownership changes fully propagate.
- Product fixes made by this audit: **none**.
