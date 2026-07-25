---
task_id: OTH-20260725-oam047-lua-runtime-adapt
coordination_id: OAM-047
status: review
branch: dudantas/oam-047-lua-runtime-adapt
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "f39d94944e72f997595a3b82854b8455c22a2f88"
related_issue: ""
related_pr: "107"
owned_paths:
  - docs/agents/tasks/active/OTH-20260725-oam047-lua-runtime-adapt.md
  - docs/oam-047-lua-runtime-adapt.md
  - src/lua/scripts/CMakeLists.txt
  - src/lua/scripts/lua_environment.cpp
  - src/lua/scripts/lua_environment.hpp
  - src/lua/scripts/luascript.hpp
  - tests/unit/lua/CMakeLists.txt
  - tests/unit/lua/oam_047_lua_runtime_adapt_test.cpp
---

# OAM-047 Lua Runtime adaptation

Final disposition: `lua-runtime → ADAPT`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T19:36:00+02:00
head: f39d94944e72f997595a3b82854b8455c22a2f88
branch: dudantas/oam-047-lua-runtime-adapt
pr: 107
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - lua-runtime
owned_paths:
  - docs/agents/tasks/active/OTH-20260725-oam047-lua-runtime-adapt.md
  - docs/oam-047-lua-runtime-adapt.md
  - src/lua/scripts/CMakeLists.txt
  - src/lua/scripts/lua_environment.cpp
  - src/lua/scripts/lua_environment.hpp
  - src/lua/scripts/luascript.hpp
  - tests/unit/lua/CMakeLists.txt
  - tests/unit/lua/oam_047_lua_runtime_adapt_test.cpp
proven:
  - Canary OAM-047 preflight PR 922 merged as bc8d7827f652b8b8b3200f7ef81818e8d5d149f5.
  - Task-start Otheryn main is 415f559f829c83d79d9c609e7f421d2449e59d74 and reviewed upstream is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Ordinary LuaScriptInterface instances retain the shared main lua_State pointer and event-table registry references.
  - The inherited main reInitState closes and replaces the shared state without child inventory or reset.
  - A process-local object registry identifies only children currently attached to the old shared state.
  - Closing attached child registry tables before lua_close and reinitializing them after main-state creation removes the dangling-state boundary without loading feature scripts.
  - Focused fixtures cover two active children, stale registry IDs, new event registration, dormant interfaces, destroyed interfaces and the shared test interface.
  - CMake, Linux, macOS and Docker paths passed on the first final-head attempt.
  - The maintained Windows Solution build isolated a build-registration defect because the separated registry translation unit was CMake-only.
  - The supported-build correction folds registry definitions into existing lua_environment.cpp and restores the original CMake source list.
derived:
  - lua-runtime requires ADAPT rather than REUSE because main-state replacement did not preserve child-interface validity.
  - The bounded correction belongs to shared Lua lifecycle, not feature-specific bindings or gameplay scripts.
unknown:
  - Complete production subsystem reload ordering and callback timing.
  - Concurrent reload/read/callback safety and race freedom.
  - Exhaustive userdata, timer parameter and external C++ wrapper lifetime safety.
  - Physical-client, protocol and production gameplay effects.
conflicts: []
first_failure:
  marker: untracked-child-interface-reset
  evidence: LuaEnvironment::reInitState closes the main state while attached child interfaces retain pointers and registry IDs unless separately reinitialized.
rejected_hypotheses:
  - Finalize REUSE from byte-identical LuaScriptInterface roots or successful compilation.
  - Automatically reload all gameplay scripts inside the main-state lifecycle primitive.
  - Expand the adaptation into feature-specific registrations, userdata redesign or generic concurrent reload orchestration.
  - Expand build-system ownership by editing the Visual Studio project when the implementation can remain in an existing supported Lua translation unit.
changed_paths:
  - docs/agents/tasks/active/OTH-20260725-oam047-lua-runtime-adapt.md
  - docs/oam-047-lua-runtime-adapt.md
  - src/lua/scripts/lua_environment.cpp
  - src/lua/scripts/lua_environment.hpp
  - src/lua/scripts/luascript.hpp
  - tests/unit/lua/CMakeLists.txt
  - tests/unit/lua/oam_047_lua_runtime_adapt_test.cpp
validation:
  - command: focused Lua child lifecycle contract
    result: PASS
    evidence: The first CI attempt compiled and executed the registered unit fixture successfully on Linux debug.
  - command: cross-platform CMake and runtime smoke
    result: PASS
    evidence: Linux release/debug, Windows CMake, macOS and Docker jobs passed before the build-registration correction.
  - command: maintained Windows Solution build
    result: FAIL
    evidence: The separated registry translation unit was absent from vcproj/canary.vcxproj; the correction removes that unsupported split.
  - command: exact-head Otheryn gates after correction
    result: NOT_RUN
    evidence: Autofix, CI and Required must pass on the corrected final PR head.
blockers:
  - corrected exact-head Autofix, CI and Required
  - clean discussion and target-main drift audit
next_action: Require exact-head Autofix, CI and Required on PR 107 after the supported-build correction, audit discussions and target-main drift, then squash-merge with the expected head.
```
