# Dossier — `opentibiabr/canary#3428`

## Identity

```yaml
canonical_key: opentibiabr/canary#3428
predecessor_row: 44
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: house-bed-pair-count
research_status: COMPLETE
```

## Source claim

Only one half of a two-tile bed can be unwrapped. Discussion reports a clean updated server works and the reporter fixes the affected houses by changing a house XML value from `1` to `2`, indicating stale/incorrect map house metadata rather than a universal bed engine defect.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: a two-tile bed placed in one house is recognized as a complete pair and both wrapped components can be unwrapped/linked according to house ownership and placement rules; house metadata describes the correct number/extent of bed tiles
version_boundary: audited houses XML/map and bed transform system
evidence_basis: [opentibiabr/canary#3428, issue discussion]
conflicts:
  - clean independent installation did not reproduce the failure
  - the exact house XML attribute and affected house IDs are not named in text
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | clean install works; environment/map metadata can fail |
| CrystalServer | pinned | separate house/map data | inconclusive |
| `blakinio/canary` | pinned | inherited world data | exact affected house inventory required |
| Otheryn | pinned | no universal source-path defect proven; all house/bed metadata must be validated as pairs | static inconclusive |
| OTClient | pinned | sends unwrap/use actions only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: house XML/map bed metadata + wrapped pair -> unwrap/link state
preconditions:
- inventory of every two-tile bed and house membership in target map
steps:
- validate both bed tiles share one house and compatible partner metadata
- unwrap each half from every orientation using owner/non-owner controls
- save/restart and verify linked bed persistence
- compare houses with suspicious one-versus-two metadata values
expected_observations:
- complete bed pairs unwrap and persist symmetrically; invalid map metadata is reported by house ID
artifacts:
- house-bed-inventory.json
- unwrap-matrix.jsonl
- persistence-results.json
- runtime-feasibility.md
cleanup:
- restore/discard house fixtures
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
confidence: high
rationale: 'discussion localizes the symptom to house metadata and contradicts a universal engine defect; target-wide pair
  validation is required to find any affected houses Runtime execution is infrastructure-blocked: the repository has no deterministic
  game/client driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Identify the exact house XML field referenced as `1`/`2` before any data change.
- Product fixes made by this audit: **none**.
