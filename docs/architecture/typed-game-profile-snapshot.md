# Typed immutable startup GameProfile snapshot

Status: **MGE-002 implementation contract**

Tracking issue: `blakinio/Otheryn#132`

## Purpose

MGE-002 introduces the first runtime artifact from the modular-engine architecture: one typed, immutable startup `GameProfile` snapshot. It does not implement a module registry, module graph, historical profile, ruleset registry or dynamic plugin system.

The snapshot converts selected Lua globals into C++ values once, validates the complete candidate, and atomically publishes `std::shared_ptr<const GameProfile>` only after successful validation.

## Snapshot boundary

The snapshot owns startup-only decisions for:

- profile identity;
- selected primary protocol profile;
- whether registered legacy protocol listeners are enabled;
- world type;
- core directory, datapack directory, main map and custom-map selection;
- login, status, modern game and effective legacy game ports.

Normal `ConfigManager::reload()` continues to refresh reloadable configuration but does not replace these fields. Compatibility getters for the selected startup keys resolve from the immutable snapshot, preventing old consumers from observing a different startup contract after reload.

## Lua declarations

Backward-compatible defaults are used when these declarations are absent:

```lua
gameProfileId = "current"
gameProtocolProfile = "current"
```

Existing globals such as `worldType`, `dataPackDirectory`, `mapName`, `allowOldProtocol` and protocol ports remain the source syntax for MGE-002. C++ owns their accepted types, ranges and combinations.

## Validation and publication

Startup fails before readiness when:

- profile identity is not a bounded lowercase identifier;
- the protocol profile name is unknown, disabled or not authorized as the MGE-002 primary profile;
- world type is unknown;
- required content identifiers are empty or an unregistered datapack is selected without the explicit custom-datapack opt-in;
- listener ports are out of range, conflict, or cannot be auto-selected.

The candidate is built off to the side. Failure returns without publishing a snapshot. A corrected configuration can then be loaded successfully. Publication uses atomic shared-pointer store/load semantics and precedes the loaded flag and deferred callbacks.

## Effective legacy ports

A configured legacy port of `0` means auto-select. MGE-002 computes and stores the effective listener port in the snapshot. Auto-selection preserves the established ordering while avoiding login, status, modern game and the other legacy listener. If no valid port remains, startup fails closed.

When `allowOldProtocol` is false, both effective legacy ports are `0` and no historical primary protocol is enabled.

## Selected consumers

The following startup paths use the snapshot directly or through snapshot-backed compatibility accessors:

- bootstrap profile/protocol logging;
- datapack validation;
- world type application;
- module core-directory selection;
- main/custom map selection;
- protocol port resolution and listener registration.

This is intentionally not a migration of every `ConfigManager` caller.

## Test-fixture compatibility

Normal reload remains unable to replace snapshot-owned startup values. Integration fixtures that intentionally load alternate core content must use the explicit `setStartupStringOverrideForTests`/`clearStartupStringOverrideForTests` scope around fixture loading. The override changes compatibility getter resolution only, does not mutate or republish `GameProfile`, and has no production caller.

## Non-goals

- no `ModuleRegistry` or dependency graph;
- no module lifecycle or hot reload;
- no Tibia 7.6/8.6/11.0 primary game profile enablement;
- no protocol packet or handshake behavior change;
- no gameplay, Lua binding, persistence, schema, map, datapack or deployment change;
- no MGE-003 or later package.
