# Dossier — `opentibiabr/canary#2639`

## Identity

```yaml
canonical_key: opentibiabr/canary#2639
predecessor_row: 63
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: deferred-liquid-use
research_status: COMPLETE
```

## Source claim

Using a liquid container from outside use range queues movement but moves/throws the liquid item to the player's original square; reference behavior walks into range and then consumes/uses the liquid at the intended target.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: deferred use preserves source item identity/location and intended target while the player walks into range; after arrival it revalidates and performs the liquid action without moving the container to the stale origin tile
version_boundary: audited use-with/autowalk and fluid-container system
evidence_basis: [opentibiabr/canary#2639, supplied Canary/reference videos]
conflicts: []
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source shows divergence from reference behavior |
| CrystalServer | pinned | related deferred-use path | inconclusive |
| `blakinio/canary` | pinned | inherited source | potentially affected |
| Otheryn | pinned | autowalk retry must retain source/target positions and stack/item identity; runtime required | static inconclusive |
| OTClient | pinned | sends initial use target and receives autowalk/item updates | protocol-critical observer |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: out-of-range fluid use request -> autowalk/revalidation -> fluid consumption/target effect and item position
preconditions: [representative fluid containers and valid self/creature/tile targets]
steps:
  - use from one to several squares away with clear and interrupted paths
  - move/replace source or target during autowalk and test cancellation
  - record source item UID/position, target and resulting fluid/item state
  - compare non-fluid use-with and throwable item controls
expected_observations:
  - source container never moves to stale player origin and action executes only after valid in-range revalidation
artifacts: [deferred-use-matrix.jsonl, movement-use-events.jsonl, inventory-tile-state.json]
cleanup: [restore/discard items and actors]
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
rationale: paired source/reference videos establish the intended deferred-use semantics; item/target identity tracing can localize the stale-position bug
```

## Drift and unresolved questions

- Ensure retry is race-safe when source/target changes during autowalk.
- Product fixes made by this audit: **none**.
