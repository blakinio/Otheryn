# Global Tibia Verification Coverage

Shared programme: `OTS-20260813-world-reconstruction-navigation`.

## Purpose

This document defines how OTBM Atlas represents what has been observed and verified against Tibia Global, what remains unverified, which areas are normally reachable, and which locations require conditional/special/admin access.

The same durable coverage state is intended to support two consumers:

1. the Atlas UI for a human operator;
2. the exploration planner for the Track A agent.

There must not be separate human and agent notions of coverage.

## Sources of truth

Atlas compares two independent sources:

```text
CANONICAL
  Otheryn canonical OTBM tile facts

REAL_TIBIA
  promoted, sanitized Track A observation facts
```

The comparison result is derived and may be recomputed whenever canonical OTBM changes. Real Tibia evidence is retained independently.

## Tile verification status

Every tile has one verification status for a given current comparison revision:

| Status | Meaning |
|---|---|
| `UNOBSERVED` | no promoted complete/partial observation has been indexed for this tile |
| `OBSERVED` | factual observation exists but full comparison is not yet established |
| `PARTIAL` | only incremental/incomplete tile knowledge exists |
| `IDENTITY_UNRESOLVED` | enough tile structure exists to observe the tile, but one or more required identities cannot be safely mapped to canonical identity |
| `VERIFIED_MATCH` | applicable complete static comparison is proven equal |
| `VERIFIED_DIFFERENT` | applicable complete static comparison is proven different |
| `CONFLICT` | promoted observations disagree materially and no accepted resolution exists |
| `STALE` | evidence is retained but current policy/version/revision says it requires revalidation before being counted as current verification |

`OBSERVED` is deliberately weaker than `VERIFIED_*`.

A tile with dynamic creatures/effects may still be verified for its comparable static geometry. Dynamic-only differences are not automatically canonical-map differences.

## Accessibility status

Accessibility is a second independent dimension:

| Status | Meaning |
|---|---|
| `UNKNOWN` | normal-player reachability has not been established |
| `NORMAL_REACHABLE` | ordinary traversal to the area is proven under normal playable conditions |
| `CONDITIONALLY_REACHABLE` | reachable only with a known/nontrivial condition such as quest/instance/world state or explicit transition requirement |
| `SPECIAL_ACCESS_REQUIRED` | requires a special access mechanism not available during ordinary unrestricted traversal |
| `ADMIN_OR_TELEPORT_REQUIRED` | known to require GM/admin/privileged teleport or equivalent non-normal access for direct verification |
| `PROVEN_UNREACHABLE_BY_NORMAL_PLAYER` | evidence proves an ordinary player cannot reach the tile under the modeled conditions |

A failed route attempt never by itself promotes a tile to `PROVEN_UNREACHABLE_BY_NORMAL_PLAYER`.

## Acquisition method provenance

Where known, an observation should retain how the observed position became available. Suggested vocabulary:

- `NORMAL_TRAVERSAL`
- `CONDITIONAL_TRAVERSAL`
- `TRANSITION`
- `TELEPORT`
- `ADMIN_TELEPORT`
- `PASSIVE_WORLD_STREAM`
- `OTHER_VERIFIED_METHOD`

Acquisition method and accessibility are related but not identical. A tile observed through admin teleport may be fully verified while correctly remaining `ADMIN_OR_TELEPORT_REQUIRED` for normal-player planning.

## Observation index semantics

Track A owns the producer-side observation index. Atlas only consumes promoted sanitized evidence.

The index should support at least:

- absolute position `x/y/z`;
- latest accepted tile observation;
- complete/partial knowledge state;
- ordered observed contents;
- raw identities and factual categories;
- deterministic tile fingerprint;
- first/last observation metadata;
- observation count;
- exact producer/client provenance;
- session/source provenance;
- observation history when material state changes;
- acquisition method when established.

If repeated observation has the same deterministic fingerprint, the producer may increment counters/timestamps rather than duplicate equivalent full snapshots. If the fingerprint changes, history is preserved rather than overwritten without provenance.

The initial implementation may use SQLite or another local store; storage technology is not part of the cross-repository semantic contract.

## Chunk export

The promoted transfer format should align with Atlas's existing 128x128 world chunks:

```text
real-tibia/
  chunks/
    z<floor>/
      <chunkX>_<chunkY>.<bundle-format>
```

Only dirty/changed observation chunks need to be exported after the initial state. Each bundle must be deterministic for the same accepted observation state and preserve enough provenance for Atlas to validate the source boundary.

The first implementation should prefer file/artifact transfer over a live direct runtime API. A streaming/service implementation can be introduced later without changing tile/coverage semantics.

## Atlas comparison model

