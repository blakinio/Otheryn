# Dossier — `opentibiabr/canary#4052`

## Identity

```yaml
canonical_key: opentibiabr/canary#4052
predecessor_row: 6
source_type: pull_request
prior_bucket: INSUFFICIENT
prior_truth_status: PARTIALLY_PROVEN
family: build-toolchain-reproducibility
research_status: COMPLETE
```

## Source claim

- Current title: `build: pin vcpkg registry and developer tools`
- Source URL: `https://github.com/opentibiabr/canary/pull/4052`
- Exact claim: moving Canary's patched protobuf port from an unversioned overlay into a versioned local registry and pinning native developer tools makes dependency resolution and local/CI builds more reproducible.
- Claimed affected version/protocol: build infrastructure on the PR base `7644bcbcbbad4a09e52a5707ed531e4dd21d8a79`; no game protocol boundary.
- Claimed validation: macOS release configure/build succeeded; manual testing was not reported and the PR checklist did not assert completed checks.
- Claimed expected behavior: supported environments resolve the same dependency sources and tool versions and produce successful configure/build/test runs without relying on mutable host defaults.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream PR | `opentibiabr/canary` | PR `#4052`, head `736a018df178907b79d5156046f11c9deaa6e560` | 2026-08-04 | stated reproducibility goal and one macOS build result | primary claim | open PR; no full matrix or comparison measurements |
| S2 | PR patch | same | same head | 2026-08-04 | adds `.mise.toml`, hash-pinned Python requirements, vcpkg bootstrap, local registry and CI wiring | exact change evidence | 25-file infrastructure change is broader than the predecessor summary |
| S3 | repository manifest | `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | 2026-08-04 | pins vcpkg builtin baseline and configures overlay ports/triplets | primary target evidence | does not pin CMake/Ninja/Python/ccache host tools |
| S4 | target overlay | `blakinio/Otheryn` | same | 2026-08-04 | protobuf overlay pins source tag `v33.4` and SHA512 | primary target evidence | overlay ownership/versioning remains repository-local rather than a vcpkg registry contract |
| S5 | client manifest | `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | 2026-08-04 | uses the same vcpkg builtin baseline as Otheryn | cross-project evidence | client toolchain policy is independent and not a reason to copy the server PR wholesale |

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: dependency source revisions and required build-tool versions are explicit, immutable enough for supported platforms, and validated by the same configure/build/test matrix used by CI
version_boundary: repository build contract only; no runtime or packet-protocol effect
evidence_basis:
  - S1
  - S2
  - S3
  - S4
conflicts:
  - Otheryn already pins the vcpkg baseline and protobuf source hash, so the PR is not a direct missing-baseline fix
  - the PR supplies only a reported macOS build and remains open, so portability and maintenance cost are not proven
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | `vcpkg.json`, `vcpkg-configuration.json`, workflows, overlay ports | predecessor base uses pinned baseline/overlay model; open PR proposes a local registry and pinned tools | improvement candidate | high |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | build manifests/workflows | separate donor build policy; no evidence that PR 4052 is adopted as a stable contract | inconclusive/independent | medium |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | build manifests/workflows | Otheryn lineage already carries project-specific overlay/tooling changes | partial overlap | medium-high |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | `vcpkg.json`, `vcpkg-configuration.json`, `cmake/overlay-ports/protobuf/portfile.cmake` | baseline and protobuf source are pinned; host developer tools and a registry contract are not | partially affected by reproducibility gap | high |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | `vcpkg.json` | same baseline pin, but separate client build system and release constraints | related architecture, not direct applicability | high |

## Deterministic runtime plan

```yaml
plan_status: NOT_APPLICABLE
system_boundary: build/toolchain validation, not game runtime behavior
preconditions: []
steps: []
expected_observations: []
artifacts:
- supported-platform configure-build-test matrix
- dependency resolution lock report
- clean-host bootstrap transcript
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
static_conclusion: TARGET_AFFECTED
runtime_conclusion: NOT_APPLICABLE
owner_action: OPEN_ARCHITECTURE_DECISION
confidence: high
rationale: Otheryn already has deterministic vcpkg and protobuf source pins, but it does not express the complete host toolchain
  contract proposed by the PR; because the upstream change remains open and incompletely validated, adoption should be decided
  and tested as Otheryn build architecture rather than copied as a bug fix Runtime execution is not applicable because the
  pinned static comparison already determines the target disposition.
```

## Drift and unresolved questions

- Drift after pinned revision: PR `#4052` remains open and changed after the predecessor snapshot; its final accepted form is not established.
- Unresolved questions:
  - Should Otheryn standardize developer tools through mise, containers, GitHub Actions images, or a narrower documented minimum-version policy?
  - Does a local vcpkg registry reduce maintenance risk compared with the existing audited overlay?
  - Must the same toolchain contract be shared with `blakinio/otclient`, or independently versioned?
- Product fixes made by this audit: **none**.
