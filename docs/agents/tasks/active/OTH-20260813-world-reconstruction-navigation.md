---
task_id: OTH-20260813-world-reconstruction-navigation
status: ready
agent: ChatGPT
project_lane: otheryn-content
task_kind: programme-coordination
phase: implementation-dispatch
branch: main
base_branch: main
start_sha: dcca3773b1b7834d9151e6792e14540ed742764b
created: 2026-08-13T22:24:00+02:00
updated: 2026-08-16T23:20:00+02:00
risk: medium
related_pr: 427
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

## Canonical architecture

The current architecture is defined by:

- `docs/maps/world-reconstruction-navigation.md`
- `docs/maps/global-tibia-verification-coverage.md`

PR #427 merged this rebaseline as `dcca3773b1b7834d9151e6792e14540ed742764b` after exact-head `Required` run `31972843468 = SUCCESS` and zero review threads.

The authoritative live observation producer is Track A `official-client-re` / official native Linux Tibia client. Track B/open-source OTClient is not the producer or local navigator.

## Frozen programme decisions

- Atlas keeps independent `CANONICAL`, `REAL_TIBIA`, `COMPARISON`, `CANDIDATE` layers.
- Real Tibia evidence survives canonical-map changes and can be re-compared later.
- Verification and accessibility are separate dimensions.
- Global Coverage is a first-class Atlas product for humans and automated planning.
- Coverage distinguishes ordinary-player-verifiable space from special/admin/teleport-only or proven normal-player-unreachable space.
- Track A maintains/indexes observations; promoted changes align with Atlas 128x128 chunks.
- Atlas owns frontier scoring and semantic exploration targets, not blind physical input scripts.
- Track A owns official-client runtime/local execution and structural resulting-state verification.
- A larger official-client viewport is an accelerator, not a hard reconstruction dependency.
- Raw client/appearance IDs are never silently treated as OTBM server IDs.
- Asset-version refresh is separate maintenance and not a current architecture blocker.

## Current implementation dependency

Otheryn PR #426 currently owns active production-incremental Atlas implementation paths, including `tools/otbm_atlas/atlas.py`, `spatial.py`, `tile_inspector.py`, `production_*`, `environment_*` and related tests/workflows.

Do not dispatch Real Tibia ingest/coverage implementation onto overlapping #426 paths until its live state/ownership is revalidated and a non-overlapping package or post-merge implementation surface is chosen.

## First integration milestone

```text
exact official Linux client
-> structurally verified absolute tile facts
-> Track A local observation index/deduplication
-> promoted sanitized changed 128x128 chunk bundle
-> Atlas REAL_TIBIA ingest
-> compare with CANONICAL
-> render Global Coverage / Difference state
```

Autonomous traversal is explicitly later.

## Acceptance still open

- Track A absolute ordered tile observations are physically/structurally proven under current evidence gates.
- Track A observation index/export is implemented and validated.
- Atlas Real Tibia ingest/comparison/coverage is implemented without colliding with #426.
- Global Coverage UI exposes verified/unverified/accessibility state.
- Machine-readable frontier/exploration queue is implemented.
- Later closed-loop mission -> Track A execution -> observation -> Atlas replan is proven.
- Candidate OTBM correction remains deterministic and review-gated.

## Context checkpoint

```yaml
checkpoint_version: 3
updated_at: 2026-08-16T23:20:00+02:00
status: ready
main_after_reconciliation: dcca3773b1b7834d9151e6792e14540ed742764b
reconciliation_pr: 427
reconciliation_ci: 31972843468
shared_coordination_id: OTS-20260813-world-reconstruction-navigation
cross_repo_producer_contract:
  repository: blakinio/otclient
  task: OTC-20260816-world-observation-atlas-boundary
proven:
  - Track A official-client-re is the live producer authority.
  - Otheryn has exact canonical tile facts and 128x128 chunk foundations.
  - Global Coverage / Real Tibia / accessibility / frontier semantics are now durable on main.
  - PR #426 is the current overlapping Atlas production implementation owner.
unknown:
  - Exact producer index engine and promoted bundle encoding beyond required semantics.
  - Final Global Coverage visual language.
blockers: []
next_action: Revalidate live PR #426; once its ownership no longer blocks the required files, create the bounded Atlas Real Tibia ingest + comparison + coverage-index implementation task, while Track A separately implements its observation index/export.
```
