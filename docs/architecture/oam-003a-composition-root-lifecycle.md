# OAM-003A — Composition Root, Lifecycle, DI and Configuration Ownership

Status: **active bounded target adaptation**

Parent coordination: `OAM-003`

Pinned target task-start baseline:

```text
blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115
```

Pinned evidence baselines:

```text
opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
blakinio/canary@c32e42469f302ab108dea08d9b90164458696328
zimbadev/crystalserver@fdd2b1f13f53894c584346ef3de43658045c42a7
```

## Goal

Introduce the smallest explicit Oteryn composition-root seam around server construction while preserving the proven upstream startup/shutdown behavior. Do not redesign persistence, protocol, scheduler internals, Lua bindings or source-tree layout in this slice.

## Canonical modules

```text
configuration            ADAPT
engine-runtime-lifecycle ADAPT
engine-service-container ADAPT
```

## First bounded implementation step

Replace entrypoint-level contextual construction:

```cpp
auto &server = inject<CanaryServer>();
```

with explicit `CanaryServer` construction from its already-declared constructor dependencies obtained at the current compatibility boundary.

The purpose is to make `main()` the visible owner of the top-level server lifetime without inventing a new application framework or changing runtime semantics.

## Invariants

- one process/world/channel;
- no multichannel/Redis/distributed ownership;
- no new Meyers singleton or second DI container;
- no repository-wide path rewrite;
- existing scheduler implementation remains unchanged;
- existing startup/shutdown ordering remains unchanged;
- current DI remains a compatibility substrate while new target-owned construction moves toward explicit dependencies;
- configuration parsing/reload behavior remains unchanged in this first step.

## Validation

- focused compile/build validation on the exact PR head;
- existing CI and `Required` gate;
- no changed runtime behavior beyond construction ownership;
- exact diff review before merge.

## Follow-up within OAM-003A

Further DI/config ownership changes require separate evidence and should be added only if the first seam exposes a concrete dependency that can be moved without broad churn.
