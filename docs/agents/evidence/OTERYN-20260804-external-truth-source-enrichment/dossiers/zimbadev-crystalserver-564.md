# Dossier — `zimbadev/crystalserver#564`

## Identity

```yaml
canonical_key: zimbadev/crystalserver#564
predecessor_row: 101
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: children-revolution-grease-oil
research_status: COMPLETE
```

## Source claim

Mission 4 grease oil does nothing on the levers. Merged Crystal PR `#656` identifies the cause: obtaining oil early can advance/overwrite the global Questline, so the action's `Questline==13` guard rejects a legitimately prepared player; it switches the gate to `Mission04==3`.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: using the oil on the intended action-ID lever succeeds whenever Mission04 is at the oil stage, independently of unrelated/global Questline drift, then atomically consumes oil and advances Mission04/Questline once
version_boundary: Children of the Revolution Mission 4 at audited revisions
evidence_basis: [zimbadev/crystalserver#564, merged zimbadev/crystalserver#656]
conflicts:
  - PR changes the target guard to `if not target.actionid == 8013`, whose Lua precedence appears to disable the action-ID rejection; this candidate line requires independent correction/validation
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | corresponding quest path must be checked for mission-specific gating |
| CrystalServer | pinned | merged PR supplies accepted storage fix but includes a questionable action-ID expression |
| `blakinio/canary` | pinned | inherited quest lineage | potentially affected |
| Otheryn | pinned | bounded search did not resolve the exact action file; direct path/storage comparison with PR #656 is required | static inconclusive |
| OTClient | pinned | standard use-with action | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: Mission04/Questline/action-ID/oil state -> action validation -> item consumption and storage transition
preconditions:
- players with canonical and early-oil divergent storage combinations
steps:
- use oil on action ID 8013 for every relevant Mission04/Questline pair
- repeat on wrong action IDs and after completion
- record item consumption, effects and both storage writes
- test replay/relog/restart idempotence
expected_observations:
- Mission04 stage controls eligibility; only correct target works; valid use advances once without loss on rejection
artifacts:
- grease-oil-storage-matrix.json
- action-results.jsonl
- runtime-feasibility.md
cleanup:
- discard players/items
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
truth_status: PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: NOT_RUN_INFEASIBLE
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: 'an accepted donor fix proves the global-versus-mission storage mismatch, but its target-ID expression must not
  be copied without a dedicated negative-control test Runtime execution is infrastructure-blocked: the repository has no deterministic
  game/client driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Verify Otheryn's exact action path and preserve a correct `target.actionid ~= 8013` guard.
- Product fixes made by this audit: **none**.
