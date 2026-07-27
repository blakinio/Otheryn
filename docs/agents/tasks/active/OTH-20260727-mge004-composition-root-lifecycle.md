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
updated_at: "2026-07-27T10:22:42+02:00"
head: "952da157edd812b513e4c49ba9292408872fa6aa"
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
  - "The branch is synchronized with main@ec5038a7f132a4c2ed030edda38a56b5b1ec916a at head 952da157edd812b513e4c49ba9292408872fa6aa."
  - "The exact main comparison is behind zero and changes exactly the seven owned paths."
  - "CI 30247921486 passed fast checks, Lua, Docker, Linux debug with full tests, Linux release, Windows Solution, Windows CMake and all applicable runtime smoke checks after the macOS job rerun."
  - "Windows CMake passed compilation, MariaDB installation, Canary runtime smoke and artifact upload."
  - "macOS rerun job 89923079893 passed compilation and Canary runtime smoke on the unchanged exact head."
  - "autofix.ci 30247921263 passed on the exact head."
  - "Required rerun job 89924255172 passed after CI became successful."
  - "PR #162 is open, non-draft and mergeable at head 952da157edd812b513e4c49ba9292408872fa6aa."
  - "PR comments, reviews and inline review threads are empty."
derived:
  - "The first macOS smoke failure was a nondeterministic hosted-runner latency warning because the server reached readiness and shut down cleanly, the unchanged-head rerun passed, and every other applicable platform passed."
  - "The branch is ready for expected-head merge if the live main and seven-path comparison remain unchanged."
unknown: []
conflicts: []
first_failure:
  marker: "CI 30247921486 attempt 1 / macOS job 89919380421 / Smoke test Canary datapack runtime"
  result: "RESOLVED"
  evidence: "Build and MySQL startup passed; smoke failed only because --fail-on-warnings observed one Dispatcher queue-latency warning after readiness. Exact-head rerun job 89923079893 passed the same compile and smoke path."
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
    evidence: "Merge base is main@ec5038a7f132a4c2ed030edda38a56b5b1ec916a, behind_by is zero and exactly seven owned paths differ."
  - command: "autofix.ci 30247921263"
    result: "PASS"
    evidence: "Completed successfully on head 952da157edd812b513e4c49ba9292408872fa6aa."
  - command: "CI 30247921486 fast checks and Lua"
    result: "PASS"
    evidence: "Formatting, analysis, yamllint and Lua tests completed successfully."
  - command: "CI 30247921486 Docker"
    result: "PASS"
    evidence: "Image build, export and validation completed successfully."
  - command: "CI 30247921486 Linux debug"
    result: "PASS"
    evidence: "Compile, Canary runtime smoke, database schema import and full unit tests completed successfully."
  - command: "CI 30247921486 Linux release"
    result: "PASS"
    evidence: "Compile plus Canary and Global datapack runtime smoke completed successfully."
  - command: "CI 30247921486 Windows Solution"
    result: "PASS"
    evidence: "MSBuild solution build and artifact upload completed successfully."
  - command: "CI 30247921486 Windows CMake"
    result: "PASS"
    evidence: "Run CMake, MariaDB installation, Canary runtime smoke and artifact upload completed successfully."
  - command: "CI 30247921486 macOS job 89919380421"
    result: "FLAKE"
    evidence: "Compile and server readiness succeeded; --fail-on-warnings rejected one Dispatcher queue-latency warning."
  - command: "CI 30247921486 macOS rerun job 89923079893"
    result: "PASS"
    evidence: "Compile, MySQL startup, Canary runtime smoke and artifact upload completed successfully on the unchanged head."
  - command: "Required 30247921286 rerun job 89924255172"
    result: "PASS"
    evidence: "Applicable CI workflow aggregation completed successfully."
  - command: "PR #162 discussion, review and thread audit"
    result: "PASS"
    evidence: "No comments, submitted reviews or inline review threads exist."
  - command: "PR #162 live state audit"
    result: "PASS"
    evidence: "Open, non-draft and mergeable at head 952da157edd812b513e4c49ba9292408872fa6aa."
blockers: []
next_action: "Merge PR #162 with expected-head protection at 952da157edd812b513e4c49ba9292408872fa6aa if main remains ec5038a7f132a4c2ed030edda38a56b5b1ec916a and the seven-path diff is unchanged."
```
