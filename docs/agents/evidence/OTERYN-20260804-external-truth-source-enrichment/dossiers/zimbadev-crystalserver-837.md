# Dossier — `zimbadev/crystalserver#837`

## Identity

```yaml
canonical_key: zimbadev/crystalserver#837
predecessor_row: 96
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: freequests-access-storage-values
research_status: COMPLETE
```

## Source claim

Freequests reports access granted, but NPCs, teleports and doors still reject players. The supplied White Raven example is internally inconsistent: freequests sets `Passage=1`, while Dalbrect's travel branch requires `Passage>=2`.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: each freequest grant writes the terminal access value expected by every corresponding NPC, teleport and door predicate; Quest Log visibility and functional access are validated together, not inferred from one storage
version_boundary: audited freequests registry and quest access consumers
evidence_basis: [zimbadev/crystalserver#837, exact White Raven storage/predicate example]
conflicts:
  - source lists several additional quests without their exact storage predicates
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | related freequests loader/content; issue #3478 shows configuration sensitivity |
| CrystalServer | pinned | exact `Passage=1` versus consumer `>=2` mismatch reported |
| `blakinio/canary` | pinned | inherited freequest/access lineage | potentially affected |
| Otheryn | pinned | bounded search did not resolve the exact literal pair; complete producer/consumer storage graph is required | static inconclusive |
| OTClient | pinned | receives NPC/teleport/Quest Log results only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: freequest registry row -> storage writes -> all NPC/teleport/door consumer predicates
preconditions:
  - generated graph of freequest storage/value producers and access consumers
steps:
  - apply each freequest row to a clean player
  - exercise every linked NPC, teleport and door and record predicate/value
  - prioritize White Raven Passage 1/2 and every source-listed access
  - relog/restart and test migrated players
expected_observations:
  - every advertised grant satisfies all intended consumers without overgranting later mission rewards
artifacts: [freequest-consumer-graph.json, access-matrix.jsonl, storage-values.json]
cleanup: [discard players/database]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: none after graph generation
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
rationale: the source proves at least one producer/consumer value mismatch; target-wide graph validation is safer than patching one storage blindly
```

## Drift and unresolved questions

- Reconcile with Canary issue `#3478`: stale duplicate files and incomplete terminal values are separate failure classes.
- Product fixes made by this audit: **none**.
