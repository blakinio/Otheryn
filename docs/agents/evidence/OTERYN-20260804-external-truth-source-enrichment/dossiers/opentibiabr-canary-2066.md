# Dossier — `opentibiabr/canary#2066`

## Identity

```yaml
canonical_key: opentibiabr/canary#2066
predecessor_row: 69
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: cults-barkless-leiden
research_status: COMPLETE
```

## Source claim

Barkless progression is broken by an NPC topic/keyword guard and misplaced TrialAccessDoor storage; later quest stages then desynchronize. Separately, Leiden's healing ability makes Ravenous Hunger immune to damage, while disabling the ability lets the encounter work.

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: Barkless dialogue follows a deterministic topic sequence and sets mission/door storages only at their intended transitions; Leiden healing modifies the boss encounter without making Ravenous Hunger permanently invulnerable or bypassing damage rules
version_boundary: Cults of Tibia Barkless and Leiden encounter at audited revisions
evidence_basis: [opentibiabr/canary#2066]
conflicts:
  - removing topic guards or the entire heal ability are diagnostic workarounds, not authoritative fixes
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | exact dialogue/storage and heal-related failures reported |
| CrystalServer | pinned | related quest/encounter lineage | inconclusive |
| `blakinio/canary` | pinned | inherited datapack | potentially affected |
| Otheryn | pinned | Barkless NPC topic/storage and Leiden heal/damage paths require direct trace; same Cults content family is present | static inconclusive |
| OTClient | pinned | NPC text and combat observer only | no direct fix target |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_INFEASIBLE
system_boundary: Barkless dialogue/storage and Leiden heal events -> quest access and Ravenous Hunger damageability
preconditions:
- isolated players at each Barkless stage and resettable Leiden arena
steps:
- execute every Barkless keyword/topic sequence including interruption/relog and inspect storage writes
- verify TrialAccessDoor before/after exact mission transitions
- fight Leiden/Ravenous Hunger with heal ability enabled, recording target, amount, immunities and boss HP
- run heal-disabled diagnostic control without treating it as expected behavior
expected_observations:
- dialogue remains reachable, storages advance once, and healing never creates permanent invulnerability
artifacts:
- barkless-dialogue-matrix.json
- storage-timeline.jsonl
- leiden-combat-events.jsonl
- runtime-feasibility.md
cleanup:
- discard players and reset arena
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
rationale: 'the source identifies two concrete, independently testable mechanisms; dialogue/storage and combat-heal fixes
  must remain separate Runtime execution is infrastructure-blocked: the repository has no deterministic game/client driver
  and adding one is outside audit-only authority.'
```

## Drift and unresolved questions

- Determine intended Leiden heal target/formula and the exact Barkless topic state machine before implementation.
- Product fixes made by this audit: **none**.
