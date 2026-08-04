# Dossier — `opentibiabr/canary#3605`

## Identity

```yaml
canonical_key: opentibiabr/canary#3605
predecessor_row: 27
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: cults-misguided-encounter
research_status: COMPLETE
```

## Source claim

The Misguided mission has three coupled failures: the amulet cannot be charged normally, live map switching corrupts the map/client, and creature deaths are not counted so the boss barrier cannot be crossed.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: the quest amulet charges through its intended action, the illusion/reality map swaps remain coherent for occupied clients, and qualifying creature deaths advance the barrier counter exactly once until boss access opens
version_boundary: Cults of Tibia Misguided implementation in the audited global datapack
evidence_basis:
  - opentibiabr/canary#3605
  - zimbadev/crystalserver#852 exact map-swap reproduction
  - zimbadev/crystalserver#785 cache-clear hypothesis
conflicts:
  - source combines three mechanisms and supplies only a video, so each must be isolated independently
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | affected claim; same Misguided action family |
| CrystalServer | pinned | issue #852 independently reproduces occupied map-swap crash; PR #785 proposes incomplete cache clearing |
| `blakinio/canary` | pinned | inherited quest/map family | potentially affected |
| Otheryn | pinned | exact `actions_misguided.lua` live `Game.loadMap` sequence is present; amulet/death-counter paths require runtime isolation | target path present |
| OTClient | pinned | required to observe map-state coherence/crash, not amulet or server counter truth | relevant end-to-end |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: amulet action + creature kills + live map swaps -> quest storage/map/client/barrier result
preconditions:
- isolated player at exact Misguided mission state
- uncharged and charged amulet fixtures
- known qualifying creature set and maintained OTClient
steps:
- test amulet charge action with valid and invalid targets/storages
- trigger one illusion/reality swap with player outside and inside the replaced area
- kill qualifying creatures one at a time and record counter, duplicate/party/summon cases
- verify barrier/teleport before threshold and after exact threshold
- correlate any client failure with map packets and server tile/cache state
expected_observations:
- one valid charge transition, coherent map state, exact-once death counting and threshold-gated boss access
artifacts:
- misguided-amulet.jsonl
- kill-counter.jsonl
- map-packets.jsonl
- barrier-results.json
- client-crash
- runtime-feasibility.md
cleanup:
- discard quest player/map state
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
truth_status: PARTIALLY_PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: NOT_RUN_INFEASIBLE
owner_action: RESEARCH_REQUIRED
confidence: medium-high
rationale: 'Otheryn contains the exact live-map quest path independently implicated by Crystal issue Runtime execution is
  infrastructure-blocked: the repository has no deterministic game/client driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Reuse the map-swap artifacts from dossiers `zimbadev-crystalserver-785` and `-852` rather than run duplicate uncontrolled tests.
- Product fixes made by this audit: **none**.
