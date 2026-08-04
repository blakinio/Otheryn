# Dossier — `zimbadev/crystalserver#561`

## Identity

```yaml
canonical_key: zimbadev/crystalserver#561
predecessor_row: 102
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: kusuma-within-the-tides
research_status: COMPLETE
```

## Source claim

CrystalServer contains no Kusuma boss content. Repository-wide bounded search across all four server lines returned no `Kusuma` symbol, supporting absence rather than a spawn-only defect.

## External reference

Community quest references identify Kusuma as the boss defeated during Within the Tides Quest, and CipSoft's public boss library lists Kusuma as a boss. These sources establish identity/applicability but not implementation details, coordinates or mechanics.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: the Within the Tides quest can start, enter, fight and complete a Kusuma encounter and report that completion to the quest NPC for the defined reward; arena/reset/cooldown and boss mechanics match the chosen game version
version_boundary: Within the Tides content generation represented by the target map/protocol
evidence_basis:
  - zimbadev/crystalserver#561
  - https://www.test.tibia.com/library/?subtopic=boostablebosses
  - https://www.tibiawiki.com.br/wiki/Within_the_Tides_Quest
conflicts:
  - source Issue contains only one sentence and no version/coordinate/mechanics
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | bounded symbol search found no Kusuma implementation | target path absent |
| CrystalServer | pinned | source and bounded search indicate boss absent | target path absent |
| `blakinio/canary` | pinned | bounded search found no Kusuma implementation | target path absent |
| Otheryn | pinned | bounded search found no Kusuma implementation | target path absent |
| OTClient | pinned | no boss-specific protocol ownership | irrelevant |

## Deterministic runtime plan

```yaml
plan_status: NOT_APPLICABLE
system_boundary: no target Kusuma content exists to reproduce
preconditions: []
steps: []
expected_observations: []
artifacts:
- repository-symbol-search.txt
- map-content-inventory.json
- runtime-feasibility.md
cleanup: []
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
truth_status: PARTIALLY_PROVEN
static_conclusion: TARGET_PATH_ABSENT
runtime_conclusion: NOT_APPLICABLE
owner_action: OPEN_ARCHITECTURE_DECISION
confidence: high
rationale: all compared server repositories lack a Kusuma symbol while external references establish that Kusuma belongs to
  Within the Tides; a full versioned content design is required rather than a bug patch Runtime execution is not applicable
  because the pinned static comparison already determines the target disposition.
```

## Drift and unresolved questions

- Obtain authoritative map coordinates, quest storages, encounter mechanics, rewards and protocol/content version before opening implementation.
- Product fixes made by this audit: **none**.
