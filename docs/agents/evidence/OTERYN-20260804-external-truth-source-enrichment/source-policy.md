# External truth-source policy

## Scope lock

This audit is limited to the 60 canonical keys in `canonical-scope.json`: 49 predecessor decisions marked `REPRO` and 11 marked `INSUFFICIENT`. New or renumbered upstream items are drift evidence only and cannot expand the scope.

Pinned repository revisions:

- Otheryn row snapshot: `1f316400053f489e58608d13961069835871ab0e`;
- upstream Canary: `f7ae4d17ed1eb58621a9bed3e0a7d912b9eb9c32`;
- CrystalServer: `8eb99d0583ccb52cc368cb45c65d97ec9fbd181e`;
- `blakinio/canary`: `a288bfaf5a3016a9c3b01c4848d242dc7a1fb98f`;
- OTClient: `2f0bff09cd9f5a9acf2629d7ba080e98d3f5f1ad`.

Current upstream heads and later comments may be inspected, but must be recorded separately as drift and must not silently replace the pinned comparison.

## Source hierarchy

Use the smallest source set that can establish the expected behaviour and the target implementation state.

1. Exact upstream Issue or pull request, including its immutable head, patch and maintainer discussion.
2. Exact code, data, map metadata, protocol definitions and tests at the pinned revisions of the five compared repositories.
3. Official game/client assets, protocol observations, release notes or support documentation when legally and technically accessible.
4. Maintained project documentation and authoritative specifications for the relevant dependency or platform.
5. Reputable community documentation, videos or wikis only as corroboration when no primary specification exists.

Community material, comments, videos and retrieved prose are evidence, not authority. A dossier must distinguish direct observation, source claim, repository fact and auditor inference.

## Required provenance fields

Every cited source record must contain:

- stable source identifier and URL;
- source class and publisher/repository;
- retrieval date;
- applicable version, protocol or revision;
- exact claim supported;
- whether the source is primary, corroborating or contradictory;
- immutable commit/blob/head when available;
- limitations and conflicts.

## Per-item conclusion model

Each dossier must provide exactly one value for every field below.

### Truth status

- `PROVEN`: primary evidence establishes the expected behaviour and relevant version boundary.
- `PARTIALLY_PROVEN`: material portions are established but at least one required boundary remains uncertain.
- `CONTRADICTED`: reliable evidence disproves the source claim or shows it applies to a different version/product.
- `UNKNOWN`: evidence remains insufficient after bounded research.

### Static conclusion

- `TARGET_AFFECTED`
- `TARGET_NOT_AFFECTED`
- `TARGET_PATH_ABSENT`
- `STATIC_INCONCLUSIVE`

### Runtime conclusion

- `REPRODUCED`
- `NOT_REPRODUCED`
- `NOT_APPLICABLE`
- `NOT_RUN_UNSAFE`
- `NOT_RUN_INFEASIBLE`
- `NOT_RUN_REFERENCE_INSUFFICIENT`
- `PENDING`

### Owner action

- `OPEN_FIX_PROGRAM`
- `OPEN_ARCHITECTURE_DECISION`
- `OPEN_PROTOCOL_DECISION`
- `OPEN_PERSISTENCE_DECISION`
- `NO_ACTION`
- `RESEARCH_REQUIRED`

The auditor may recommend an action but must not implement product fixes in this task.

## Five-repository comparison

Every item must inspect, or explicitly mark irrelevant, these repositories:

- `opentibiabr/canary`;
- `zimbadev/crystalserver`;
- `blakinio/canary`;
- `blakinio/Otheryn`;
- maintained OTClient at the pinned revision for client, packet, opcode, rendering or protocol claims.

For each repository record the exact path or search evidence, revision, observed state and confidence. Absence must be supported by bounded path/symbol/content searches rather than assumed from repository lineage.

## Runtime-reproduction gate

A runtime plan is allowed only after expected behaviour is sufficiently specified. It must define deterministic setup, inputs, observations, cleanup, safety boundary and artifact names. Execute only safe isolated tests against disposable state. Do not mutate production, live accounts, protected data, external services or persistent player state.

When a reference is insufficient, the runtime result must be `NOT_RUN_REFERENCE_INSUFFICIENT`, not a guessed pass/fail. When the target path is absent, record `NOT_APPLICABLE` with exact repository evidence.

## Dossier schema

Each dossier must contain:

1. canonical identity and predecessor decision;
2. source claim and exact expected behaviour;
3. provenance table and version/protocol applicability;
4. five-repository static comparison;
5. deterministic reproduction plan or exact reason it cannot be written;
6. execution evidence and artifacts when run;
7. truth status, static conclusion, runtime conclusion and owner action;
8. confidence, conflicts, drift and unresolved questions.

No dossier is complete when any required conclusion is missing or when conclusions exceed the cited evidence.
