---
task_id: OTH-20260815-otbm-atlas-extraction-review
status: investigating
branch: task/OTH-20260815-otbm-atlas-extraction-review
base_branch: main
created: 2026-08-15T14:20:00+02:00
updated: 2026-08-15T14:20:00+02:00
project_lane: otheryn-content
execution_mode: chat-github
related_pr: null
owned_paths:
  - docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-extraction-review.md
  - docs/agents/tasks/archive/OTH-20260815-otbm-atlas-extraction-review.md
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

## Scope constraints

- Treat this repository as LEGACY / MIGRATION SOURCE / HISTORICAL REFERENCE.
- Do not rename the repository, create a destination repository, run `git filter-repo`, move Atlas code, or delete legacy code.
- Produce only the architecture review and a precise future extraction/migration plan.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-15T14:20:00+02:00
head: 5e87f6cb50681b3f9b00d3eb4fbdaf2c0509f461
branch: task/OTH-20260815-otbm-atlas-extraction-review
pr: none
status: investigating
context_routes:
  - none
owned_paths:
  - docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-extraction-review.md
  - docs/agents/tasks/archive/OTH-20260815-otbm-atlas-extraction-review.md
proven:
  - current main at task start is 5e87f6cb50681b3f9b00d3eb4fbdaf2c0509f461
  - technical Atlas implementation is concentrated under tools/otbm_atlas with additional factual extraction under tools/otbm_atlas_facts
  - current Atlas builder is explicitly pinned to vendor/map-analysis CrystalServer world/content and Tibia appearance assets
  - current browser runtime consumes generated manifest, tile images, spatial shards and search index
  - raw OTBM parser and semantic decoder currently live inside the Atlas tool namespace
  - current open PRs are unrelated PR 369, 339, 341 and 347
unknown:
  - final destination repository layout and package naming
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - moving tools/otbm_atlas wholesale into Oteryn-Atlas
changed_paths:
  - docs/agents/tasks/active/OTH-20260815-otbm-atlas-extraction-review.md
validation:
  - command: repository/API inspection
    result: PASS
    evidence: main, open PRs, task registry, Atlas source tree and history inspected through GitHub
blockers: []
next_action: write and verify the extraction review, then archive this task and open its documentation-only PR
```
