# Dossier — `opentibiabr/canary#2730`

## Identity

```yaml
canonical_key: opentibiabr/canary#2730
predecessor_row: 62
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: killing-in-the-name-snapper
research_status: COMPLETE
```

## Source claim

After completing the crocodile kill count and killing The Snapper, Grizzly Adams repeatedly grants boss access without recognizing boss completion, so the prerequisite is paid once and the boss can be farmed indefinitely.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: crocodile task completion grants one Snapper attempt; boss death advances the boss/task storage exactly once, enables the defined reward/dialogue and prevents repeat access until an explicitly repeatable task cycle is completed
version_boundary: Killing in the Name of task generation at audited revisions
evidence_basis: [opentibiabr/canary#2730]
conflicts: []
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | persistent boss-completion failure reported |
| CrystalServer | pinned | related task/NPC/boss lineage | inconclusive |
| `blakinio/canary` | pinned | inherited datapack | potentially affected |
| Otheryn | pinned | crocodile counter, boss access, death event and Grizzly dialogue storages must be reconciled | static inconclusive |
| OTClient | pinned | NPC dialogue/teleport observer only | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: crocodile task storages -> boss access/death -> Grizzly dialogue/reward/re-entry
preconditions: [isolated players before count, after count, after access and after boss kill]
steps:
  - complete exact crocodile count and request boss access
  - kill The Snapper, relog/restart and speak to Grizzly Adams
  - attempt immediate and delayed re-entry
  - repeat boss death event delivery/party/summon variants and verify idempotence
expected_observations:
  - one completion transition and reward occur; duplicate death/dialogue cannot reopen access without a valid new cycle
artifacts: [snapper-storage-timeline.jsonl, npc-dialogue.json, access-matrix.json]
cleanup: [discard players/arena]
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
rationale: the issue supplies a complete persistence sequence; storage/event tracing will identify the mismatched boss-completion key or transition
```

## Drift and unresolved questions

- Confirm whether task design permits repeat cycles and, if so, which prerequisite must reset.
- Product fixes made by this audit: **none**.
