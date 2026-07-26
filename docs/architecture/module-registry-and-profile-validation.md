# Module registry and profile validation

Status: **MGE-003 implementation contract**

Issue: `#154`

## Purpose

MGE-003 adds the static C++ descriptor and validation foundation required before a composition root can own lifecycle. It does not extract gameplay systems and does not claim that a catalog entry is already an isolated implementation.

The bounded flow is:

```text
static C++ module catalog
  + immutable current module selection
  + selected protocol capabilities
  -> deterministic graph validation
  -> dependency-first startup order
  -> publish immutable GameProfile snapshot
```

## Descriptor contract

Each descriptor declares:

- stable `ModuleId`;
- `ModuleRequirement` (`CoreRequired`, `ProfileRequired`, or `Optional`);
- legal direct dependencies;
- required abstract protocol capabilities.

Lua cannot create descriptors, redefine dependencies, remove required modules, or select a different module set in MGE-003.

## Current catalog meaning

The current catalog names the legal logical boundaries required by the active architecture contract. It is an architecture registry, not evidence that source ownership, public APIs, persistence, threading, adapters, or lifecycle have already been extracted.

The immutable current selection contains every catalog entry so existing runtime behavior remains enabled. No feature is disabled and no new runtime toggle is exposed.

## Validation contract

Validation is deterministic and fails closed for:

- invalid or duplicate descriptor identifiers;
- dependencies on unregistered modules;
- dependency cycles;
- unknown or duplicate profile selections;
- missing core/profile-required modules;
- selected modules whose dependencies are not selected;
- selected modules whose protocol capability is unavailable.

Successful validation returns one deterministic dependency-first startup order. MGE-003 computes this order but does not execute module start or stop hooks.

## Protocol capability boundary

Descriptors depend on abstract module capabilities rather than client version checks. The current bridge maps reviewed `ProtocolProfile` features to:

- `market-protocol`;
- `imbuement-protocol`;
- `wheel-protocol`.

A capability states that the selected client protocol can represent a module surface. It does not prove gameplay parity or ruleset compatibility.

## GameProfile integration

Every startup `GameProfile` is constructed with a copy of the static current selection after the registry validates it against the current protocol. If the internal graph is invalid, construction throws before `ConfigManager` can publish the immutable startup snapshot.

Normal config reload keeps the same snapshot and therefore the same module selection. Runtime code does not continuously query Lua for module existence.

## Failure behavior

Any registry or selection error is formatted as stable ordered diagnostics and prevents a valid startup profile from being constructed. The server cannot proceed to readiness with an invalid graph.

## Explicit exclusions

MGE-003 does not implement:

- composition-root ownership;
- module construction, start, rollback, stop, or reverse shutdown;
- dynamic plugins or shared-library ABI;
- runtime hot enable/disable;
- Lua-defined module metadata;
- gameplay extraction;
- protocol wire changes or historical-profile enablement;
- persistence, schema, map, datapack, or deployment changes.

## Next package

MGE-004 may introduce a bounded composition root and lifecycle state machine using the validated startup order. It must preserve behavior, prove startup rollback and reverse shutdown, and must not yet extract a gameplay feature.
