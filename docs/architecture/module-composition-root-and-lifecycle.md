# Module composition root and lifecycle

Status: **MGE-004 implementation contract**

Issue: `#161`

## Purpose

MGE-004 introduces one bounded composition-root lifecycle coordinator on top of the validated MGE-003 module graph. It establishes explicit start, rollback, readiness and reverse-stop semantics for participants that have actually been registered with the root.

It does not claim lifecycle ownership for the rest of the legacy server.

## Lifecycle flow

```text
validated GameProfile module selection
  -> dependency-first order from ModuleRegistry
  -> explicit participant registration
  -> start registered participants in graph order
  -> ready only after every participant succeeds
  -> reverse rollback on startup failure
  -> reverse idempotent stop on shutdown
```

## Registration contract

A lifecycle participant declares:

- its stable `ModuleId`;
- a diagnostic name;
- a start callback;
- a stop callback.

Registration fails deterministically when:

- the selected profile does not contain the module;
- the module already has a participant;
- the participant name is empty;
- start or stop is missing;
- lifecycle start has already begun.

Registration is explicit C++ composition-root work. Lua cannot register lifecycle participants or redefine lifecycle dependencies.

## Start and readiness

The root consumes the deterministic dependency-first order produced by MGE-003. Only registered participants are invoked; unregistered logical modules remain under their existing legacy ownership.

The root remains in `Starting` while callbacks run and exposes `Ready` only after every registered callback succeeds. A start attempt is single-use.

## Failure rollback

When a start callback throws, the failing participant is not marked as started. Every participant that completed startup is stopped in exact reverse order. The root transitions to `Failed`, readiness remains false, and deterministic diagnostics identify the module and participant.

## Shutdown

Normal stop invokes successfully started participants in exact reverse order. Stop is idempotent. A stop failure is recorded but does not prevent remaining participants from stopping.

The root owns no process-global mutable lifecycle state, so separate roots remain isolated in tests.

## First selected infrastructure participant

MGE-004 registers the existing `MonsterComputeService` under logical module `Creatures`.

Its configuration and startup position are preserved:

- `MONSTER_COMPUTE_THREADS` and `MONSTER_COMPUTE_QUEUE_CAPACITY` are read exactly as before;
- startup still occurs after configuration, database, Lua/content loading, world type and maps;
- the existing mode/worker/capacity log is preserved;
- shutdown remains safe when the legacy process-level fallback calls it again because `MonsterComputeService::shutdown()` is idempotent.

This is the only existing infrastructure service transferred to the composition root in MGE-004.

## Ownership boundary

The composition root owns lifecycle only for registered participants. Dispatcher, ThreadPool, database, Lua environment, Game, protocol listeners, persistence services and all gameplay systems remain under current legacy ownership.

A logical module descriptor or an unregistered module selection is not evidence of runtime lifecycle ownership.

## Explicit exclusions

MGE-004 does not implement:

- gameplay feature extraction;
- dynamic plugins or a stable shared-library ABI;
- runtime hot enable/disable;
- Lua-defined lifecycle;
- broad singleton removal;
- Dispatcher, ThreadPool, database, Lua, Game, protocol or persistence migration;
- protocol wire, schema, map, datapack or deployment changes.

## Next package

Per the MGE-001 sequence, MGE-006 should define bounded command/query protocol and Lua adapter interfaces for the Bank candidate before MGE-005 implements the first vertical gameplay extraction.
