# World Reconstruction & Navigation

Shared ID: `OTS-20260813-world-reconstruction-navigation`.

## Goal

Extend the OTBM Atlas with a versioned evidence pipeline. Native Linux `blakinio/otclient` exports structured facts from its already-decoded map state; `blakinio/Otheryn` imports them, preserves provenance, compares them with canonical OTBM geometry, tracks coverage/connectivity, and prepares reviewable candidate corrections.

## Ownership

`blakinio/otclient` owns observation production, exact absolute positions, tile completeness, ordered observed contents, map deltas, non-secret provenance, and local live-state/pathfinding results.

`blakinio/Otheryn` owns Atlas ingestion, chunk storage, identity resolution, canonical diff, evidence consensus, coverage/frontier selection, world-connectivity modelling, global route goals, candidate-map generation, and Atlas evidence UI.

Live Track A/Track B runtime namespaces are not shared across repositories. Canonical `world.otbm` is never directly modified by the observation producer.

## Contract v1

P0 defines deterministic fixtures for four records:

- `tile_snapshot`: absolute x/y/z, `FULL|EMPTY|PARTIAL|UNKNOWN`, ordered observed things, source and non-secret producer provenance;
- `tile_delta`: later add/change/delete/update evidence;
- `transition_event`: observed before/after world-position transition;
- `navigation_action_result`: requested semantic route step plus decoded result state.

Absence of an observation remains `UNKNOWN`. Client/appearance identity is never assumed to equal OTBM/server identity.

## Evidence layers

For each position Atlas keeps independent `CANONICAL`, `OBSERVED`, `CONSENSUS`, and `CANDIDATE` layers. Diff states include `MATCH`, `MISSING_IN_CANONICAL`, `CONFLICT`, `OBSERVED_DYNAMIC_ONLY`, `IDENTITY_UNRESOLVED`, and `INSUFFICIENT_EVIDENCE`.

Identity resolution is explicitly `VERIFIED`, `AMBIGUOUS`, or `UNKNOWN`; unresolved identities are stored as evidence but cannot be silently promoted to canonical geometry.

## Navigation split

Atlas owns the global connectivity model and target selection. OTClient owns current local state and reuses its existing pathfinding primitives. Global output is semantic route intent rather than an authoritative sequence of input events; outcomes are accepted only from decoded resulting state.

## Delivery phases

1. P0 contract + deterministic producer/consumer fixtures.
2. P1 read-only OTClient observation recorder.
3. P2 Atlas ingest + provenance + identity resolver + canonical diff.
4. P3 consensus + coverage/frontier indexes + viewer layers.
5. P4 semantic connectivity/navigation graph.
6. P5 local navigator integration using existing OTClient pathfinding and verified result state.
7. P6 closed loop: target -> navigation -> observation -> Atlas update -> replan.
8. P7 deterministic reviewable candidate OTBM reconstruction.

## Codex

Codex is technically useful for bounded multi-file implementation/test loops in P1, P2, P4, P5 and P7. Chat/GitHub coordination is preferred for architecture, contract decisions, live PR/CI state and acceptance; material code should receive an independent validation pass.

Repository policy remains controlling: owner-funded Codex/API quota must not be consumed without explicit permission for that specific use. This project definition grants no such permission.

## Next milestone

Complete P0 under shared ID `OTS-20260813-world-reconstruction-navigation` with paired tasks in `blakinio/otclient` and `blakinio/Otheryn`. P1+ starts only after the v1 semantics and fixtures agree on both sides.