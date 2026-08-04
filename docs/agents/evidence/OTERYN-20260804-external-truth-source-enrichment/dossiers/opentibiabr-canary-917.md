# Dossier — `opentibiabr/canary#917`

## Identity

```yaml
canonical_key: opentibiabr/canary#917
predecessor_row: 71
source_type: issue
prior_bucket: INSUFFICIENT
prior_truth_status: UNPROVEN
family: incoming-monster-damage-defense
research_status: COMPLETE
```

## Source claim

- Current title: `Bugged base damage and defense`
- Source URL: `https://github.com/opentibiabr/canary/issues/917`
- Exact claims:
  1. a creature deals substantially more total damage while the player attacks it than while the player does not attack it;
  2. characters with shielding skill 26 and 50 receive the same damage with the same equipment.
- Claimed evidence: two one-minute videos with totals 40 and 154; no raw hit sequence, monster name, equipment list, stance, simultaneous attackers, defense charges, skill progression state or server revision.
- Claimed expected behavior: comparison with an unspecified “original CipSoft” environment; no versioned formula or deterministic vector.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue | `opentibiabr/canary` | Issue `#917`, open/stale | 2026-08-04 | two qualitative combat/defense claims and aggregate video totals | primary claim | external videos are not normalized; critical state and raw rolls are absent |
| S2 | Issue discussion | same | stale-bot only | 2026-08-04 | no maintainer confirmation, reproduction or formula was added | negative evidence | does not disprove the report |
| S3 | bounded repository comparison | five repositories | pinned audit revisions | 2026-08-04 | relevant monster attack, player block/armor/shielding, fight mode and client display families exist | scope-location evidence | no exact branch can be classified without a complete combat trace |

## Expected behavior

```yaml
expected_behavior_status: UNKNOWN
expected_behavior: UNKNOWN; valid comparison requires identical monster attack rolls and player defense state while controlling attack/follow mode, defense charges, shield/weapon defense, armor, skills and concurrent attackers
version_boundary: UNKNOWN; source only says Rookgaard/original CipSoft without a client/server date
evidence_basis:
  - S1
  - S2
conflicts:
  - one-minute aggregate totals are dominated by random attack timing and rolls unless the same deterministic sequence is replayed
  - attacking can change facing, distance, target behavior, defense stance or simultaneous combat state, none of which is controlled
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | creature combat, `blockHit`, armor/defense/shielding and fight-mode paths | many possible variables; no source vector maps to one defect | inconclusive | low |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | same families | donor formula/data differences exist but cannot establish truth | inconclusive | low |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | same families | inherited model with drift | inconclusive | low |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | player mitigation, combat state, monster attacks, vocation/skill data | no statically falsifiable claim can be evaluated from source evidence | inconclusive | low |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | fight-mode input and combat-message display | may alter submitted fight mode but cannot define server mitigation truth | relevant control only | medium |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_REFERENCE
system_boundary: fixed monster attack sequence and complete player defense state -> mitigation stages -> received damage distribution
preconditions: []
steps: []
expected_observations: []
artifacts:
- runtime-feasibility.md
cleanup: []
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: source lacks named monster, equipment, stance, attack sequence, defense-charge conditions, official version/formula
  and raw hit samples; the two aggregate videos cannot define deterministic expected output
```

## Runtime execution

```yaml
execution_status: BLOCKED
exact_otheryn_head: not applicable
run_ids: []
observations:
- reference behavior is insufficient for a deterministic pass/fail runtime assertion
artifacts:
- runtime-feasibility.md
cleanup_result: not started; no state created
```

## Conclusions

```yaml
truth_status: UNKNOWN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: NOT_RUN_REFERENCE_INSUFFICIENT
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: the report combines uncontrolled random combat totals with an underspecified shielding comparison; neither the
  source nor discussion supplies a versioned authoritative mitigation model or reproducible fixture Runtime execution is reference-blocked
  because no deterministic expected result is supported.
```

## Drift and unresolved questions

- Minimum evidence needed:
  - exact monster, attack XML and official/reference version;
  - complete equipment, skills, fight mode, facing and concurrent attacker count;
  - deterministic attack rolls or a statistically powered raw sample;
  - defense-charge and shield/weapon selection observations;
  - expected mitigation stages and tolerances.
- Product fixes made by this audit: **none**.
