# Dossier — `opentibiabr/canary#2272`

## Identity

```yaml
canonical_key: opentibiabr/canary#2272
predecessor_row: 67
source_type: issue
prior_bucket: INSUFFICIENT
prior_truth_status: UNPROVEN
family: player-weapon-damage-distribution
research_status: COMPLETE
```

## Source claim

- Current title: `Attack Knight/Paladin low hit`
- Source URL: `https://github.com/opentibiabr/canary/issues/2272`
- Exact claim: knights and paladins miss too often and produce excessively frequent low weapon hits; one example uses a level-100 elite knight, skill 100 and Magic Sword.
- Claimed comparison: a calculator maximum of 316 is asserted, while changing vocation melee damage reportedly raises maximum to 558.
- Missing inputs: stance, weapon attack/imbuements, target armor/defense/resistances, player level/vocation data, blessings/charms/wheel, sample size, raw rolls, calculator identity/version and official reference distribution.
- Claimed expected behavior: not sufficiently specified beyond one asserted maximum.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue | `opentibiabr/canary` | Issue `#2272`, open/stale | 2026-08-04 | qualitative low-hit/miss report and one character summary | primary claim | video is not normalized; no raw sample or complete combat state |
| S2 | upstream comment | same | 2025 comment | 2026-08-04 | disputes the report and says level scaling matters | contradictory community evidence | no calculation or trace is supplied either |
| S3 | bounded repository comparison | five repositories | pinned audit revisions | 2026-08-04 | relevant weapon formula, vocation multiplier, armor/defense and client display paths exist | scope-location evidence | many parameters prevent a unique static conclusion without a reference vector |

## Expected behavior

```yaml
expected_behavior_status: UNKNOWN
expected_behavior: UNKNOWN; a valid truth vector must define deterministic min/max or probability distribution after attack, skill, level, vocation multipliers, stance, target mitigation and miss chance
version_boundary: UNKNOWN; formulas and vocation data are update-sensitive
evidence_basis:
  - S1
  - S2
conflicts:
  - source asserts too-low damage while the only technical comment asserts behavior is acceptable and other damage can be too high
  - the cited 316 calculator value has no source/version and cannot control the audit
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | weapon/combat formula, vocation XML, armor/defense and hit-chance families | target architecture located, but source state is insufficient to select an erroneous term | inconclusive | low |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | same families | formula/data divergences exist but cannot be ranked without truth vectors | inconclusive | low |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | same families | inherited combat model with project drift | inconclusive | low |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | weapon formulas, vocation values, mitigation and random roll paths | no static invariant is violated by the vague report | inconclusive | low |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | combat-message/display path | displays server result and cannot establish authoritative damage distribution | not a direct formula target | high |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_REFERENCE
system_boundary: fully specified attacker/weapon/target/stance and fixed RNG -> raw attack/mitigation rolls -> damage distribution
preconditions: []
steps: []
expected_observations: []
artifacts: []
cleanup: []
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: no authoritative formula/version or complete combat vector; reproducing “low hits” without an expected distribution cannot yield pass/fail
```

## Runtime execution

```yaml
execution_status: BLOCKED
exact_otheryn_head: not applicable
run_ids: []
observations: []
artifacts: []
cleanup_result: not run
```

## Conclusions

```yaml
truth_status: UNKNOWN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: NOT_RUN_REFERENCE_INSUFFICIENT
owner_action: RESEARCH_REQUIRED
confidence: high
rationale: the report omits nearly every parameter that determines weapon damage and provides neither raw samples nor a versioned authoritative calculator/formula; any proposed code change would be tuning by guess
```

## Drift and unresolved questions

- Minimum evidence needed:
  - exact protocol/game balance version and authoritative formula or official sample;
  - complete attacker, weapon, stance and target state;
  - fixed-RNG or sufficiently large raw hit/miss sample;
  - expected min/max/mean/percentiles and mitigation stages;
  - separate knight melee and paladin distance vectors.
- Product fixes made by this audit: **none**.