Atlas stores comparison separately from both source layers.

Conceptually:

```text
CANONICAL tile
    +
REAL_TIBIA tile
    +
identity resolution
    +
comparison policy
    -> COMPARISON result
```

Identity state is explicit:

- `VERIFIED`
- `AMBIGUOUS`
- `UNKNOWN`

Raw client/appearance IDs are never assumed to equal OTBM server IDs, even when client asset versions match.

## Human presentation

Atlas must expose a selectable map mode with at least:

- `Otheryn / Canonical`
- `Real Tibia`
- `Difference`
- `Global Coverage`

### Global Coverage layer

At close zoom, tiles can show individual status. At lower zoom, Atlas aggregates by 128x128 chunk.

Required verification filters:

- unobserved;
- observed;
- partial;
- identity unresolved;
- verified match;
- verified different;
- conflict;
- stale.

Required access filters:

- normal reachable;
- conditional;
- special access;
- admin/teleport required;
- proven normal-player unreachable;
- access unknown.

The visual design may use colors/patterns/icons, but it must remain distinguishable for accessibility and must not rely on one color channel alone.

## Chunk summary

For each chunk Atlas should expose a compact summary such as:

```text
floor/chunk
canonical tiles
observed tiles
fully comparable tiles
verified match
verified different
partial
identity unresolved
conflict
unobserved
normal reachable unverified
conditional unverified
special/admin-only
access unknown
```

The exact metric names may evolve, but counts must be reproducible from tile-level state.

## Coverage metrics

Do not publish one ambiguous `coverage %`.

At minimum distinguish:

1. **total-world observed coverage** — fraction of canonical/world-index tiles with any current accepted Real Tibia observation;
2. **total-world verified coverage** — fraction fully comparable and verified;
3. **normal-player-verifiable coverage** — verified fraction of the denominator currently classified as normally/conditionally verifiable by the ordinary exploration model;
4. **special/admin-only inventory** — count/area known to require non-normal access;
5. **access-unknown inventory** — count/area whose reachability remains unresolved.

This allows the programme to report, for example, high normal-player verification without falsely claiming equivalent verification of inaccessible/admin-only areas.

## Exploration frontier

A frontier is a useful boundary between currently observed/verified space and unobserved or unresolved space.

Atlas should score frontier candidates from factual coverage/access/connectivity data. A conceptual score may include:

```text
+ expected new tiles
+ nearby verified-difference value
+ conflict-resolution value
+ connectivity/discovery value
- travel cost
- repeated failure penalty
- access uncertainty penalty
```

The exact formula is an implementation decision and should remain explainable/reproducible.

## Exploration queue

Atlas publishes a machine-readable queue for the Track A agent and a human-facing queue/table for the operator.

Each queue record should identify at least:

- target floor/chunk/bounds;
- optional justified entry coordinate;
- reason;
- priority;
- estimated remaining/new coverage;
- access status/uncertainty;
- repeated-failure state where relevant.

Suggested reasons include:

- `UNOBSERVED_FRONTIER`
- `VERIFY_DIFFERENCE`
- `RESOLVE_CONFLICT`
- `RESOLVE_IDENTITY`
- `ACCESS_DISCOVERY`

Ordinary exploration must not continually requeue `ADMIN_OR_TELEPORT_REQUIRED` or `PROVEN_UNREACHABLE_BY_NORMAL_PLAYER` tiles as though a normal character could simply walk there.

## Exploration history

Atlas should retain session/run-level summaries so a human can tell whether the agent is expanding useful coverage or revisiting the same space.

Useful fields include:

- exploration/session ID;
- start/end or observation interval;
- starting region/position when available;
- new observed tiles;
- reobserved tiles;
- new verified matches/differences;
- new conflicts/unresolved identities;
- attempted frontiers and outcome;
- access classifications learned.

Presentation filters such as current session, recent period and all-time are desirable but are not part of the first storage contract.

## Agent planning boundary

The Atlas queue describes **what to verify**, not how to press keys.

Track A receives a semantic mission. It owns:

- current official-client state;
- local route/action selection;
- transitions/interactions;
- authoritative action/result verification;
- observation production after movement.

Atlas receives new promoted observations, updates the Real Tibia index/comparison/coverage and replans.

## First product slice

The smallest useful implementation slice is:

1. ingest deterministic promoted Real Tibia chunk fixtures;
2. persist Real Tibia facts separately from canonical facts;
3. compare complete resolvable tiles;
4. compute tile and chunk verification/access summaries;
5. expose `Global Coverage` view and basic filters;
6. expose machine-readable unobserved/frontier queue.

Autonomous runtime movement is not required to validate this first Atlas slice.
