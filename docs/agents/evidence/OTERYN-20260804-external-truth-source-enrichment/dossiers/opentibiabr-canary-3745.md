# Dossier — `opentibiabr/canary#3745`

## Identity

```yaml
canonical_key: opentibiabr/canary#3745
predecessor_row: 23
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: quick-access-quiver-swap
research_status: COMPLETE
```

## Source claim

With a bow equipped, using a quick-access slot configured to equip another full quiver is rejected; removing the bow allows the swap. On the reference game, quick-access “equip” swaps quivers while the bow remains equipped and “use” opens the quiver.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: quick-access equip atomically replaces the shield-slot quiver without requiring bow removal; quick-access use opens the selected quiver and does not equip it
version_boundary: modern inventory/quiver protocol supporting quick-access action modes
evidence_basis: [opentibiabr/canary#3745]
conflicts: []
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reports affected equipment path |
| CrystalServer | pinned | equipment lineage present; exact swap semantics inconclusive |
| `blakinio/canary` | pinned | related equip/move path; inconclusive |
| Otheryn | pinned | bow, quiver, shield-slot and quick-access paths exist; no static proof that replacement transaction handles occupied quiver correctly |
| OTClient | pinned | must distinguish quick-access use versus equip and encode target item/action mode; relevant end-to-end |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: quick-access use/equip input -> server inventory transaction -> slot/container/client state
preconditions:
  - paladin with bow equipped and two non-empty quivers
steps:
  - bind quiver B as equip and invoke while quiver A and bow are equipped
  - bind quiver B as use and invoke under the same state
  - repeat with empty quivers, no bow and insufficient free inventory space controls
  - record return message, slot contents, open container and item conservation
expected_observations:
  - equip swaps A/B atomically; use opens B; bow remains equipped
artifacts: [quiver-swap-matrix.json, inventory-packets.jsonl, server.log]
cleanup: [discard player state]
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
rationale: the source defines observable reference behavior and a simple state-dependent reproduction, but the target failure cannot be assigned to quick-access decoding, equip validation or container movement without executing the transaction
```

## Drift and unresolved questions

- Capture the exact rejection message/return value to identify the failing validation layer.
- Product fixes made by this audit: **none**.
