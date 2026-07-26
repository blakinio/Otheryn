# OTH-20260727 — MGE-004 composition root lifecycle

Status: **implementing**

Issue: `#161`
Branch: `dudantas/mge-004-composition-root-lifecycle`
Pull request: pending
Target repository: `blakinio/Otheryn`
Start main: `64ad965eee40f62ff996980fd8a0d329245c519f`

## Objective

Add a bounded module composition root with deterministic dependency-order start, reverse rollback/stop, readiness and test isolation, then transfer only MonsterComputeService into explicit lifecycle ownership without changing its configuration or startup phase.

## Owned paths

- `src/modules/module_lifecycle.hpp`
- `src/canary_server.hpp`
- `src/canary_server.cpp`
- `tests/unit/modules/CMakeLists.txt`
- `tests/unit/modules/mge_004_module_lifecycle_test.cpp`
- `docs/architecture/module-composition-root-and-lifecycle.md`
- this task record

## Safety boundaries

- no gameplay extraction;
- no dynamic plugin ABI or runtime hot toggle;
- no Lua-defined lifecycle;
- no migration of Dispatcher, ThreadPool, database, Lua environment, Game, protocol listeners or persistence;
- no protocol wire, schema, map, datapack, or deployment change;
- no lifecycle ownership claim for unregistered modules.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-27T00:40:00+02:00"
head: "f5756759a4c79d76dd7aab426f0b5c6ac2863fbb"
branch: "dudantas/mge-004-composition-root-lifecycle"
pr: null
status: "implementing"
context_routes:
  - "docs/architecture/modular-game-engine-and-profiles.md"
  - "docs/architecture/current-engine-ownership-and-dependencies.md"
  - "docs/architecture/module-registry-and-profile-validation.md"
  - "docs/architecture/module-composition-root-and-lifecycle.md"
owned_paths:
  - "src/modules/module_lifecycle.hpp"
  - "src/canary_server.hpp"
  - "src/canary_server.cpp"
  - "tests/unit/modules/CMakeLists.txt"
  - "tests/unit/modules/mge_004_module_lifecycle_test.cpp"
  - "docs/architecture/module-composition-root-and-lifecycle.md"
  - "docs/agents/tasks/active/OTH-20260727-mge004-composition-root-lifecycle.md"
proven:
  - "MGE-003 registry validation is merged and archived on main."
  - "No open PR owned MGE-004 paths at task start."
  - "ModuleCompositionRoot validates the graph, starts registered participants in dependency order, rolls back and stops in reverse, records stop errors and exposes no shared mutable lifecycle state."
  - "Focused tests cover ordering, rollback, idempotence, stop failure, registration rejection, readiness, isolation and invalid graph rejection."
  - "CanaryServer owns one composition root and registers MonsterComputeService under logical module Creatures."
  - "Monster compute configuration, startup location and diagnostics are preserved."
  - "MonsterComputeService shutdown is idempotent, preserving the legacy process-level fallback."
derived:
  - "A single selected participant is sufficient to prove explicit lifecycle ownership without broad infrastructure migration."
unknown:
  - "Exact compile and runtime smoke result on the integrated head."
conflicts: []
first_failure:
  marker: null
  result: "NOT_RUN"
  evidence: "Repository validation has not run on the integrated MGE-004 head."
rejected_hypotheses:
  - "Move all singleton services into the root in one package."
  - "Treat every MGE-003 descriptor as lifecycle-owned."
  - "Combine lifecycle foundation with Bank gameplay extraction."
changed_paths:
  - "docs/agents/tasks/active/OTH-20260727-mge004-composition-root-lifecycle.md"
  - "docs/architecture/module-composition-root-and-lifecycle.md"
  - "src/canary_server.cpp"
  - "src/canary_server.hpp"
  - "src/modules/module_lifecycle.hpp"
  - "tests/unit/modules/CMakeLists.txt"
  - "tests/unit/modules/mge_004_module_lifecycle_test.cpp"
validation:
  focused_tests: "NOT_RUN"
  full_ci: "NOT_RUN"
  required: "NOT_RUN"
blockers: []
next_action: "Open the draft PR, run exact-head CI, fix the first compile/test failure, then complete live audits and merge with expected-head protection."
```
