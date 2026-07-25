---
task_id: OTH-20260725-oam047-lua-runtime-adapt
coordination_id: OAM-047
status: review
branch: dudantas/oam-047-lua-runtime-adapt
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "768a7a62da0b959c6851a04402bfc6ba0f7a8ddf"
related_issue: ""
related_pr: "107"
owned_paths:
  - docs/agents/tasks/active/OTH-20260725-oam047-lua-runtime-adapt.md
  - docs/oam-047-lua-runtime-adapt.md
  - src/lua/scripts/CMakeLists.txt
  - src/lua/scripts/lua_environment.cpp
  - src/lua/scripts/lua_environment.hpp
  - src/lua/scripts/lua_interface_registry.cpp
  - src/lua/scripts/luascript.hpp
  - tests/unit/lua/CMakeLists.txt
  - tests/unit/lua/oam_047_lua_runtime_adapt_test.cpp
---

# OAM-047 Lua Runtime adaptation

Final disposition: `lua-runtime → ADAPT`.

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T16:31:00+02:00
head: 768a7a62da0b959c6851a04402bfc6ba0f7a8ddf
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
  - src/lua/scripts/lua_interface_registry.cpp
  - src/lua/scripts/luascript.hpp
  - tests/unit/lua/CMakeLists.txt
  - tests/unit/lua/oam_047_lua_runtime_adapt_test.cpp
proven:
  - Canary OAM-047 preflight PR 922 merged as bc8d7827f652b8b8b3200f7ef81818e8d5d149f5.
  - Task-start Otheryn main is 415f559f829c83d79d9c609e7f421d2449e59d74 and reviewed upstream is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Ordinary LuaScriptInterface instances retain the shared main lua_State pointer and event-table registry references.
  - The inherited main reInitState closes and replaces the shared state without child inventory or reset.
  - A process-local object registry can identify only children currently attached to the old shared state.
  - Closing attached child registry tables before lua_close and reinitializing them after main-state creation removes the dangling-state boundary without loading feature scripts.
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
changed_paths:
  - docs/agents/tasks/active/OTH-20260725-oam047-lua-runtime-adapt.md
  - docs/oam-047-lua-runtime-adapt.md
  - src/lua/scripts/CMakeLists.txt
  - src/lua/scripts/lua_environment.cpp
  - src/lua/scripts/lua_environment.hpp
  - src/lua/scripts/lua_interface_registry.cpp
  - src/lua/scripts/luascript.hpp
  - tests/unit/lua/CMakeLists.txt
  - tests/unit/lua/oam_047_lua_runtime_adapt_test.cpp
validation:
  - command: focused Lua child lifecycle contract
    result: NOT_RUN
    evidence: The final feature PR head must compile and execute the registered fixtures.
  - command: exact-head Otheryn gates and audit
    result: NOT_RUN
    evidence: Autofix, CI and Required must pass before merge.
blockers:
  - Otheryn feature PR exact-head validation and merge
next_action: Mark PR 107 ready, require exact-head Autofix, CI and Required, audit discussions and target-main drift, then squash-merge with the expected head.
```
