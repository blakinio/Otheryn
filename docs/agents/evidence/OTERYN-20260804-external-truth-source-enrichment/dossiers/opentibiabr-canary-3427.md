# Dossier — `opentibiabr/canary#3427`

## Identity

```yaml
canonical_key: opentibiabr/canary#3427
predecessor_row: 45
source_type: issue
prior_bucket: INSUFFICIENT
prior_truth_status: UNPROVEN
family: player-movement-desynchronization
research_status: COMPLETE
```

## Source claim

- Current title: `Character stuck`
- Source URL: `https://github.com/opentibiabr/canary/issues/3427`
- Exact source text: “Sometimes character is on other sqm and stuck on back sqm.”
- Claimed affected environment: Linux; no server revision, client version, coordinates, action sequence, latency, map tile or log.
- Claimed reproduction: only a user-attachment video is referenced; no textual deterministic steps exist.
- Claimed expected behavior: unknown beyond the general invariant that server and client agree on the player's authoritative tile and rejected movement is reconciled.

## Provenance

| ID | Source class | Publisher/repository | Revision/version | Retrieved | Claim supported | Role | Limitation/conflict |
|---|---|---|---|---|---|---|---|
| S1 | upstream Issue | `opentibiabr/canary` | Issue `#3427`, open/stale | 2026-08-04 | reports an intermittent visual/authoritative position mismatch | primary claim | no machine-readable attachment, coordinates, steps, client/version or logs |
| S2 | Issue discussion | same | one stale-bot comment | 2026-08-04 | no additional technical evidence was supplied | negative evidence | does not disprove the symptom |
| S3 | bounded repository search | five compared repositories | pinned audit revisions | 2026-08-04 | common movement, cancel-walk, tile and client reconciliation families exist | scope-location evidence | search cannot identify one failing path without a trigger or packet trace |

## Expected behavior

```yaml
expected_behavior_status: UNKNOWN
expected_behavior: UNKNOWN; the general position-consistency invariant is insufficient to distinguish walk rejection, map desynchronization, speed timing, floor change, teleport, push, pathfinding or client prediction failures
version_boundary: UNKNOWN
evidence_basis:
  - S1
  - S2
conflicts:
  - “on other sqm” and “stuck on back sqm” may describe client rendering, server position, path queue, movement cancellation or map collision; the source does not disambiguate
```

## Five-repository static comparison

| Repository | Revision | Paths/symbols searched | Observed state | Static assessment | Confidence |
|---|---|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | player movement, `internalMoveCreature`, walk cancellation and tile query families | relevant paths exist; no source trigger maps to a unique branch | inconclusive | low |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | same families | shared architecture with donor divergences; no deterministic comparison point | inconclusive | low |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | same families | inherited movement architecture; no exact symptom marker | inconclusive | low |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | server movement, protocol walk-cancel and tile state | many plausible paths; none can be classified from the source | inconclusive | low |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | local walk prediction, creature position and server reconciliation | client is potentially material, but the source client/build is unknown | inconclusive | low |

## Deterministic runtime plan

```yaml
plan_status: BLOCKED_REFERENCE
system_boundary: cannot be selected without knowing the triggering movement operation and client/server observation
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
blocker: source lacks client build, map position/tile stack, exact input sequence, network conditions, authoritative server
  position and packet/log evidence; unbounded movement fuzzing would not test the stated claim
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
rationale: the source does not define a falsifiable scenario, and the symptom spans server movement, map state, packet ordering
  and client prediction; selecting any one target path would be guesswork Runtime execution is reference-blocked because no
  deterministic expected result is supported.
```

## Drift and unresolved questions

- Drift after pinned revision: none can be evaluated against the undefined trigger.
- Minimum evidence needed to reopen:
  - client name/build and server SHA;
  - starting and ending coordinates plus tile stack IDs;
  - exact movement/action sequence and whether latency/loss was present;
  - server-side authoritative position and packet trace around the mismatch;
  - repeatability rate and a control case.
- Product fixes made by this audit: **none**.
