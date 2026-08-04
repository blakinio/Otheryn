# Dossier — `opentibiabr/canary#3479`

## Identity

```yaml
canonical_key: opentibiabr/canary#3479
predecessor_row: 36
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: brain-head-encounter-entry
research_status: COMPLETE
```

## Source claim

Entering from `(31974,32326,10)` teleports players into an empty Brain Head arena and still applies the ten-hour cooldown. Discussion confirms GOD characters are intentionally ignored by `encounter` through `IgnoredByMonsters`, while the reporter states ordinary characters fail on two servers; another tester's ordinary players spawned the boss successfully.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: an eligible ordinary player crossing any valid entry tile starts exactly one Brain Head encounter with boss/minions; ignored staff characters do not start it; cooldown is committed only after successful encounter creation or is refunded on startup failure
version_boundary: Canary 3.1.2 / client 13.40-era encounter framework and current descendants
evidence_basis: [opentibiabr/canary#3479, issue discussion]
conflicts:
  - ordinary-player results differ between clean/test installations, indicating configuration, quest state or persisted encounter drift rather than a universal entry-tile bug
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | mixed ordinary-player reproduction; intentional GOD exclusion established |
| CrystalServer | pinned | encounter lineage | configuration/state parity unknown |
| `blakinio/canary` | pinned | inherited encounter framework | potentially affected |
| Otheryn | pinned | encounter start/cooldown/eligibility path requires state matrix; no universal static defect proven | static inconclusive |
| OTClient | pinned | entry/movement only | irrelevant to spawn authority |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: role/quest/cooldown/freequest state + entry tile -> encounter creation -> boss/minions and cooldown
preconditions:
  - clean isolated world with ordinary and GOD characters
steps:
  - test every valid east entry tile for ordinary eligible player
  - repeat with GOD/IgnoredByMonsters, missing quest, active cooldown and freequest variants
  - inject encounter creation failure and verify cooldown rollback
  - record encounter registry before/after exit/reset
expected_observations:
  - ordinary eligible entry spawns full encounter; staff does not; failed start never consumes ten-hour access
artifacts: [brain-head-entry-matrix.json, encounter-registry.jsonl, cooldown-state.json]
cleanup: [reset encounter and discard characters]
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
truth_status: PARTIALLY_PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: PENDING
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: the source reveals an important role distinction and cooldown-loss failure, but clean ordinary players produced contradictory results; a full eligibility/configuration matrix is required
```

## Drift and unresolved questions

- Check whether `freequests.lua`, quest storage or stale encounter registry differs on failing servers.
- Product fixes made by this audit: **none**.
