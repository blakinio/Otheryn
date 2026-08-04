# Dossier — `opentibiabr/canary#3724`

## Identity

```yaml
canonical_key: opentibiabr/canary#3724
predecessor_row: 25
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: wheel-gem-persistence
research_status: COMPLETE
```

## Source claim

Equipping/applying a Wheel gem, dismantling a gem, then relogging restores the dismantled gem while the dismantling rewards remain. The issue states the rollback occurs only when another gem is equipped.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: applying/equipping and dismantling gems are persisted atomically; after relog the gem inventory, equipped slots and dismantling rewards reflect exactly one committed transaction with no duplication
version_boundary: Wheel of Destiny gem system at the audited protocol/content generation
evidence_basis:
  - opentibiabr/canary#3724 exact state-dependent reproduction
conflicts: []
```

## Five-repository static comparison

| Repository | Revision | Observed state | Assessment |
|---|---|---|---|
| upstream Canary | pinned | Wheel persistence path exists; source supplies state-dependent failure | affected claim |
| CrystalServer | pinned | related Wheel code/data lineage; persistence parity not established | inconclusive |
| `blakinio/canary` | pinned | related implementation lineage | inconclusive |
| Otheryn | pinned | Wheel/gem and player-save families are present, but bounded symbol search did not prove transaction ordering | static inconclusive |
| OTClient | pinned | supplies equip/apply/dismantle requests and relog observation; server persistence is authoritative | runtime control only |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: gem equip/apply/dismantle requests -> database transaction/save -> relogged gem/reward state
preconditions:
  - isolated player with at least two known gems and deterministic dismantle reward
steps:
  - baseline: dismantle with no equipped gem, logout/relogin and verify conservation
  - defect case: equip/apply gem A, dismantle gem B, logout/relogin through graceful and forced disconnect variants
  - query persisted wheel/gem records before action, after action, after save and after relog
  - repeat with explicit server save and process restart
expected_observations:
  - no gem or reward is duplicated; equipped and owned gem state is identical across memory and database
artifacts:
  - wheel-gem-transactions.jsonl
  - database-snapshots.sql.txt
  - relog-state.json
cleanup:
  - discard isolated player/database
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
confidence: medium-high
rationale: the issue provides a precise duplication sequence, but the target transaction/save ordering was not proven statically; isolated database-backed reproduction is required before assigning a fix path
```

## Drift and unresolved questions

- Determine whether apply persists a stale full gem snapshot that later overwrites dismantle changes during logout save.
- Product fixes made by this audit: **none**.
