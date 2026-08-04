# Independent falsification — external truth-source enrichment

Status: **PASS**

This review uses a separate parser and invariant set from `validate_evidence.py`. It attempts to falsify canonical identity, item counters, runtime-disposition logic, registry equality, path authority and the zero-runtime-execution claim.

## Results

- canonical scope: 60 rows / 60 unique keys / 49 `REPRO` + 11 `INSUFFICIENT`;
- dossiers: 60 rows / 60 unique keys;
- truth: {'PARTIALLY_PROVEN': 24, 'PROVEN': 31, 'UNKNOWN': 5};
- static: {'STATIC_INCONCLUSIVE': 47, 'TARGET_AFFECTED': 9, 'TARGET_NOT_AFFECTED': 2, 'TARGET_PATH_ABSENT': 2};
- runtime: {'NOT_APPLICABLE': 13, 'NOT_RUN_INFEASIBLE': 42, 'NOT_RUN_REFERENCE_INSUFFICIENT': 5};
- owner actions: {'NO_ACTION': 2, 'OPEN_ARCHITECTURE_DECISION': 3, 'OPEN_FIX_PROGRAM': 8, 'OPEN_PROTOCOL_DECISION': 2, 'RESEARCH_REQUIRED': 45};
- plans: {'BLOCKED_INFEASIBLE': 42, 'BLOCKED_REFERENCE': 5, 'NOT_APPLICABLE': 13};
- executions: {'BLOCKED': 47, 'NOT_RUN': 13};
- changed paths reviewed: 77; product/runtime paths: 0;
- matrices and both compressed registries: exact 60-key equality checked;
- runtime feasibility claim: checked against item-level conclusion/plan/execution consistency.

## Material findings

- none; open material findings: **0**.

## Non-claims

- This audit does not claim that any of the 42 gameplay/client scenarios was executed.
- It does not authorize product fixes or a reusable gameplay E2E harness.
- `NOT_RUN_INFEASIBLE` is an exact repository-capability/authority conclusion, not evidence that the reported behavior is absent.
