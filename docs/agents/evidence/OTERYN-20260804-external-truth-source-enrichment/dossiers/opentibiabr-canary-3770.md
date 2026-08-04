# Dossier — `opentibiabr/canary#3770`

## Identity

```yaml
canonical_key: opentibiabr/canary#3770
predecessor_row: 22
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: ice-islands-anthill-action
research_status: COMPLETE
```

## Source claim

Using the filled ant jug on the western mast does nothing during Nibelor 2. Later discussion supplies a corrected action and reports that the fix is merged and the quest works.

## Provenance

| ID | Source | Revision | Claim |
|---|---|---|---|
| S1 | Issue `#3770` | open | original no-action symptom |
| S2 | Issue discussion | later comments | exact corrected action and a successful quest report |
| S3 | Otheryn `actions_anthill.lua` | `1f316400053f489e58608d13961069835871ab0e` | contains the supplied `7244` + mast `(32360,31365,7)` branch and advances quest/storage |

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: with questline storage 6 and filled jug 7244, using mast item 4940 at 32360,31365,7 emits effect/message and advances Questline to 7 and Mission03 to 3
version_boundary: The Ice Islands quest datapack at the audited revisions
evidence_basis: [S1, S2, S3]
conflicts:
  - target branch removes item 7243 although the used jug is 7244; this is a separate consumption question, not the reported no-action failure
```

## Five-repository static comparison

| Repository | Revision | State | Assessment |
|---|---|---|---|
| upstream Canary | pinned | corrected action present in current lineage | fixed relative to report |
| CrystalServer | pinned | corresponding action path located | requires consumption parity check |
| `blakinio/canary` | pinned | inherited corrected action family | likely fixed |
| Otheryn | pinned | exact mast branch and storage progression present | not affected by reported no-action bug |
| OTClient | pinned | standard use-item path only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: quest storage/item/mast use -> effects, storage transition and jug consumption
preconditions: [isolated player at Questline 6 with item 7244]
steps:
  - use 7244 on item 4940 at the exact mast
  - record return, effects, messages, storage and inventory
  - run wrong-coordinate, wrong-item and wrong-storage controls
expected_observations:
  - valid case advances to 7/3; controls do not
  - verify whether 7244 is consumed or remains because code removes 7243
artifacts: [ice-islands-anthill.jsonl, server.log]
cleanup: [discard quest player]
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
static_conclusion: TARGET_NOT_AFFECTED
runtime_conclusion: PENDING
owner_action: NO_ACTION
confidence: high
rationale: Otheryn already contains the exact corrected mast branch reported as merged; only a separate filled-jug consumption check remains
```

## Drift and unresolved questions

- Verify whether official behavior consumes item 7244 and whether `removeItem(7243)` is an independent defect.
- Product fixes made by this audit: **none**.
