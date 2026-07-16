# OAM-003B — Lua runtime lifecycle boundary

Status: implementation slice

Parent coordination: `OAM-003` in `blakinio/canary#411`

Dependency satisfied by: `blakinio/Otheryn#4`, squash-merged as `9b5805aaeef50774e9db5225c05529a06cec507e`.

Task issue: `blakinio/Otheryn#5`

## Pinned task-start baseline

```text
blakinio/Otheryn@9b5805aaeef50774e9db5225c05529a06cec507e
```

Comparison evidence remains pinned to:

```text
opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
blakinio/canary@c32e42469f302ab108dea08d9b90164458696328
zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7
```

## Goal

Make the existing `LuaEnvironment` the explicit root Lua runtime lifecycle boundary used by the Oteryn composition seam, while preserving existing typed shared-userdata ownership helpers and avoiding a broad binding or reload rewrite.

## Bounded implementation

1. Add an idempotent public `LuaEnvironment::shutdown()` lifecycle operation.
2. Keep the destructor as a safety net by delegating to `shutdown()`.
3. Add `LuaEnvironment::reloadCore(coreDirectory)` so callers do not manually compose root runtime reload from direct `loadFile` calls.
4. Resolve the existing `LuaEnvironment` from the composition root in `main()` alongside the other root dependencies.
5. Close the root Lua runtime explicitly in `main()` after `CanaryServer` returns from normal server/doc-generation execution; the `LuaEnvironment` destructor remains the process-exit fallback.
6. Route SIGHUP and `GameReload::reloadCore()` through the same `LuaEnvironment::reloadCore()` boundary.

## Explicit non-goals

- Do not bulk-reload or reconstruct child `LuaScriptInterface` instances.
- Do not claim the existing `LuaEnvironment::reInitState()` child-interface TODO is solved.
- Do not rewrite `BaseEvents`, `Modules`, NPC, raid or script subsystem lifecycle.
- Do not change gameplay/domain Lua bindings.
- Do not change typed shared-userdata ownership semantics or `docs/systems/lua-shared-userdata.md`.
- Do not add a second DI container, Lua runtime singleton or parallel registry.
- Do not change scheduler, persistence, protocol or client behavior.

## Binding boundary rule for this package

This package touches no new domain-facing binding implementation. Existing binding code must continue to use the current typed ownership helpers (`pushSharedUserdata`, `pushBorrowedSharedUserdata` and the `LuaUserdataTraits` contract where applicable). Any future OAM package that changes a domain-facing binding must state the ownership mode explicitly and audit only the touched polymorphic/shared-userdata path.

## Reload semantics

`reloadCore()` is intentionally a narrow root-runtime operation. It reloads `core.lua` into the existing root `LuaEnvironment`; it does not call `reInitState()` and therefore does not silently claim child-interface reconstruction.

Subsystem reloads remain owned by their current bounded subsystem paths until separately revalidated.

## Shutdown semantics

`shutdown()` marks the root environment as shutting down before closing its Lua state. Repeated shutdown calls are no-ops, preventing normal composition-root shutdown plus the destructor fallback from reopening or double-closing the root state.

`initState()`, `reInitState()` and `reloadCore()` refuse to resurrect the root runtime after shutdown has begun.

## Acceptance evidence

- exact-head build and runtime smoke matrix passes;
- `Required` passes on the same head;
- `LuaEnvironment::shutdown()` is idempotent for an already-closed/uninitialized state by explicit guard;
- SIGHUP and game core reload use the same root-runtime reload API;
- no feature/domain binding files change;
- typed shared-userdata documentation/implementation remains unchanged.
