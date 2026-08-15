---
task_id: OTH-20260815-otbm-atlas-creature-sprites
status: completed
branch: feat/otbm-atlas-creature-sprites
base_branch: main
created: 2026-08-15T00:16:59+02:00
updated: 2026-08-15T08:49:00+02:00
completed: 2026-08-15T08:49:00+02:00
related_pr: "395"
merge_sha: ea1810ed0a878230d1e68ad45e455c01ef7fc99d
---

# Canonical OTBM Atlas creature sprites — completed

PR #395 was squash-merged into `main` as `ea1810ed0a878230d1e68ad45e455c01ef7fc99d`.

Final delivery:

- canonical atlas world/spawn, runtime composition evidence, NPC, monster, appearance and sprite inputs are restricted to `vendor/map-analysis/**`;
- NPC and monster sprites share the bounded `CreatureSpriteRenderer` pipeline with deterministic outfit deduplication and conservative unresolved dot fallbacks;
- monster definitions support canonical names containing apostrophes and duplicate/ambiguity handling;
- NPC and monster sprite enrichment is retained through `spawns.json` and spatial sharding;
- close-zoom viewer parity is implemented while preserving low-zoom monster suppression;
- vendor-only canonical input changes trigger the pinned-data Chromium showcase.

Final exact-head PR validation passed before merge: Required, CI, OTBM Atlas Tests, OTBM Environment Animation E2E, factual-layer tests/audit, and OTBM Canonical Creature Showcase. Both review findings were fixed with regression coverage and both review threads were resolved.

Pinned corpus evidence from the validated implementation:

- NPC: 752 unique sprites, 974 resolved spawns, 94 unresolved spawns, 8 ambiguous definitions;
- monsters: 719 unique sprites, 87,193 resolved spawns, 372 unresolved spawns, 0 ambiguous definitions;
- real Chromium showcase decoded both selected creature sprites as 64x64 and produced PNG + JSON evidence.

This archive replaces the former `tasks/active` checkpoint so resume tooling cannot treat the completed PR #395 work as active.
