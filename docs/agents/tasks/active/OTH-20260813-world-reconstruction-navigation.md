---
task_id: OTH-20260813-world-reconstruction-navigation
status: investigating
agent: ChatGPT
project_lane: otheryn-content
task_kind: programme-coordination
phase: current-main-reconciliation
branch: docs/OTH-20260816-global-verification-coverage-model
base_branch: main
start_sha: 468392d304dc87e1d9d67ebe3ec44b743ec1beae
created: 2026-08-13T22:24:00+02:00
updated: 2026-08-16T23:09:00+02:00
risk: medium
related_pr: null
shared_coordination_id: OTS-20260813-world-reconstruction-navigation
owned_paths:
  - docs/agents/tasks/active/OTH-20260813-world-reconstruction-navigation.md
  - docs/maps/world-reconstruction-navigation.md
  - docs/maps/global-tibia-verification-coverage.md
cross_repo_tasks:
  - OTC-20260816-world-observation-atlas-boundary
execution_mode: chat-github
decomposition_decision: split
---

# World reconstruction and Global Tibia verification programme

## Rebaseline decision

The original 2026-08-13 design is superseded. The current authoritative live producer is Track A `official-client-re` in `blakinio/otclient`, using the official native Linux Tibia client. The open-source OTClient/Track B runtime is not the producer or local navigator for this programme.

The programme now has two durable sides:

1. Track A produces exact-client semantic observations and maintains a local/indexed observation history under its own runtime and evidence governance.
2. Otheryn OTBM Atlas consumes separately promoted, sanitized observation bundles and owns comparison, visualization, coverage, access classification, frontier selection and candidate-map work.

Canonical `world.otbm` is never directly mutated from live observations.

## Current Atlas baseline

Current Otheryn `main` already provides deterministic canonical tile facts, exact per-chunk tile-inspector data and 128x128 spatial chunking. PR #426 owns the active production-incremental Atlas implementation paths and must not be overlapped by this documentation reconciliation.

The future Real Tibia evidence layer should align with the existing 128x128 chunk coordinate system so changed observation chunks can be ingested and compared incrementally.

## Current Track A baseline

Track A is organized as parallel draft-only research lanes with coordinator promotion:

- `P0-STATE`: authoritative player/world semantic reads;
- `P1-BRIDGE`: stable read-only bridge/API and reacquisition health;
- `P2-NETWORK`: protocol/network semantics;
- `RUNTIME`: the only normal owner/provider of physical persistent login/display/input/gameplay/relogin evidence;
- `COVERAGE-AUDIT`: quantitative evidence/coverage reconciliation.

The current world-observation milestone depends primarily on P0-STATE/worldmap structural evidence plus the coordinator-promoted P1 bridge. A larger worldmap viewport is an accelerator, not a hard requirement; an exact smaller viewport may be accumulated by traversal when absolute coordinates and tile semantics are reliable.

## Core data model

Atlas keeps independent layers for each world position:

- `CANONICAL`: current Otheryn OTBM facts;
- `REAL_TIBIA`: promoted Track A observation facts;
- `COMPARISON`: result of comparing the two at the current canonical revision;
- `CANDIDATE`: reviewable proposed correction, never automatic canonical mutation.

Real Tibia observations remain durable independently of comparison results. If canonical OTBM changes later, Atlas recomputes comparison against preserved Real Tibia evidence without requiring the player to revisit the location.

## Verification states

Minimum comparison/verification states:

- `UNOBSERVED`
- `OBSERVED`
- `PARTIAL`
- `IDENTITY_UNRESOLVED`
- `VERIFIED_MATCH`
- `VERIFIED_DIFFERENT`
- `CONFLICT`
- `STALE`

`OBSERVED` and `VERIFIED` are distinct. Verification requires enough complete observation and identity evidence to perform the applicable canonical comparison. Absence of observation remains `UNKNOWN`/`UNOBSERVED`, never `EMPTY`.

## Access states

Verification and accessibility are independent axes. Minimum access states:

- `UNKNOWN`
- `NORMAL_REACHABLE`
- `CONDITIONALLY_REACHABLE`
- `SPECIAL_ACCESS_REQUIRED`
- `ADMIN_OR_TELEPORT_REQUIRED`
- `PROVEN_UNREACHABLE_BY_NORMAL_PLAYER`

A tile may therefore be unobserved but intentionally excluded from normal-player exploration. One failed route attempt is not proof of unreachability.

Observation provenance should preserve the verified acquisition method where known, such as normal traversal, conditional traversal, transition, teleport, admin teleport or passive world stream. Being observable does not imply a normal walk edge exists.

## Global Coverage product

Atlas must expose a first-class `Global Coverage` view for both humans and automated planning. At close zoom it can show tile-level state; at lower zoom it aggregates by existing 128x128 chunks.

Required filters include at least:

- verified match;
- verified different;
- unobserved;
- partial;
- identity unresolved;
- conflict;
- normal reachable;
- conditional;
- special/admin access;
- access unknown.

Chunk summaries should expose totals such as observed, fully comparable, verified match/different, unresolved, unobserved and accessibility classes.

Coverage metrics must distinguish total-world coverage from normal-player-verifiable coverage. The programme must never imply that inaccessible/admin-only tiles can necessarily be verified by an ordinary character.

## Exploration frontier and queue

Atlas owns global coverage prioritization. It identifies frontier regions between verified/observed space and useful unobserved space, scores them and publishes a machine-readable exploration queue.

A target should describe the goal, not dictate blind input events. Example fields:

