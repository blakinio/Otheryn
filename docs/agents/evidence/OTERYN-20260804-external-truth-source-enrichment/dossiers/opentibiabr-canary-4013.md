# Dossier — `opentibiabr/canary#4013`

## Identity

```yaml
canonical_key: opentibiabr/canary#4013
predecessor_row: 16
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: interval-server-save
research_status: COMPLETE
```

## Source claim

Canary 15.11 interval saves no longer emit warnings or completion logs and may not execute at all. The source tests hourly and other intervals on Windows/Linux.

## Provenance

| ID | Source | Revision | Claim |
|---|---|---|---|
| S1 | `opentibiabr/canary#4013` | open | interval save produces no visible warning/completion |
| S2 | Otheryn `save_interval.lua` | `1f316400053f489e58608d13961069835871ab0e` | every interval callback returns unless current time is within 60 seconds of `GLOBAL_SERVER_SAVE_TIME` |
| S3 | same script | same | actual save, broadcast, log and webhook occur only after that daily-time gate passes |

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: when interval saving is enabled, every configured interval independently schedules one warning and one save/completion sequence; daily global-save time must not suppress unrelated interval saves
version_boundary: Canary/Otheryn 15.11-era save interval configuration
evidence_basis: [S1, S2, S3]
conflicts: []
```

## Five-repository static comparison

| Repository | Revision | Observed state | Assessment |
|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | interval script family contains daily-time gating | affected |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | corresponding interval/global-save scripts require exact behavior comparison | potentially affected |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | inherited script family | likely affected |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | interval callback is gated by time-left-to-daily-save | affected |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | only receives broadcast; no fix target | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: NOT_APPLICABLE
system_boundary: short interval configuration -> warning/save invocation -> durable player/database state and logs
preconditions:
- isolated database and player with a known unsaved mutation
- interval set to two minutes and daily save time more than one hour away
steps:
- run for three intervals while recording broadcasts, logs, save invocation counters and persisted mutation
- repeat with daily save time within 60 seconds as a positive control
- repeat with interval toggle disabled as a negative control
expected_observations:
- pinned target skips all far-from-daily-time intervals and only saves near the daily time
artifacts:
- save-events.jsonl
- server.log
- persistence-before-after.json
- runtime-feasibility.md
cleanup:
- discard isolated database/world
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: 'not applicable: pinned static evidence already reaches a target disposition; runtime execution would not change
  the audit decision'
```

## Runtime execution

```yaml
execution_status: NOT_RUN
exact_otheryn_head: not applicable
run_ids: []
observations:
- static comparison is sufficient for the target disposition; no game-world state was created
artifacts:
- runtime-feasibility.md
cleanup_result: not applicable
```

## Conclusions

```yaml
truth_status: PROVEN
static_conclusion: TARGET_AFFECTED
runtime_conclusion: NOT_APPLICABLE
owner_action: OPEN_FIX_PROGRAM
confidence: high
rationale: the target interval handler explicitly suppresses every callback outside a 60-second daily-save window, exactly
  explaining the missing warnings, logs and saves Runtime execution is not applicable because the pinned static comparison
  already determines the target disposition.
```

## Drift and unresolved questions

- Determine whether interval save and daily global save should coexist or be mutually exclusive configuration modes.
- Ensure any repair prevents overlapping saves and duplicate warnings.
- Product fixes made by this audit: **none**.
