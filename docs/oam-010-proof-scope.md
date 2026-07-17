# OAM-010 Character Progression Target Proof Scope

This proof-only target slice validates the existing Otheryn character-progression substrate without changing production runtime behavior.

- Task-start target: `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`.
- Canonical module: `character-progression`.
- Production source remains unchanged.
- Focused tests cover experience thresholds, zero-stamina experience gating, offline-training time bounds, regular-skill advancement, and magic-level advancement.
- Legacy disconnect-death protection is intentionally not imported by this proof. It is a session-coupled death-loss policy divergence that requires separate authorization/evidence and prevents whole-module `REUSE`.