- target chunk / bounds / floor;
- suggested entry coordinate when justified;
- reason (`UNOBSERVED_FRONTIER`, `VERIFY_DIFFERENCE`, `RESOLVE_CONFLICT`, etc.);
- expected new coverage;
- travel/access cost or uncertainty;
- priority.

The planner should prefer reachable, high-value new coverage and penalize repeated failure or known special/admin-only access. It must not endlessly retry tiles already classified as unavailable to a normal player.

## Track A to Atlas transfer

Track A should maintain a durable local world-observation index optimized for deduplication and history (SQLite or equivalent is an implementation choice). It may export deterministic changed-chunk bundles matching Atlas 128x128 chunking.

Atlas does not need a live direct network connection to the client in the first implementation. The first integration boundary is promoted sanitized artifacts/bundles; streaming/service transport can be added later without changing semantics.

The same observation index should support both human visualization and agent planning. Atlas UI and automated frontier selection read the same canonical coverage state rather than maintaining separate truths.

## Identity rule

Raw client/appearance identity is never silently treated as OTBM server identity. Asset-version refreshes do not remove this rule. Identity resolution remains explicit: `VERIFIED`, `AMBIGUOUS`, or `UNKNOWN`.

## Navigation boundary

Atlas owns global target selection and semantic connectivity. Track A owns actual local official-client state, native action execution and resulting-state verification. Atlas may request an exploration mission; it does not own the physical runtime and should not emit blind keyboard/mouse sequences.

A transition or action is accepted only from structurally verified resulting state under current Track A evidence/runtime gates.

## Updated delivery streams

The programme is no longer a strict P0->P7 line. Work proceeds in parallel streams:

1. Track A state: authoritative player/world coordinates and semantic reads.
2. Track A worldmap: ordered tile contents/storage/coordinate semantics.
3. Track A runtime: persistent physical session and causal/relogin validation.
4. Atlas production: current incremental canonical tile-facts pipeline (#426).
5. Observation integration: Track A index/bundle -> Atlas Real Tibia layer.
6. Coverage/access/frontier: Global Coverage UI + machine-readable exploration queue.
7. Navigation/exploration: Atlas mission -> Track A execution -> new observations -> replan.
8. Candidate reconstruction: deterministic reviewable OTBM corrections from verified evidence.

## First end-to-end milestone

The first integration E2E does not require autonomous walking. It is:

```text
exact official Linux client
-> structurally read current absolute world tiles
-> persist/index MAP_OBSERVATION_V1-compatible observations
-> export promoted sanitized changed chunk(s)
-> Atlas ingest as REAL_TIBIA
-> compare against CANONICAL
-> show verification/coverage state
```

Only after this is reliable should closed-loop autonomous exploration be treated as the next milestone.

## Acceptance inventory

- [ ] Track A can produce absolute, ordered, structurally verified tile observations without OCR or guessed IDs.
- [ ] Track A world-observation index deduplicates unchanged facts while preserving provenance/history.
- [ ] Deterministic changed-chunk export aligns with Atlas 128x128 chunks.
- [ ] Atlas stores Real Tibia evidence independently from comparison result.
- [ ] Atlas exposes Canonical, Real Tibia, Difference and Global Coverage views.
- [ ] Verification and accessibility are independent states.
- [ ] Normal-player coverage can exclude proven special/admin-only areas without pretending those tiles were verified.
- [ ] Atlas recomputes comparison after canonical-map changes without requiring re-observation.
- [ ] Frontier/queue identifies useful remaining verification targets for humans and agents.
- [ ] Track A receives semantic exploration missions rather than blind input scripts.
- [ ] Candidate OTBM corrections remain deterministic, provenance-linked and separate from canonical world.otbm until explicit acceptance.

## Context checkpoint

```yaml
checkpoint_version: 2
updated_at: 2026-08-16T23:09:00+02:00
status: investigating
branch: docs/OTH-20260816-global-verification-coverage-model
base_main: 468392d304dc87e1d9d67ebe3ec44b743ec1beae
shared_coordination_id: OTS-20260813-world-reconstruction-navigation
proven:
  - Track A official-client-re is the authoritative live observation producer; Track B is excluded.
  - Otheryn main has deterministic per-tile canonical facts and 128x128 chunk/spatial foundations.
  - PR #426 owns active Atlas production-incremental implementation paths and must not be overlapped here.
  - Track A uses separate P0-STATE, P1-BRIDGE, RUNTIME and related lanes with coordinator promotion.
owner_decisions:
  - Atlas must have selectable Real Tibia and coverage/difference presentation.
  - Verified Global Tibia tiles must remain visibly marked.
  - The agent should index discoveries and deliver changed indexed data for Atlas comparison.
  - Coverage must model ordinary-player inaccessible areas, including locations requiring GM/admin teleport or other special access.
  - Human and agent must both be able to see/select what remains unverified.
  - Asset version skew is not a programme blocker because the Atlas assets will be refreshed separately; raw client ID still never equals OTBM server ID by assumption.
unknown:
  - Exact storage engine for the Track A local index; SQLite is preferred but not yet frozen.
  - Exact bundle file schema beyond MAP_OBSERVATION_V1-compatible semantics and 128x128 chunk alignment.
  - Final UI visual language for coverage/access states.
blockers: []
next_action: Merge this programme reconciliation, then dispatch non-overlapping implementation tasks for Track A observation-index/export and Atlas Real-Tibia ingest/coverage after revalidating current implementation ownership.
```
