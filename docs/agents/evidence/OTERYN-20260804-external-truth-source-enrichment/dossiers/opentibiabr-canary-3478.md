# Dossier — `opentibiabr/canary#3478`

## Identity

```yaml
canonical_key: opentibiabr/canary#3478
predecessor_row: 37
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: freequests-secret-library
research_status: COMPLETE
```

## Source claim

Freequests runs and reports success but The Secret Library does not appear in Quest Log. Independent testing with the posted entries worked; the reporter later found a stale copied `freequests.lua` and also noted that the canonical list lacked the top-level `TheSecretLibrary.Questlog` row they added manually.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: each configured freequest stage is applied once, from the active canonical file, and sets every required top-level and subquest storage so Quest Log visibility matches the configured grant; stale duplicate files are detected or excluded deterministically
version_boundary: audited freequests loader and Secret Library storage schema
evidence_basis: [opentibiabr/canary#3478, issue discussion]
conflicts:
  - clean independent run succeeded, while reporter environment contained a stale file copy
  - missing top-level Questlog entry is a configuration-content question, not proof of a loader defect
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | loader works in clean reproduction; canonical Secret Library grant completeness remains content-specific |
| CrystalServer | pinned | related issue #837 requires separate storage sync analysis |
| `blakinio/canary` | pinned | inherited loader/content | configuration-sensitive |
| Otheryn | pinned | bounded search did not locate the claimed top-level freequest row; exact active-file inventory/runtime stage is required | static inconclusive |
| OTClient | pinned | reads Quest Log after server storages | no fix target |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: freequests stage/config/file inventory -> player storages -> Quest Log response
preconditions:
- clean old and new database fixtures and one canonical freequests file
steps:
- apply the posted Secret Library rows with and without top-level Questlog storage
- increment stage, restart, capture active script paths and storage writes
- repeat with an intentionally duplicated stale file as a diagnostic control
- decode Quest Log visibility for new and migrated players
expected_observations:
- one active file applies each row exactly once and Quest Log visibility follows documented storage dependencies
artifacts:
- freequests-loaded-files.json
- storage-writes.jsonl
- questlog-results.json
- runtime-feasibility.md
cleanup:
- discard databases/players
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
rationale: 'evidence points to stale script duplication and possibly incomplete grant data rather than a universal loader
  failure; clean migration and storage-dependency tests must separate them Runtime execution is infrastructure-blocked: the
  repository has no deterministic game/client driver and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Reconcile this item with Crystal issue `#837` in the final decision matrix.
- Product fixes made by this audit: **none**.
