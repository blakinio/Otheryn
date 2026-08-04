# Dossier — `opentibiabr/canary#3485`

## Identity

```yaml
canonical_key: opentibiabr/canary#3485
predecessor_row: 35
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: hireling-customization
research_status: COMPLETE
```

## Source claim

Using Customize on a hireling opens the player's outfit window instead of a hireling-specific editor. Discussion confirms the official-like interaction is missing and points to closed, unmerged PR `#3700` as a candidate implementation.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: customize interaction identifies the selected owned hireling, opens a hireling-specific outfit/color UI, validates house/ownership context and applies changes only to the hireling; player outfit remains unchanged
version_boundary: protocol generation exposing hireling context actions/customize
evidence_basis: [opentibiabr/canary#3485, opentibiabr/canary#3700]
conflicts:
  - candidate PR is unmerged, broad and 51 commits, so it is evidence of intent rather than accepted implementation
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | missing feature confirmed by discussion |
| CrystalServer | pinned | hireling/protocol lineage | exact support inconclusive |
| `blakinio/canary` | pinned | inherited path | potentially affected |
| Otheryn | pinned | context-action/outfit path must distinguish player versus hireling target; no accepted donor patch is present | potentially affected |
| OTClient | pinned | must encode target hireling/context and render the correct outfit editor | protocol-critical |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: hireling context action -> server target/ownership validation -> customization packet/UI -> persisted hireling outfit
preconditions:
  - owned house/hireling and non-owner control
steps:
  - customize hireling and player separately and capture target identifiers/packets
  - change colors/outfit, close/reopen and relog
  - test outside house, non-owner and multiple-hireling controls
expected_observations:
  - only selected owned hireling changes and state persists; player never changes
artifacts: [hireling-customize-packets.jsonl, outfit-state.json, authorization-matrix.json]
cleanup: [restore/discard house and character state]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: none for maintained-client testing; official packet layout must be confirmed before implementation
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
owner_action: OPEN_PROTOCOL_DECISION
confidence: high
rationale: source and discussion establish missing target-specific customization, but the only candidate PR was rejected/unmerged and cannot be migrated wholesale
```

## Drift and unresolved questions

- Determine whether Otheryn's custom protocol profiles already reserve a hireling target field/opcode.
- Product fixes made by this audit: **none**.
