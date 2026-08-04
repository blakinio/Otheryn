# Dossier template

> Copy this structure to `dossiers/<source-owner>-<source-repo>-<number>.md`. Replace every placeholder. Do not mark a dossier complete while any required field remains `PENDING` or unsupported.

## Identity

```yaml
canonical_key: <owner/repo#number>
predecessor_row: <integer>
source_type: issue | pull_request
prior_bucket: REPRO | INSUFFICIENT
prior_truth_status: PROVEN | PARTIALLY_PROVEN | UNPROVEN | BLOCKED_BY_DECISION
family: <bounded behavior family>
research_status: PENDING | COMPLETE
```

## Source claim

- Current title: `<title>`
- Source URL: `<url>`
- Exact claim: `<one testable statement>`
- Claimed affected version/protocol: `<version, revision or UNKNOWN>`
- Claimed reproduction: `<steps or none>`
- Claimed expected behavior: `<expected result or UNKNOWN>`

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream issue/PR | `<repo>` | `<head or issue state>` | `<date>` | `<claim>` | primary claim | issue prose is not independent proof |

## Expected behavior

```yaml
expected_behavior_status: PROVEN | PARTIALLY_PROVEN | CONTRADICTED | UNKNOWN
expected_behavior: <observable result or UNKNOWN>
version_boundary: <exact applicability or UNKNOWN>
evidence_basis:
  - <source IDs>
conflicts:
  - <none or exact conflict>
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | `<paths>` | `<state>` | affected/fixed/absent/inconclusive/irrelevant | low/medium/high |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | `<paths>` | `<state>` | affected/fixed/absent/inconclusive/irrelevant | low/medium/high |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | `<paths>` | `<state>` | affected/fixed/absent/inconclusive/irrelevant | low/medium/high |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | `<paths>` | `<state>` | affected/fixed/absent/inconclusive/irrelevant | low/medium/high |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | `<paths or reason irrelevant>` | `<state>` | affected/fixed/absent/inconclusive/irrelevant | low/medium/high |

## Deterministic runtime plan

```yaml
plan_status: READY | NOT_APPLICABLE | BLOCKED_REFERENCE | BLOCKED_UNSAFE | BLOCKED_INFEASIBLE
system_boundary: <real input to observable output>
preconditions:
  - <condition>
steps:
  - <deterministic step>
expected_observations:
  - <observation>
artifacts:
  - <artifact path/name>
cleanup:
  - <cleanup>
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: <none or exact blocker>
```

## Runtime execution

```yaml
execution_status: NOT_RUN | PASS | FAIL | BLOCKED
exact_otheryn_head: <sha or not applicable>
run_ids: []
observations: []
artifacts: []
cleanup_result: <not run or result>
```

## Conclusions

```yaml
truth_status: PROVEN | PARTIALLY_PROVEN | CONTRADICTED | UNKNOWN
static_conclusion: TARGET_AFFECTED | TARGET_NOT_AFFECTED | TARGET_PATH_ABSENT | STATIC_INCONCLUSIVE
runtime_conclusion: REPRODUCED | NOT_REPRODUCED | NOT_APPLICABLE | NOT_RUN_UNSAFE | NOT_RUN_INFEASIBLE | NOT_RUN_REFERENCE_INSUFFICIENT | PENDING
owner_action: OPEN_FIX_PROGRAM | OPEN_ARCHITECTURE_DECISION | OPEN_PROTOCOL_DECISION | OPEN_PERSISTENCE_DECISION | NO_ACTION | RESEARCH_REQUIRED
confidence: low | medium | high
rationale: <bounded evidence-grounded rationale>
```

## Drift and unresolved questions

- Drift after pinned revision: `<none or exact later change>`
- Unresolved questions: `<none or list>`
- Product fixes made by this audit: **none**
