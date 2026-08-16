# World Reconstruction & Navigation

Shared ID: `OTS-20260813-world-reconstruction-navigation`.

## Current architecture

This programme compares the canonical Otheryn OTBM world with facts observed from the **official native Linux Tibia client** through Track A `official-client-re` in `blakinio/otclient`.

Track B / the open-source OTClient-to-Global compatibility runtime is not the live producer and is not the local navigator for this programme.

The durable boundary is:

```text
official Tibia Linux client / Track A
  -> structurally verified world observations
  -> local observation index + promoted sanitized changed-chunk bundles
  -> Otheryn Atlas REAL_TIBIA evidence layer
  -> canonical comparison + coverage/access model
  -> exploration targets / candidate corrections
```

Canonical `world.otbm` is never directly mutated by the live producer.

## Ownership

### Track A / blakinio/otclient

Owns:

- exact-client structural player/world state;
- authoritative absolute positions where proven;
- ordered observed tile contents;
- observation provenance and exact-client fencing;
- local durable observation indexing/deduplication;
- physical runtime/session/action evidence through the Track A runtime governance model;
- local native action execution and resulting-state verification;
- deterministic sanitized observation export.

### Otheryn / OTBM Atlas

Owns:

- canonical OTBM tile facts;
- `REAL_TIBIA` evidence ingestion and storage;
- identity resolution against canonical server/OTB identities;
- canonical-vs-Real-Tibia comparison;
- verification coverage and accessibility classification;
- chunk/frontier scoring and exploration queue;
- global semantic connectivity/mission planning;
- human-facing Global Coverage and Difference presentation;
- reviewable candidate OTBM corrections.

## Evidence layers

Each tile is modeled through independent layers:

- `CANONICAL` — current Otheryn map fact;
- `REAL_TIBIA` — preserved promoted observation fact;
- `COMPARISON` — result against the current canonical revision;
- `CANDIDATE` — optional proposed correction.

Observations are never discarded merely because the canonical map later changes. Atlas re-runs comparison against preserved evidence.

## Observation contract

Track A currently uses the producer-neutral `MAP_OBSERVATION_V1` semantics. The important invariants remain:

- absolute `x/y/z`;
- explicit `FULL`, `EMPTY`, `PARTIAL`, `UNKNOWN` knowledge;
- ordered contents;
- raw client identities preserved without assuming OTBM/server identity;
- deterministic sequence/provenance;
- decoded resulting state required for verified transitions/action success;
- no secret-bearing or raw packet payloads.

The first integration does not require a direct runtime network API. A local indexed store plus deterministic promoted chunk bundles is the preferred initial boundary.

## Chunk alignment

Atlas already uses 128x128 world chunks. Observation export and Real Tibia ingestion should use the same chunk coordinates so a small runtime discovery invalidates only the corresponding evidence/comparison/coverage chunks.

The local Track A index may use SQLite or another suitable implementation; the storage engine is not yet part of the semantic contract.

## Verification state

Minimum states:

- `UNOBSERVED`
- `OBSERVED`
- `PARTIAL`
- `IDENTITY_UNRESOLVED`
- `VERIFIED_MATCH`
- `VERIFIED_DIFFERENT`
- `CONFLICT`
- `STALE`

Observed is not the same as verified. A tile can be observed yet remain incomparable because completeness or identity is unresolved.

## Accessibility state

Accessibility is independent from verification:

- `UNKNOWN`
- `NORMAL_REACHABLE`
- `CONDITIONALLY_REACHABLE`
- `SPECIAL_ACCESS_REQUIRED`
- `ADMIN_OR_TELEPORT_REQUIRED`
- `PROVEN_UNREACHABLE_BY_NORMAL_PLAYER`

A tile seen using special/admin teleport may be verified while still correctly classified as not normally reachable. Conversely, one failed attempt to reach a tile does not prove it is unreachable.

## Atlas views

Atlas should expose at least:

1. **Otheryn / Canonical** — current map;
2. **Real Tibia** — preserved observed facts only;
3. **Difference** — comparison results;
4. **Global Coverage** — what has and has not been verified, including access class.

At close zoom the coverage layer may operate tile-by-tile. At lower zoom it should aggregate to 128x128 chunks.

Detailed coverage/product semantics are defined in `docs/maps/global-tibia-verification-coverage.md`.

## Global exploration model

Atlas is responsible for deciding **where verification is valuable next**. It should identify frontier regions and publish a machine-readable exploration queue.

Atlas sends Track A a semantic mission such as:

```text
verify region/chunk X,Y,Z
reason = UNOBSERVED_FRONTIER | VERIFY_DIFFERENCE | RESOLVE_CONFLICT
priority = ...
expected new coverage = ...
```

Atlas does not own the physical client runtime and should not prescribe blind keyboard/mouse event sequences.

Track A decides how to execute the mission from current local state and validates every material transition/action from resulting structural state.

## Viewport rule

A larger official-client worldmap viewport is useful but is not a hard dependency of reconstruction. If Track A can reliably produce absolute ordered tiles from the currently available viewport, repeated traversal can accumulate larger coverage. Viewport enlargement is therefore an accelerator rather than a programme gate.

## Identity rule

Refreshing Atlas client assets to a newer version is a separate maintenance action and is not a blocker for this architecture. Even when versions match, raw client/appearance IDs must never be assumed to equal canonical OTBM server IDs. Identity remains explicit: `VERIFIED`, `AMBIGUOUS`, `UNKNOWN`.

## Updated work streams

The programme is intentionally parallel rather than a strict P0->P7 sequence:

- **Track A state** — authoritative player/world semantic reads;
- **Track A worldmap** — tile storage, coordinates and ordered contents;
- **Track A runtime** — physical persistent session, causal/relogin evidence and later native exploration;
- **Atlas production** — canonical/incremental tile-facts pipeline;
- **Observation integration** — Track A indexed export -> Atlas Real Tibia layer;
- **Coverage/access/frontier** — UI plus machine-readable exploration queue;
- **Closed-loop exploration** — mission -> Track A -> observations -> Atlas replan;
- **Candidate reconstruction** — deterministic, evidence-linked corrections.

## First integration milestone

The first required E2E is deliberately narrower than autonomous exploration:

```text
exact official Linux client
-> structurally read absolute world tile facts
-> index/deduplicate observations
-> export promoted sanitized changed chunk
-> Atlas ingest into REAL_TIBIA
-> compare against CANONICAL
-> display verification/coverage result
```

Only after this is reliable should autonomous traversal/coverage expansion become the next integration milestone.

## Acceptance principles

- Missing observation remains unknown/unobserved, never empty.
- Verification and reachability are separate dimensions.
- Human and automated planners consume the same coverage source of truth.
- Areas requiring GM/admin teleport or other special access are not endlessly queued for an ordinary character.
- Being observed does not imply a normal walk edge exists.
- Dynamic creatures/effects are preserved as observations but do not silently become static OTBM geometry.
- Candidate corrections remain separate from canonical `world.otbm` until explicit acceptance.
