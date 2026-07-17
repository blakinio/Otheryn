# OAM-010 Character Progression Target Proof Scope

This proof-only target slice validates the existing Otheryn `character-progression` substrate without changing production runtime behavior.

## Exact baseline

- target: `blakinio/Otheryn@f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`
- canonical module: `character-progression`

## Proof boundary

Focused tests exercise the existing target implementation for:

- monotonic experience thresholds;
- offline-training time upper/lower bounds;
- regular-skill advancement through `addOfflineTrainingTries`;
- magic-level advancement through `addOfflineTrainingTries`.

The zero-stamina experience gate remains source-reviewed compatibility evidence rather than a unit-test claim in this slice. Exercising `gainExperience` in the minimal unit harness crosses broader runtime callback/global-service boundaries, so OAM-010 does not create a second harness merely to force that path.

No production `Player`, IOLoginData, persistence, protocol, client, database, map or gameplay source is changed by this target slice.

## Deliberate exclusion

Legacy Canary contains a session-coupled disconnect-death-protection extension that can set death loss to zero and preserve blessings after a protected disconnect. The pinned Otheryn target and pinned upstream do not contain that behavior.

This proof does not import that legacy extension. Its presence prevents treating the whole legacy `character-progression` boundary as unconditional `REUSE`; any future adoption of disconnect-death protection requires its own explicit session/protocol/runtime evidence and authorization.
