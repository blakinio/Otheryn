# OTH-20260727 — MGE-004 composition root lifecycle

Status: **review**

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
updated_at: "2026-07-27T10:56:36+02:00"
head: "88b657b6ade78498ca3a52f34c5d57f31ad81b6b"
head_scope: "latest fully validated build-affecting head; this task-record update is checkpoint-only"
branch: "dudantas/mge-004-composition-root-lifecycle"
pr: "https://github.com/blakinio/Otheryn/pull/162"
status: "review"
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
  - "ModuleCompositionRoot validates the graph, starts registered participants in dependency order, rolls back and stops in reverse, records stop errors and isolates root instances."
  - "Focused tests cover ordering, rollback, idempotence, stop failure, registration rejection, readiness, isolation and invalid graph rejection."
  - "CanaryServer registers only MonsterComputeService under logical module Creatures while preserving its configuration, startup phase and diagnostics."
  - "The implementation branch is synchronized with main@4ad8c0f2ed1c6bd60da9b747b8ff180ced60b593 at validated head 88b657b6ade78498ca3a52f34c5d57f31ad81b6b."
  - "The exact main comparison is behind zero and changes exactly the seven owned paths."
  - "CI 30250205214 passed fast checks, Lua, Docker, Linux debug with full tests, Linux release, macOS, Windows Solution, Windows CMake and all applicable runtime smoke checks."
  - "Windows CMake passed compilation, MariaDB installation, Canary runtime smoke and artifact upload."
  - "Linux debug passed compilation, Canary runtime smoke, schema import and the full test suite."
  - "Linux release passed compilation plus Canary and Global datapack runtime smoke."
  - "macOS passed compilation and Canary runtime smoke without a rerun on the final synchronized head."
  - "autofix.ci 30250204998 passed on the exact validated head."
  - "Required 30250204935 job 89926244941 passed on the exact validated head."
  - "PR #162 is open, non-draft and mergeable at the exact validated head."
  - "PR comments, submitted reviews and inline review threads are empty."
derived:
  - "The earlier macOS queue-latency warning was a hosted-runner flake because the unchanged prior head passed on rerun and the final synchronized head passed macOS without rerun."
  - "The implementation is ready for expected-head merge after focused validation of this checkpoint-only commit and one final live main-drift audit."
unknown: []
conflicts: []
first_failure:
  marker: "CI 30247921486 attempt 1 / macOS job 89919380421 / Smoke test Canary datapack runtime"
  result: "RESOLVED"
  evidence: "The server reached readiness and shut down cleanly; the unchanged prior head passed on rerun, and final-head macOS job 89926709126 passed without rerun."
rejected_hypotheses:
  - "Move all singleton services into the root in one package."
  - "Treat every MGE-003 descriptor as lifecycle-owned."
  - "Combine lifecycle foundation with Bank gameplay extraction."
  - "Change MGE-004 code to suppress a one-off hosted-runner queue-latency warning."
changed_paths:
  - "docs/agents/tasks/active/OTH-20260727-mge004-composition-root-lifecycle.md"
  - "docs/architecture/module-composition-root-and-lifecycle.md"
  - "src/canary_server.cpp"
  - "src/canary_server.hpp"
  - "src/modules/module_lifecycle.hpp"
  - "tests/unit/modules/CMakeLists.txt"
  - "tests/unit/modules/mge_004_module_lifecycle_test.cpp"
validation:
  - command: "compare main...dudantas/mge-004-composition-root-lifecycle"
    result: "PASS"
    evidence: "Merge base is main@4ad8c0f2ed1c6bd60da9b747b8ff180ced60b593, behind_by is zero and exactly seven owned paths differ."
  - command: "autofix.ci 30250204998"
    result: "PASS"
    evidence: "Completed successfully on head 88b657b6ade78498ca3a52f34c5d57f31ad81b6b."
  - command: "CI 30250205214 fast checks and Lua"
    result: "PASS"
    evidence: "Formatting, analysis, yamllint and Lua tests completed successfully."
  - command: "CI 30250205214 Docker"
    result: "PASS"
    evidence: "Image build, export, validation and artifact upload completed successfully."
  - command: "CI 30250205214 Linux debug"
    result: "PASS"
    evidence: "Compile, Canary runtime smoke, database schema import and full tests completed successfully."
  - command: "CI 30250205214 Linux release"
    result: "PASS"
    evidence: "Compile plus Canary and Global datapack runtime smoke completed successfully."
  - command: "CI 30250205214 macOS"
    result: "PASS"
    evidence: "Compile, MySQL startup, Canary runtime smoke and artifact upload completed successfully without rerun."
  - command: "CI 30250205214 Windows Solution"
    result: "PASS"
    evidence: "MSBuild solution build and artifact upload completed successfully."
  - command: "CI 30250205214 Windows CMake"
    result: "PASS"
    evidence: "Run CMake, MariaDB installation, Canary runtime smoke and artifact upload completed successfully."
  - command: "Required 30250204935 job 89926244941"
    result: "PASS"
    evidence: "Applicable CI workflow aggregation completed successfully."
  - command: "PR #162 discussion, review and thread audit"
    result: "PASS"
    evidence: "No comments, submitted reviews or inline review threads exist."
  - command: "PR #162 live state audit"
    result: "PASS"
    evidence: "Open, non-draft and mergeable at head 88b657b6ade78498ca3a52f34c5d57f31ad81b6b."
blockers: []
next_action: "Re-read the live PR head and main, then merge PR #162 with expected-head protection if behind_by remains zero, the seven-path diff is unchanged and the focused checks triggered by this checkpoint-only commit are green."
```
