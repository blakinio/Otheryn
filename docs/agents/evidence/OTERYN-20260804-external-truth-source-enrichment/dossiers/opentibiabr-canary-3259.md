# Dossier — `opentibiabr/canary#3259`

## Identity

```yaml
canonical_key: opentibiabr/canary#3259
predecessor_row: 57
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: secret-library-scorpion-forcefield
research_status: COMPLETE
```

## Source claim

The Secret Library cannot be completed because a magic forcefield, client item `1949`, action ID `4930`, at `(32963,32312,8)` blocks entry to the Furious Scorpion area even when nobody entered previously. Later screenshot-only comments report additional map/content anomalies but do not identify them textually.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: an eligible player at the correct Secret Library state can pass or deactivate the forcefield at 32963,32312,8, enter the Furious Scorpion sequence once, and complete/reset it without stale occupancy locks
version_boundary: The Secret Library/Furious Scorpion map and action generation at audited revisions
evidence_basis: [opentibiabr/canary#3259]
conflicts:
  - later screenshot-only issues are not sufficiently identified and are excluded from this canonical claim
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | exact tile/item/action blocker reported |
| CrystalServer | pinned | corresponding quest/map lineage | inconclusive |
| `blakinio/canary` | pinned | inherited map/action | potentially affected |
| Otheryn | pinned | exact map tile/action/storage/arena occupancy must be dumped; source gives deterministic coordinate | static inconclusive |
| OTClient | pinned | movement/use observation only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: quest/arena state + forcefield tile -> movement/action transition -> encounter completion/reset
preconditions: [isolated players before/at/after the Scorpion mission]
steps:
  - dump full tile stack and action/unique IDs at 32963,32312,8
  - attempt passage for every relevant quest state with empty and occupied arena controls
  - complete, wipe and time out the encounter and retest entry
  - inspect stale event/occupancy storage after restart
expected_observations:
  - eligible empty-arena entry opens/passes once and all failure/completion paths restore a valid state
artifacts: [scorpion-tile-dump.json, entry-matrix.json, arena-state.jsonl]
cleanup: [reset arena and discard players]
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
rationale: exact coordinate, item and action ID make the primary blocker deterministic; map/action/storage tracing is required before repair
```

## Drift and unresolved questions

- Treat unlabelled screenshot comments as separate evidence only after their coordinates/IDs are recovered.
- Product fixes made by this audit: **none**.
