---
task_id: OTH-20260813-world-reconstruction-navigation
status: investigating
agent: ChatGPT
project_lane: otheryn-content
task_kind: programme-coordination
phase: architecture-bootstrap
branch: docs/OTH-20260813-world-reconstruction-navigation
base_branch: main
start_sha: 8a7d1b22a12ebc6245765f58f321a0f9921a9ca0
created: 2026-08-13T22:24:00+02:00
updated: 2026-08-13T22:24:00+02:00
risk: medium
related_pr: null
shared_coordination_id: OTS-20260813-world-reconstruction-navigation
owned_paths:
  - docs/agents/tasks/active/OTH-20260813-world-reconstruction-navigation.md
  - docs/maps/world-reconstruction-navigation.md
cross_repo_tasks:
  - OTC-20260813-map-observation-export
execution_mode: chat-github
decomposition_decision: split
---

# World reconstruction and navigation program

## Objective

Create a durable cross-repository program in which `blakinio/otclient` exports structured, non-secret observations from its already-decoded map state and `blakinio/Otheryn` OTBM Atlas consumes those observations to compare canonical geometry, track evidence/coverage, model world connectivity, select useful exploration targets, and build reviewable candidate OTBM corrections.

## Boundaries

- OTClient is the observation producer and local runtime owner.
- Otheryn/OTBM Atlas is the canonical-map consumer, evidence model and global planning owner.
- Live Track A/Track B runtime namespaces are never shared across repositories.
- Canonical `world.otbm` is never mutated directly from a live observation.
- Secrets and authentication/session material are excluded from exports.
- Missing observations remain UNKNOWN, not EMPTY.
- Client/appearance IDs are not assumed to equal OTBM/server IDs.
- Dynamic/stateful world objects are not promoted to static geometry without explicit evidence policy.

## Program phases

1. P0: versioned observation/navigation contract and deterministic fixtures in both repositories.
2. P1: read-only OTClient observation recorder for full tile snapshots and map deltas.
3. P2: Atlas observation ingest, identity resolution, canonical diff and provenance.
4. P3: consensus, coverage/frontier indexes and Atlas evidence layers.
5. P4: semantic world navigation graph with ordinary movement and explicit interaction/transition edges.
6. P5: OTClient local navigator that reuses existing pathfinding and verifies each semantic route step from decoded server state.
7. P6: closed-loop frontier exploration: Atlas target -> local navigation -> new observations -> replanning.
8. P7: reviewable candidate OTBM reconstruction with canonical map unchanged until explicit acceptance.

## Acceptance inventory

- [ ] P0 producer and consumer agree on one versioned schema and deterministic fixtures.
- [ ] Every observation retains exact producer revision and non-secret provenance.
- [ ] FULL, EMPTY, PARTIAL and UNKNOWN tile knowledge remain distinct.
- [ ] Identity mapping status is explicit: VERIFIED, AMBIGUOUS or UNKNOWN.
- [ ] Atlas can classify canonical-vs-observed state without silently changing canonical geometry.
- [ ] Navigation model distinguishes ordinary walk edges from interactions and floor/teleport transitions.
- [ ] A transition is VERIFIED only from observed before/after position evidence.
- [ ] Local navigation verifies live state after interaction/movement and reports failure for replanning.
- [ ] Coverage/frontier selection can identify a reachable high-value unknown/conflicting area.
- [ ] Closed-loop E2E is proven on the required native Linux runtime before the program is called complete.
- [ ] Candidate patch output is deterministic, provenance-linked and separate from canonical `world.otbm`.

## Codex routing

Codex is a good fit for bounded multi-file implementation/test loops in P1, P2, P4, P5 and P7. Chat/GitHub coordination remains the preferred mode for architecture, contract decisions, live PR/CI state and acceptance. A fresh validator should independently audit material implementation packages.

Repository policy remains controlling: owner-funded Codex/API quota must not be consumed unless the owner explicitly authorizes that specific use. This task does not grant that permission.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-13T22:24:00+02:00
status: investigating
branch: docs/OTH-20260813-world-reconstruction-navigation
shared_coordination_id: OTS-20260813-world-reconstruction-navigation
proven:
  - Current OTBM Atlas provides chunked semantic map processing and spatial viewer foundations.
  - Current OTClient exposes semantic Tile/Map state and local pathfinding primitives suitable for a producer/local-navigator layer.
  - Otheryn PR #381 does not own this program's documentation paths.
  - Track isolation requires live runtime ownership to remain inside the owning OTClient track and permits deliberate promotion of stable repository-owned evidence/contracts.
derived:
  - A file-based versioned observation contract is the lowest-coupling first integration boundary.
unknown:
  - Exact v1 wire/storage encoding until P0 fixtures are implemented and benchmarked.
conflicts: []
blockers: []
next_action: Merge the project definition, then create and execute the paired OTClient P0 producer-contract task without touching Track B live runtime ownership.
```