# Dossier — `zimbadev/crystalserver#853`

## Identity

```yaml
canonical_key: zimbadev/crystalserver#853
predecessor_row: 75
source_type: pull_request
prior_bucket: REPRO
prior_truth_status: PARTIALLY_PROVEN
family: hot-cuisine-quest
research_status: COMPLETE
```

## Source claim

Open PR `#853` extends Hot Cuisine from 14 to 15 ordered recipes by adding Zaoan Sauce, then allows annual out-of-order recooking and awards Culinary Master after every dish has been cooked twice.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: first completion requires all 15 recipes in order; Zaoan Sauce is represented in Quest Log/NPC ingredients/rewards; after completion each recipe can be repeated according to one explicit annual/bonus rule; Culinary Master is awarded only after every required dish meets the defined repeat count
version_boundary: CrystalServer base 8eb99d0583ccb52cc368cb45c65d97ec9fbd181e and compatible Otheryn content generation
evidence_basis: [zimbadev/crystalserver#853, exact two-file patch]
conflicts:
  - PR is open and unmerged with no published validation
  - patch comments describe a same-year bonus plus later annual cycle; official recurrence semantics are not independently proven
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | Hot Cuisine lineage must be checked independently; PR is Crystal-specific drift |
| CrystalServer | pinned | base lacks open PR changes | improvement candidate |
| `blakinio/canary` | pinned | related quest lineage | exact recipe parity unknown |
| Otheryn | pinned | bounded search found no Zaoan Sauce/Culinary Master implementation in the target quest path | target path absent/incomplete |
| OTClient | pinned | Quest Log/NPC text only | no direct fix target |

## Deterministic runtime plan

```yaml
plan_status: NOT_APPLICABLE
system_boundary: ordered recipe dialogue/items/calendar state -> quest progression/rewards/achievement
preconditions:
- isolated players before first dish, before Zaoan Sauce and after completion
- controlled clock across August/year boundaries
steps:
- complete all recipes in order and verify ingredient/reward conservation
- attempt out-of-order recipes before completion
- exercise same-year bonus and following-year repeats for every dish
- cook each dish once/twice and verify Culinary Master threshold
- relog/restart at each boundary
expected_observations:
- exact order, recurrence and achievement invariants hold without duplicate rewards or calendar lockout
artifacts:
- hot-cuisine-dialogue.jsonl
- recipe-ledger.json
- calendar-matrix.json
- achievements.json
- runtime-feasibility.md
cleanup:
- discard players/items/database
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
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: the donor patch clearly adds content absent from bounded Otheryn search, but it remains an unmerged, unvalidated
  interpretation of annual and achievement rules Runtime execution is not applicable because the pinned static comparison
  already determines the target disposition.
```

## Drift and unresolved questions

- Do not import the 226-line rewrite wholesale; first prove official recipe count, recurrence and achievement criteria.
- Product fixes made by this audit: **none**.
