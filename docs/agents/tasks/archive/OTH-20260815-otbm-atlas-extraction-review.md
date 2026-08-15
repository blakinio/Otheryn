---
task_id: OTH-20260815-otbm-atlas-extraction-review
status: completed
branch: task/OTH-20260815-otbm-atlas-extraction-review
base_branch: main
created: 2026-08-15T14:20:00+02:00
updated: 2026-08-15T21:32:00+02:00
project_lane: otheryn-content
execution_mode: chat-github
related_pr: 407
ownership_released: true
owned_paths:
  - docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md
required_reads:
  - AGENTS.md
  - AGENTS.override.md
  - docs/agents/AGENTS.md
  - docs/agents/EXECUTION_PROTOCOL.md
  - tools/otbm_atlas/README.md
  - docs/maps/otbm-atlas-product-readiness-backlog-20260815.md
search_first: []
optional_reads: []
---

# OTBM Atlas pre-migration extraction review

## Goal

Audit the current OTBM Atlas in legacy `blakinio/Otheryn` and document future ownership between `Oteryn-Atlas`, `Oteryn-Game`, legacy-only, rewrite, and drop buckets without implementing migration or repository extraction.

## Result

- Verdict: `EXTRACTABLE_WITH_REFACTOR`.
- Report: `docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md`.
- PR: #407.
- No migration, repository creation/rename, `git filter-repo`, code move, legacy deletion, or runtime change was performed.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T21:32:00+02:00
head: branch head recorded by PR 407
branch: task/OTH-20260815-otbm-atlas-extraction-review
pr: 407
status: completed
context_routes:
  - none
owned_paths:
  - docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md
proven:
  - task began from main 5e87f6cb50681b3f9b00d3eb4fbdaf2c0509f461
  - main advanced during the audit to 596c37c832a75999f4049b4b16a79ed47b1dbf9b via PR 405, changing only the codec benchmark/report corpus identity details and not the audited ownership architecture
  - Atlas implementation is concentrated under tools/otbm_atlas with Crystal factual extraction under tools/otbm_atlas_facts
  - raw OTBM parser and semantic decoder are currently Atlas-namespaced but are future Oteryn-Game responsibilities
  - browser viewer, URL/deep-link state, bounded caches, spatial/search projection and publication verification are future Oteryn-Atlas responsibilities
  - tools/otbm_atlas/atlas.py and factual_layers.py are mixed ownership hotspots and must be split/reimplemented before clean path extraction
  - generated build artifacts are ignored and must be regenerated rather than history-extracted
  - path-scoped Atlas Git history exists and can be preserved selectively after ownership refactor
  - PR 407 merged the audit as main commit 7fccfccdd4d6380acbefd0c8e509dee6f4989488
  - revalidation at main 92ad2ef36d31fe0ada838d55032ffd29907f1b6b found that post-audit PRs 408 and 409 touched only the codec benchmark and benchmark research artifacts, so they do not change the ownership or extraction verdict
derived:
  - the EXTRACTABLE_WITH_REFACTOR verdict remains valid at main 92ad2ef36d31fe0ada838d55032ffd29907f1b6b
  - the two post-audit codec benchmark fixes do not require a new architecture report revision
unknown:
  - exact destination package layout and implementation language
  - final Game-to-Atlas export serialization format
  - redistribution policy for Tibia-derived imagery/assets
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - moving tools/otbm_atlas wholesale into Oteryn-Atlas
  - treating legacy OTBM Tile/Item dataclasses as the future canonical World Model
  - extracting generated build artifacts as source history
changed_paths:
  - docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md
  - docs/agents/tasks/archive/OTH-20260815-otbm-atlas-extraction-review.md
validation:
  - command: GitHub source/tree/history inspection
    result: PASS
    evidence: current source modules, dedicated Atlas workflows, task registry, open PRs and path-scoped commits inspected
  - command: scope review
    result: PASS
    evidence: documentation/task changes only; no migration/runtime/source implementation changes
  - command: current-main revalidation
    result: PASS
    evidence: main 92ad2ef36d31fe0ada838d55032ffd29907f1b6b; PR 408 changed docs/research/otbm-atlas-webp-lossless-benchmark/report.md, docs/research/otbm-atlas-webp-lossless-benchmark/summary.json and tools/otbm_atlas/codec_benchmark.py; PR 409 changed only tools/otbm_atlas/codec_benchmark.py
blockers: []
next_action: Retain this archived audit as the migration-source decision record; start any migration only under a separately authorized task.
```
