# Dossier — `zimbadev/crystalserver#647`

## Identity

```yaml
canonical_key: zimbadev/crystalserver#647
predecessor_row: 100
source_type: issue
prior_bucket: REPRO
prior_truth_status: UNPROVEN
family: abdendriel-library-books
research_status: COMPLETE
```

## Source claim

All Ab'Dendriel library shelves were empty. Discussion points to a community library index and later claims the world map was updated with all Tibia library texts, but does not identify an immutable fix commit.

## Expected behavior

```yaml
expected_behavior_status: PARTIALLY_PROVEN
expected_behavior: every Ab'Dendriel library shelf intended to contain readable books exposes the correct book items/texts at the correct map positions; empty/decorative shelves remain intentionally empty
version_boundary: world-map/library content generation used by the audited target
evidence_basis: [zimbadev/crystalserver#647, issue discussion]
conflicts:
  - reference is a community wiki rather than primary map data
  - later “fixed” assertion lacks commit, coordinates and before/after inventory
```

## Five-repository static comparison

| Repository | Revision | Assessment |
|---|---|---|
| upstream Canary | pinned | separate world map/library data | comparison requires map extraction |
| CrystalServer | pinned | source reports missing books; later unpinned map update claims repair | pinned state inconclusive |
| `blakinio/canary` | pinned | separate inherited map snapshot | inconclusive |
| Otheryn | pinned | binary map/book text inventory required; source names only the city/library | static inconclusive |
| OTClient | pinned | renders/reads map book descriptions | observer only |

## Deterministic runtime plan

```yaml
plan_status: READY
system_boundary: Ab'Dendriel library map shelves -> readable item/text inventory -> client look/read result
preconditions:
  - authoritative coordinate/shelf/book list for the chosen map version
steps:
  - extract every shelf/tile/book/text in Ab'Dendriel library polygons from all compared map snapshots
  - log in and look/use each expected book and intentional empty shelf
  - compare later Crystal map commit only after its immutable revision is identified
expected_observations:
  - target inventory matches the versioned reference with no missing/duplicate/misplaced texts
artifacts: [abdendriel-library-inventory.json, map-diff.json, look-results.jsonl]
cleanup: [none beyond isolated world]
safety:
  production_access: false
  persistent_live_state: false
  external_side_effects: false
blocker: authoritative versioned shelf/book coordinate list and claimed fix commit remain required for final pass/fail
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
truth_status: PARTIALLY_PROVEN
static_conclusion: STATIC_INCONCLUSIVE
runtime_conclusion: PENDING
owner_action: RESEARCH_REQUIRED
confidence: medium
rationale: the source establishes an all-empty library symptom and a later unverified repair claim; Otheryn must be checked by extracting its actual map/text inventory against a versioned reference
```

## Drift and unresolved questions

- Identify the exact Crystal world-map commit referenced by the “fixed already” comment.
- Product fixes made by this audit: **none**.
