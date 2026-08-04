# Dossier — `opentibiabr/canary#3407`

## Identity

```yaml
canonical_key: opentibiabr/canary#3407
predecessor_row: 50
source_type: issue
prior_bucket: INSUFFICIENT
prior_truth_status: UNPROVEN
family: monster-perception-viewport
research_status: COMPLETE
```

## Source claim

- Current title: `Monster vision`
- Source URL: `https://github.com/opentibiabr/canary/issues/3407`
- Exact claim: monsters perceive players farther than intended, making one-on-one pulls harder.
- Claimed affected environment: Linux; no monster, map, coordinate, distance, line-of-sight arrangement, server revision or official comparison.
- Discussion hypothesis: server viewport constants are client viewport plus 3 horizontally and plus 5 vertically.
- Claimed expected behavior: not specified; the source does not define the intended official aggro/acquisition range.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue | `opentibiabr/canary` | Issue `#3407`, open/stale | 2026-08-04 | qualitative report of enlarged monster vision | primary claim | no reproducible geometry or reference value |
| S2 | upstream comment | same | comment on `map_const.hpp` | 2026-08-04 | identifies viewport constants as a possible control | hypothesis | does not prove monster target acquisition uses exactly those limits or that they are incorrect |
| S3 | target code | `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | 2026-08-04 | client viewport is 8x6 and server maximum viewport is 11x11 | primary static fact | these are global spectator/path boundaries, not a normative monster-vision specification |

## Expected behavior

```yaml
expected_behavior_status: UNKNOWN
expected_behavior: UNKNOWN; a valid reference must define acquisition, retention and line-of-sight ranges for at least one named monster and map geometry
version_boundary: UNKNOWN; behavior may differ by monster, floor, invisibility, challenge/provoke state and official client/server version
evidence_basis:
  - S1
  - S2
  - S3
conflicts:
  - a server spectator viewport larger than the client screen can be intentional for movement, pathfinding and prefetch and is not by itself proof of excessive aggro range
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | `src/map/map_const.hpp`, monster target/search and spectator families | enlarged server viewport architecture is present | behavior intent inconclusive | medium |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | corresponding constants and monster logic | inherited architecture with donor drift | inconclusive | medium-low |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | same families | related viewport model | inconclusive | medium |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | `src/map/map_const.hpp`, monster acquisition/search families | constants are 8/6 client and 11/11 server maximum viewport; no per-Issue expected range exists | inconclusive | high for constants, low for defect |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | visible map viewport | client screen dimensions do not define authoritative server monster acquisition | not a direct target path | high |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_REFERENCE
system_boundary: named monster and fixed geometry -> server target acquisition/retention distances -> observed aggro transition
preconditions: []
steps: []
expected_observations: []
artifacts: []
cleanup: []
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: no authoritative expected acquisition/retention distances, named monster fixture or geometry is supplied; changing global viewport constants would test a hypothesis rather than the claim
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
rationale: Otheryn shares the cited enlarged server viewport, but no evidence establishes that this constant is the monster aggro range or that an 11x11 maximum viewport violates the intended game behavior
```

## Drift and unresolved questions

- Drift after pinned revision: exact constants can be rechecked, but applicability remains blocked by missing truth data.
- Minimum evidence needed:
  - named monster and official/reference server version;
  - exact flat-map geometry and line-of-sight blockers;
  - acquisition and retention distances in each direction;
  - behavior with floors, invisibility and challenge/provoke effects;
  - repeated observations or authoritative specification.
- Product fixes made by this audit: **none**.
