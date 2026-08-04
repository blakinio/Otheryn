# Dossier — `opentibiabr/canary#3500`

## Identity

```yaml
canonical_key: opentibiabr/canary#3500
predecessor_row: 34
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: soul-war-bosses
research_status: COMPLETE
```

## Source claim

Four Soul War encounters have explicit state-machine defects: Hatred counter reset/kick, Malice Soulcage health/failure scaling, Megalomania repeated Aspect vulnerability, and Greed initial vulnerability/order.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: Hatred counter interaction prevents a valid kick; Malice applies bounded Soulcage health and failure amplification; Megalomania requires repeated Aspect cycles; Greed begins protected and transitions only after four Greedbeasts
version_boundary: Soul War encounter scripts in the audited content generation
evidence_basis: [opentibiabr/canary#3500]
conflicts:
  - numeric timings/HP/scaling are not specified
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source supplies four exact state failures |
| CrystalServer | pinned | related Soul War lineage | inconclusive |
| `blakinio/canary` | pinned | inherited content | potentially affected |
| Otheryn | pinned | named encounter families exist; exact state/event registration must be traced | static inconclusive |
| OTClient | pinned | observes counters/effects; no authoritative state ownership | runtime control |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: controlled boss phases/counters/add deaths -> vulnerability, kick/fail and reset state
preconditions:
- isolated party
- deterministic boss health/time controls
steps:
- Hatred: exercise counter before/after deadline and record kick marker
- Malice: kill or leave Soulcage and measure boss mitigation before/after
- Megalomania: complete multiple Aspect cycles and record vulnerability windows
- Greed: inspect entry state, kill exactly four Greedbeasts and record transition
- test wipe/reset and repeated entry for every boss
expected_observations:
- each state transition occurs once in the documented order and resets cleanly
artifacts:
- soulwar-state-machines.jsonl
- boss-stats.csv
- reset-results.json
- runtime-feasibility.md
cleanup:
- reset arenas and discard party state
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
rationale: 'the source defines four falsifiable ordering/state defects, but code-path assignment and numeric balance require
  isolated execution Runtime execution is infrastructure-blocked: the repository has no deterministic game/client driver and
  adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Source official numeric thresholds before repair; keep structural state fixes separate from balance tuning.
- Product fixes made by this audit: **none**.
