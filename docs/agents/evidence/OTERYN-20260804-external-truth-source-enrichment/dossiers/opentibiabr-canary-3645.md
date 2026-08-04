# Dossier — `opentibiabr/canary#3645`

## Identity

```yaml
canonical_key: opentibiabr/canary#3645
predecessor_row: 26
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: wand-item-protocol-metadata
research_status: COMPLETE
```

## Source claim

After the 13.40-to-14.12 transition, registering/using a wand can expose attack value 0/null in skills or Cyclopedia and can crash/debug the client when opening those views or attacking. The source suspects wand-specific weapon metadata serialization.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: every wand serialized to supported 14.x client item/skill/Cyclopedia paths carries protocol-valid weapon metadata; viewing or attacking never emits null/invalid fields or crashes the client
version_boundary: source explicitly contrasts 13.40 with 14.12; exact opcode/field layout is not supplied
evidence_basis: [opentibiabr/canary#3645]
conflicts:
  - source does not identify wand ID, exact client build, packet or stack trace
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | source reports affected weapon/item metadata path |
| CrystalServer | pinned | wand and protocol item-description paths exist; version applicability inconclusive |
| `blakinio/canary` | pinned | related source lineage | inconclusive |
| Otheryn | pinned | wand registration, item type and profile-specific protocol serialization exist; no exact invalid field proven by bounded search | static inconclusive |
| OTClient | pinned | maintained parser/UI is essential to identify whether null attack is accepted, defaulted or fatal | relevant end-to-end |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: named wand definition/equip/use -> server item/skills/Cyclopedia packets -> client parse/UI/attack result
preconditions:
  - representative wand IDs including zero-attack and level-restricted variants
  - protocol fixtures for 13.40 and 14.12-compatible profiles
steps:
  - open skills and Cyclopedia, inspect wand, equip/use and attack for each profile
  - capture serialized item/weapon fields and client logs/crash artifacts
  - compare with non-wand melee and distance controls
  - fuzz only declared optional/zero fields within isolated packet fixtures
expected_observations:
  - no null/invalid field or client failure; wand-specific fields match the negotiated layout
artifacts: [wand-protocol-matrix.json, packet-traces.jsonl, client-logs, crash-artifacts]
cleanup: [discard test player]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: exact source wand/client is missing, but a bounded representative matrix is feasible
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
truth_status: PARTIALLY_PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: PENDING
owner_action: OPEN_PROTOCOL_DECISION
confidence: medium
rationale: the reported cross-version client failure is plausible and testable, but the source omits the exact item and packet field, so protocol capture must precede any wand-specific condition
```

## Drift and unresolved questions

- Identify the exact 14.12 item/skills/Cyclopedia field that distinguishes wands from attack-bearing weapons.
- Product fixes made by this audit: **none**.
