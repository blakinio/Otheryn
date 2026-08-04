# Dossier — `opentibiabr/canary#3430`

## Identity

```yaml
canonical_key: opentibiabr/canary#3430
predecessor_row: 43
source_type: issue
prior_bucket: INSUFFICIENT
prior_truth_status: UNPROVEN
family: account-login-protocol-gating
research_status: COMPLETE
```

## Source claim

- Current title: `getCharacterList has a possible logical bug`
- Source URL: `https://github.com/opentibiabr/canary/issues/3430`
- Exact claim: the `if (oldProtocol && disabled) ... else if (!oldProtocol)` gate disconnects every modern account login, producing the unsupported-protocol message even when the incoming client version is otherwise valid.
- Claimed affected environment: Windows, OTClient attempting protocol 13.40; source author explicitly was unsure whether this was the root cause.
- Claimed expected behavior: a negotiated and allowed modern protocol reaches authentication and character-list serialization; only disabled legacy compatibility or an unrecognized profile is rejected.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue | `opentibiabr/canary` | Issue `#3430`, open | 2026-08-04 | identifies a concrete unconditional modern-protocol rejection branch | primary claim | reporter's minimal example omits the wider protocol setup and reporter had a different client that worked |
| S2 | upstream pinned code | `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | 2026-08-04 | `getCharacterList` still contains `else if (!oldProtocol)` and rejects all modern logins reaching that function | primary code proof | code may be a transient regression relative to later main |
| S3 | donor pinned code | `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | 2026-08-04 | contains the same unconditional modern rejection shape | donor comparison | Crystal supports a narrower protocol model |
| S4 | target pinned code | `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | 2026-08-04 | removes the unconditional modern rejection and resolves allowed layouts/profiles before authentication | primary target evidence | runtime matrix still needed to guard profile-specific regressions |

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: modern clients whose version/assets resolve to an allowed account-login profile continue to authentication and receive the corresponding character-list layout; disabled or unknown profiles are rejected once with a precise reason
version_boundary: all Otheryn account-login profiles registered by ProtocolProfileRegistry at the audited revision
evidence_basis:
  - S2
  - S4
conflicts:
  - the Issue title calls the defect only possible, but the pinned upstream branch condition is logically unconditional for `oldProtocol == false`
  - source client behavior cannot establish which profile/assets it actually sent
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | `src/server/network/protocol/protocollogin.cpp::getCharacterList` | modern branch is unconditionally disconnected | affected | high |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | same function | same unconditional modern rejection shape | affected under its modern path | high |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | account-login protocol gate | project lineage requires exact-head check; predecessor evidence did not prove removal | inconclusive | medium |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | `getCharacterList`, `resolveLoginLayout`, profile registry | only disabled old protocol is rejected in `getCharacterList`; modern/legacy acceptance is profile-driven | not affected by claimed branch | high |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | login packet/profile inputs | useful as a negotiated-profile client, but server branch conclusion does not depend on client implementation | relevant runtime control | medium-high |

## Deterministic runtime plan

```yaml
plan_status: NOT_APPLICABLE
system_boundary: login prelude/version/assets -> profile resolution -> authentication -> character-list or precise rejection
preconditions:
- isolated Otheryn account with one character
- valid credentials and deterministic fixtures for every enabled account-login profile
- invalid version, invalid asset signature and disabled-legacy controls
steps:
- execute successful login for each enabled profile and decode the full character-list response
- execute disabled legacy, unknown version and invalid asset-signature controls
- assert exactly one rejection at the profile-resolution boundary and no modern request reaches the historic unconditional
  message path
expected_observations:
- enabled modern and legacy profiles succeed according to configuration
- unsupported controls fail with profile-specific messages and no authentication side effects
artifacts:
- login-profile-matrix.json
- account-login-packets.jsonl
- server-login.log
- runtime-feasibility.md
cleanup:
- discard isolated account/database state
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
truth_status: PROVEN
static_conclusion: TARGET_NOT_AFFECTED
runtime_conclusion: NOT_APPLICABLE
owner_action: NO_ACTION
confidence: high
rationale: the defect is real in the pinned upstream and Crystal code, but Otheryn removed the unconditional modern rejection
  and replaced version gating with explicit profile/layout resolution; only regression coverage remains Runtime execution
  is not applicable because the pinned static comparison already determines the target disposition.
```

## Drift and unresolved questions

- Drift after pinned revision: exact-final-head login profile tests remain required.
- Unresolved questions:
  - Does `blakinio/canary` independently contain the final profile-driven fix?
  - Which official and maintained-client build/assets fixtures should remain permanent regression tests?
- Product fixes made by this audit: **none**.
