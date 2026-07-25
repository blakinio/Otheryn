# OAM-047 Lua Runtime target proof

Final disposition: `lua-runtime → ADAPT`.

## Exact baselines

- Canary preflight PR #922 merged as `bc8d7827f652b8b8b3200f7ef81818e8d5d149f5`.
- Otheryn task-start main: `415f559f829c83d79d9c609e7f421d2449e59d74`.
- reviewed current upstream: `opentibiabr/canary@7323503b3dc61ed86bf1f04a611b2d0aec64b35a`.
- target/upstream/live-legacy `src/lua/scripts/luascript.hpp`: blob `e65ac8fab062491a8d60a951d38ff6b57e025f4a`.
- target/upstream/live-legacy `src/lua/scripts/luascript.cpp`: blob `2bbfed787aaa39f63f11a69165e9d47fca8aa067`.
- target pre-adaptation `lua_environment.hpp`: blob `9e5d8d8b5224eed6f23da01d99bd9f2f419aaeda`.
- target pre-adaptation `lua_environment.cpp`: blob `060a735293a5b89abe98e58a40000d9b264818f9`.
- reviewed upstream/live-legacy `lua_environment.cpp`: blob `c28c3a77824fc7fc997940921b039a3eeca1a6ce`.

## Isolated target defect

Ordinary `LuaScriptInterface::initState()` stores the shared main `lua_State*` and allocates an event-table registry reference. `LuaEnvironment::reInitState()` closed that state and created a replacement without inventorying, invalidating or reinitializing child interfaces. The inherited source retained an explicit `get children, reload children` TODO. A child could therefore keep a pointer and registry IDs belonging to the closed state until a separate subsystem happened to reinitialize it.

## Bounded adaptation

- Every `LuaScriptInterface` has a process-local lifetime registry entry independent of the Lua environment singleton.
- The main environment snapshots only registered children whose base `luaState` equals the current shared state; uninitialized or independently overridden test interfaces are excluded.
- `closeState()` invalidates those child event tables before `lua_close()`.
- `reInitState()` recreates the main state and initializes the same child interfaces against the replacement state.
- A child rebind failure closes the replacement main state and already rebound children, preserving fail-closed behavior.
- The adaptation resets interfaces only. It does not reload feature scripts or claim that every subsystem completed its own data/event reload.

The registry implementation is compiled through the existing `lua_environment.cpp` source so both CMake and the maintained Visual Studio solution consume the same bounded implementation without expanding build-system ownership.

Adapted blobs:

- `luascript.hpp`: `0660238ca408687142d9a9e1c8d839c45ed9486d`.
- `lua_environment.hpp`: `f684825b2351ca9d7e41fbc95649542386549497`.
- `lua_environment.cpp`: `fc246af01578788cd3fcfcc2b39655c94c42cc3b`.

Focused fixtures prove:

- two active children are rebound to the current main state;
- old event-table IDs fail closed after the reset;
- rebound children can register and resolve new events;
- an uninitialized interface is not attached merely because an object exists;
- a destroyed interface is removed before a later main reset;
- the shared test interface follows the same bounded child lifecycle.

## Build-path correction

The first final-head CI attempt passed CMake, Linux, macOS and Docker paths but failed the maintained Windows Solution build because a newly separated registry translation unit was registered only in CMake. The correction folded the registry definitions into the already-supported `lua_environment.cpp` translation unit and restored the original scripts CMake source list. This preserves one implementation across both supported build paths without editing Visual Studio project ownership.

## Explicit boundaries

This package does not claim:

- automatic reloading of individual gameplay scripts or feature-specific registration families;
- complete correctness of every subsystem reload sequence or event-data clear/load order;
- concurrent reload/callback safety, thread safety, lock freedom or race freedom;
- safe lifetime of every Lua userdata, C++ object wrapper, timer parameter or external callback;
- serialization, persistence, crash recovery or distributed runtime behavior;
- physical-client behavior, protocol compatibility, production gameplay parity or full server readiness.

## Remaining unknowns

Production reload ordering, callback timing during operator-triggered reloads, complete userdata lifetime safety and concurrency behavior remain `UNKNOWN`.

`next_action`: require exact-head Autofix, CI and Required after the supported-build correction, audit discussions and target-main drift, then squash-merge with the expected head.
