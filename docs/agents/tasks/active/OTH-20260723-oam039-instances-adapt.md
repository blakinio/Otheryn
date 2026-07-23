---
task_id: OTH-20260723-oam039-instances-adapt
status: validating
branch: dudantas/oam-039-instances-adapt
base_branch: main
created: 2026-07-23
updated: 2026-07-23
related_pr: "81"
owned_paths:
  - docs/agents/tasks/active/OTH-20260723-oam039-instances-adapt.md
  - docs/oam-039-instances-adapt.md
  - src/game/instance/**
  - src/game/CMakeLists.txt
  - tests/unit/game/instance/**
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/game/instance/**
  - src/game/CMakeLists.txt
  - tests/unit/game/instance/**
  - tests/unit/game/CMakeLists.txt
optional_reads: []
---

# OAM-039 Instances target adaptation

## Goal

Adapt the bounded canonical `instances` subsystem into clean Otheryn without importing legacy cross-module runtime wiring or map-specific data as if it were target truth.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T13:00:00+02:00
head: ed91b095763dd989d85f5d3545cd7aa2223a122e
branch: dudantas/oam-039-instances-adapt
pr: 81
status: validating
context_routes:
  - cpp-runtime
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/OTH-20260723-oam039-instances-adapt.md
  - docs/oam-039-instances-adapt.md
  - src/game/instance/**
  - src/game/CMakeLists.txt
  - tests/unit/game/instance/**
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is a275f1d788b50164ffc79b6f6143e13b9150c82e.
  - Canary OAM-039 preflight merged as 5c0613fd853e85421a89f661e9b3774c4dd730ff and selected canonical instances as an ADAPT candidate.
  - Clean Otheryn and fresh upstream baseline 7323503b3dc61ed86bf1f04a611b2d0aec64b35a lacked canonical InstanceManager roots.
  - Legacy Canary provides a staged tested donor for strong ids region pool lifecycle stable creature ownership binder liveness and bounded arena consumer.
  - Canonical instances depends only on completed world-map-runtime and owns src/game/instance/**; Game Creature spawn spectator combat Lua admin map content and physical-client surfaces are interaction boundaries rather than owned migration paths.
  - The target adaptation adds ten canonical source files under src/game/instance and registers the three translation units in src/game/CMakeLists.txt.
  - Focused target tests cover region allocation lifecycle quarantine ownership inheritance binder rollback scoped-event liveness and bounded arena behavior.
  - The clean target deliberately does not import legacy data-canary arena coordinates; InstanceArenaService configuredRegions is empty by default and operates only against explicitly configured regions.
  - No Game Creature Lua talkaction protocol client map asset schema or persistence path is changed by the bounded adaptation.
derived:
  - OAM-039 final disposition is instances ADAPT if exact-head target build and tests pass after any concrete target-API compatibility repairs limited to the owned package.
  - Default target instance runtime remains dormant/fail-closed without a separately owned Game/runtime configuration integration.
  - The adapted package establishes the reusable lifecycle and isolation foundation without claiming complete production instance activation.
unknown:
  - Exact compile/API compatibility of the legacy-derived canonical package against current Otheryn until target CI executes.
  - Whether target CI reveals a concrete owned-package compatibility defect requiring a bounded source repair.
  - Exact final target merge SHA and platform-gate evidence.
conflicts: []
first_failure:
  marker: none
  evidence: Target CI has not executed on the adapted package yet.
rejected_hypotheses:
  - Classify as REUSE; clean target and fresh upstream lacked the canonical InstanceManager roots.
  - Copy legacy cross-module Game Creature Lua or talkaction wiring; those are interaction boundaries outside canonical ownership.
  - Import hard-coded data-canary arena coordinates; map content is outside OAM-039 and target map placement requires separate evidence.
changed_paths:
  - docs/agents/tasks/active/OTH-20260723-oam039-instances-adapt.md
  - docs/oam-039-instances-adapt.md
  - src/game/instance/instance_id.hpp
  - src/game/instance/instance_region_pool.hpp
  - src/game/instance/instance_region_pool.inl
  - src/game/instance/instance_region_pool.cpp
  - src/game/instance/instance_manager.hpp
  - src/game/instance/instance_manager.cpp
  - src/game/instance/instance_creature_binder.hpp
  - src/game/instance/instance_scoped_event.hpp
  - src/game/instance/instance_arena_service.hpp
  - src/game/instance/instance_arena_service.cpp
  - src/game/CMakeLists.txt
  - tests/unit/game/instance/instance_region_pool_test.cpp
  - tests/unit/game/instance/instance_manager_test.cpp
  - tests/unit/game/instance/instance_creature_binder_test.cpp
  - tests/unit/game/instance/instance_scoped_event_test.cpp
  - tests/unit/game/instance/instance_arena_service_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: canonical ownership and donor boundary analysis
    result: PASS
    evidence: target package is restricted to canonical instance sources tests and build registration with cross-module interactions excluded
  - command: clean-target map adaptation
    result: PASS
    evidence: legacy data-canary coordinates are not imported and default arena configuration is fail-closed
blockers: []
next_action: Require exact-current-head autofix CI Required and full platform tests on PR 81, repair only concrete owned-package target incompatibilities, then audit review state and target-main drift before expected-head squash merge.
```
