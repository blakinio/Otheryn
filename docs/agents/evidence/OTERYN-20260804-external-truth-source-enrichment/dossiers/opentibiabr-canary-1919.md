# Dossier — `opentibiabr/canary#1919`

## Identity

```yaml
canonical_key: opentibiabr/canary#1919
predecessor_row: 70
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: diamond-arrow-elemental-imbuement
research_status: COMPLETE
```

## Source claim

Diamond Arrow area hits inherit an elemental bow imbuement, but the reporter questions whether the original holy component should still damage secondary targets or whether elements are being combined/applied incorrectly.

## Expected behavior

```yaml
expected_behavior_status: UNKNOWN
expected_behavior: UNKNOWN; authoritative rules must define how physical/holy arrow components and bow elemental conversion are split across primary and expanded targets, including resistance application and combat messages
version_boundary: UNKNOWN; ammunition/imbuement behavior is balance-version sensitive
evidence_basis: [opentibiabr/canary#1919]
conflicts:
  - source is framed as a question and supplies no expected formula or reference result
  - videos are not normalized into raw damage/components
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | behavior questioned, not proven defective |
| CrystalServer | pinned | related ammunition/imbuement combat lineage | inconclusive |
| `blakinio/canary` | pinned | inherited formula path | inconclusive |
| Otheryn | pinned | arrow area, weapon imbuement and multi-component combat paths exist; no authoritative invariant to classify | static inconclusive |
| OTClient | pinned | displays damage types/effects but server calculates them | observer only |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_REFERENCE
system_boundary: bow imbue + Diamond Arrow + primary/secondary target resistances -> damage components
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
blocker: no versioned official formula or complete reference damage vector defines whether holy and imbuement components should
  coexist or convert on expanded targets
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
rationale: the Issue does not assert a falsifiable expected formula; reproducing current numbers would not establish correctness
  without an authoritative balance-version reference Runtime execution is reference-blocked because no deterministic expected
  result is supported.
```

## Drift and unresolved questions

- Minimum truth source: exact official version, attacker/bow/imbue/arrow state, primary and secondary targets with known resistances, and expected raw damage-component formula.
- Product fixes made by this audit: **none**.
