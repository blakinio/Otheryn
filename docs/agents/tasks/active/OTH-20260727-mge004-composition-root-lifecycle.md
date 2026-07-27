# OTH-20260727 — MGE-004 composition root lifecycle

Status: **validating**

Issue: `#161`
Branch: `dudantas/mge-004-composition-root-lifecycle`
Pull request: `#162`
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
updated_at: "2026-07-27T09:37:22+02:00"
head: "6a355962acf525f9bc02e97014bc73014f4ae21b"
branch: "dudantas/mge-004-composition-root-lifecycle"
pr: "https://github.com/blakinio/Otheryn/pull/162"
status: "validating"
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
  - "PR #162 is open, ready for review and mergeable at head 6a355962acf525f9bc02e97014bc73014f4ae21b."
  - "ModuleCompositionRoot validates the graph, starts registered participants in dependency order, rolls back and stops in reverse, records stop errors and isolates root instances."
  - "Focused tests cover ordering, rollback, idempotence, stop failure, registration rejection, readiness, isolation and invalid graph rejection."
  - "CanaryServer registers only MonsterComputeService under logical module Creatures while preserving its configuration, startup phase and diagnostics."
  - "CI 30223667513 passed fast checks, Lua, Linux debug/release, macOS, Docker, Linux tests and available runtime smoke checks."
  - "Windows Solution job 89850437092 passed the MSBuild solution build."
  - "Windows CMake job 89850437085 passed Run CMake and failed later while installing MariaDB before runtime smoke."
  - "autofix.ci 30223667422 passed on head 6a355962acf525f9bc02e97014bc73014f4ae21b."
derived:
  - "The Windows CMake failure is infrastructure-only because compilation completed before MariaDB installation failed."
  - "A fresh exact-head validation is required after synchronizing the branch with current main."
unknown:
  - "Whether the two main commits since the branch merge base conflict with any of the seven owned paths."
  - "Whether the Windows MariaDB installation succeeds on the next exact-head CI attempt."
conflicts: []
first_failure:
  marker: "CI 30223667513 / job 89850437085 / Install MariaDB for smoke test"
  evidence: "Windows Run CMake passed; MariaDB installation failed before smoke, while all other completed platform builds, tests and smoke checks passed."
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
  - command: "autofix.ci 30223667422"
    result: "PASS"
    evidence: "Completed successfully on head 6a355962acf525f9bc02e97014bc73014f4ae21b."
  - command: "CI 30223667513 fast checks and Lua"
    result: "PASS"
    evidence: "Formatting, analysis and Lua tests completed successfully."
  - command: "CI 30223667513 Linux debug"
    result: "PASS"
    evidence: "Compile, Canary runtime smoke and full unit tests completed successfully."
  - command: "CI 30223667513 Linux release"
    result: "PASS"
    evidence: "Compile plus Canary and Global datapack runtime smoke completed successfully."
  - command: "CI 30223667513 macOS"
    result: "PASS"
    evidence: "Compile and Canary runtime smoke completed successfully."
  - command: "CI 30223667513 Docker"
    result: "PASS"
    evidence: "Image build and validation completed successfully."
  - command: "CI 30223667513 Windows Solution job 89850437092"
    result: "PASS"
    evidence: "MSBuild solution build and artifact upload completed successfully."
  - command: "CI 30223667513 Windows CMake job 89850437085"
    result: "BLOCKED"
    evidence: "Run CMake passed; MariaDB installation failed before smoke and artifact steps."
  - command: "Required 30223667420"
    result: "BLOCKED"
    evidence: "Aggregate failed because CI 30223667513 contained the Windows MariaDB infrastructure failure."
  - command: "compare main...dudantas/mge-004-composition-root-lifecycle"
    result: "BLOCKED"
    evidence: "Branch is ahead 9 and behind 2; current main is 9703da845384423ad85883216bf8853642c21bcd."
blockers:
  - "Branch is behind current main by two commits and must be synchronized before final exact-head validation."
  - "Required remains blocked by the Windows MariaDB installation failure in CI 30223667513."
next_action: "Synchronize dudantas/mge-004-composition-root-lifecycle with main@9703da845384423ad85883216bf8853642c21bcd while preserving exactly the seven changed paths."
```
