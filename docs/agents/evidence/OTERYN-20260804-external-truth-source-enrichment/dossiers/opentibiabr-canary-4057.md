# Dossier — `opentibiabr/canary#4057`

## Identity

```yaml
canonical_key: opentibiabr/canary#4057
predecessor_row: 15
source_type: issue
prior_bucket: REPRO
prior_truth_status: PARTIALLY_PROVEN
family: way-of-the-monk-shrine-map
research_status: COMPLETE
```

## Source claim

The Three-Fold Path chain is blocked by five material defects: unreachable Respect and Eternity approaches, an unopenable Serenity door, and two shrine actions registered on floor 1 instead of floors 13 and 15. The source supplies exact coordinates, item IDs, a bounded reachability argument and an official-client minimap comparison.

## Provenance

| ID | Source | Revision/version | Claim supported | Limitation |
|---|---|---|---|---|
| S1 | `opentibiabr/canary#4057` | opened 2026-08-02 | exact map tiles, door item, shrine coordinates and official 15.25 minimap comparison | external minimap/tile dumps are described but not committed as audit artifacts |
| S2 | Otheryn shrine script | `1f316400053f489e58608d13961069835871ab0e` | Empathy is registered at `(32532,31569,1)` and Power at `(32890,32352,1)` | script alone does not prove map binary coordinates |
| S3 | source runtime report | source server | changing floors and map obstacles makes the shrines usable | not independently reproduced by this audit |

## Expected behavior

```yaml
expected_behavior_status: PROVEN
expected_behavior: all ten shrines are reachable and usable in strict order; Empathy action is bound at z=13, Power at z=15, Serenity opens by ordinary use, and Respect/Eternity approaches match walkable official map geometry
version_boundary: Way of the Monk content aligned with official client 15.25 assets
evidence_basis: [S1, S2]
conflicts: []
```

## Five-repository static comparison

| Repository | Revision | Observed state | Assessment |
|---|---|---|---|
| `opentibiabr/canary` | `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32` | source Issue demonstrates map/script defects | affected |
| `zimbadev/crystalserver` | `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e` | content lineage requires map/script coordinate comparison | inconclusive |
| `blakinio/canary` | `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f` | inherited global datapack/map lineage | likely affected; exact map dump pending |
| `blakinio/Otheryn` | `1f316400053f489e58608d13961069835871ab0e` | exact two wrong z-values are present; map binary must be dumped for remaining three defects | affected at least for script |
| `blakinio/otclient` | `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad` | no client fix target; useful for movement/use validation | not directly affected |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: clean quest player and source map -> ordered shrine traversal/use -> storage progression and rewards
preconditions:
  - isolated clean Otheryn map/database
  - test monk at required levels with ShrinesCount initialized
steps:
  - dump exact tiles/items at every source coordinate and compare with the supplied official-minimap expectations
  - perform bounded reachability checks to Respect, Serenity and Eternity
  - attempt each shrine in order and record action dispatch, storage transition and reward
  - verify Empathy at z=13 and Power at z=15 while confirming no action is bound at the erroneous z=1 positions
expected_observations:
  - pinned target fails the two action registrations and any source-confirmed map obstacles
artifacts:
  - shrine-tile-dump.json
  - reachability.json
  - shrine-sequence.jsonl
  - server.log
cleanup:
  - discard quest player/database state
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: map-binary inspection/runtime harness not yet executed
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
truth_status: PROVEN
static_conclusion: TARGET_AFFECTED
runtime_conclusion: PENDING
owner_action: OPEN_FIX_PROGRAM
confidence: high
rationale: Otheryn contains the two objectively wrong shrine floors, while the source provides exact map/item evidence for three additional blockers; runtime/map dump should determine the complete repair set without changing this audit task
```

## Drift and unresolved questions

- Verify whether Otheryn's final map blob exactly retains all 13 blocking pieces and Serenity item `5124` without action/unique ID.
- Treat cosmetic snowy-mountain fill separately from quest-blocking acceptance.
- Product fixes made by this audit: **none**.
