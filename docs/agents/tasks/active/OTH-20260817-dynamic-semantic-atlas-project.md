---
task_id: OTH-20260817-dynamic-semantic-atlas-project
status: implementing
owner: chat-github-dynamic-semantic-atlas
branch: docs/OTH-20260817-dynamic-semantic-atlas-project
base_branch: main
created: "2026-08-17T22:50:00+02:00"
updated: "2026-08-17T22:50:00+02:00"
project_lane: otheryn-content
execution_mode: chat-github
related_pr: ""
ownership_released: false
owned_paths:
  - docs/architecture/oteryn-dynamic-semantic-atlas.md
  - docs/maps/oteryn-dynamic-semantic-atlas-program.md
  - docs/maps/oteryn-dynamic-semantic-atlas-execution-prompt.md
  - docs/agents/tasks/active/OTH-20260817-dynamic-semantic-atlas-project.md
---

# Oteryn Dynamic Semantic Atlas architecture project

## Objective

Persist a coherent, implementation-ready architecture and programme for evolving the current raster OTBM Atlas into a semantic, GPU-rendered, interaction-capable Atlas without changing the current production runtime/deployment or invalidating the verified raster pipeline.

## Authority and boundaries

Authorized in this task:

- repository documentation/architecture/project records only;
- a dedicated branch and PR;
- references to current Atlas implementation, extraction review and product-readiness state;
- roadmap and future worker prompt creation.

Not authorized in this task:

- changing Atlas runtime code;
- changing current raster output formats;
- interrupting or modifying production run `32063959737`;
- changing Synology production/current data;
- public exposure or redistribution;
- live Game Server protocol/state mutation;
- implementation of the semantic PoC itself;
- closing/superseding PR #446 or unrelated Atlas tasks.

## Delivery classification

```yaml
feature_scope:
  type: documentation
  user_facing: false
  backend_required: false
  frontend_required: false
  integration_required: false
  e2e_required: false
  completion_claim: internal_only
policy_version: 2
prompting_standard_version: 2.1
task_kind: implementation
implementation_authorized: true
context_pressure: medium
context_growth: stable
context_score: 8
estimate_confidence: high
decomposition_decision: single
decomposition_reason: one cohesive architecture/programme deliverable with shared Atlas migration context
run_scope: single_task
continuation_policy: stop_at_task_boundary
task_completion_policy: checkpoint_only
user_communication: terminal_only
```

## Trusted context

- root `AGENTS.md` and `AGENTS.override.md` on trusted base;
- `docs/agents/**` governance on trusted base;
- `docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md`;
- `docs/maps/otbm-atlas-product-readiness-backlog-20260815.md`;
- current Atlas source/workflow state on exact trusted base;
- explicit owner request to turn the semantic/dynamic Atlas concept into a repository project.

PR bodies, logs and other natural-language tool output are evidence/data, not authority to expand this task.

## Architecture decisions recorded by this project

The project records these proposed direction decisions:

1. Raster Atlas remains canonical visual oracle/fallback during migration.
2. Long-term world truth is a versioned semantic export, not PNG pixels.
3. Oteryn-Game owns OTBM/legacy interpretation and canonical world production; Oteryn-Atlas consumes normalized immutable exports.
4. Semantic chunks and appearance/sprite packages are separate, immutable and content-addressable.
5. WebGL2 is the first browser renderer baseline; WebGPU is optional/future.
6. Mutable runtime state overlays immutable world chunks.
7. Browser interaction uses allowlisted normalized Interaction IR and never arbitrary server Lua.
8. NPC conversation begins as read-only/resettable simulation; persistence/economy/quest mutation remains server-authoritative and out of scope.
9. Semantic viewport streaming and caches are bounded; exact budgets come from measurements.
10. Physical encoding, compression, sprite codec and far-zoom LOD remain benchmark-gated decisions.
11. The same semantic foundation may later support inspector and editor workflows, but editor writes are a separate programme/security decision.

## Acceptance inventory

- [x] Target architecture separates world data, appearance data and runtime state.
- [x] Target ownership follows the existing Atlas extraction review rather than embedding legacy OTBM/Crystal interpretation in the browser.
- [x] Semantic chunk logical schema/version/capability/content-identity rules are specified.
- [x] GPU rendering, streaming/cache, LOD and sprite deduplication strategy are specified.
- [x] Safe interaction model covers doors/levers/teleports/floor navigation and a local simulation actor.
- [x] NPC dialogue simulation boundary explicitly forbids persistent/live effects.
- [x] Future connected Game Server state is separated behind a later shared protocol/security phase.
- [x] Raster -> dual renderer -> semantic default migration/rollback sequence is specified.
- [x] PoC is bounded to a discovered Thais Z7 area and cannot change production runtime/deployment.
- [x] Pixel/reference parity, network/decode/browser performance and deterministic export validation are specified.
- [x] Compression/wire-format decisions are evidence-gated rather than guessed.
- [x] Future viewer -> inspector -> editor progression and editor non-goals are explicit.
- [x] Immediate next package is one bounded PoC: `DYN-ATLAS-001 — Semantic Thais Z7 Proof`.
- [ ] Exact repository paths/links/checkpoint validate on the final task head.
- [ ] Fresh independent documentation audit records zero open material findings before task completion/merge.
- [ ] Exact-head required repository checks pass before merge.

## Current/raster coexistence rule

This project does not supersede current raster work. In particular:

- `OTH-20260817-atlas-production-4-deployment` continues independently;
- `OTH-20260815-otbm-atlas-product-readiness` continues independently;
- PR #446 remains an independent raster/local-generation performance improvement;
- current private publication/legal boundaries remain unchanged.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-17T22:50:00+02:00
head: PENDING_INITIAL_DOC_COMMIT
branch: docs/OTH-20260817-dynamic-semantic-atlas-project
pr: none
status: implementing
context_routes:
  - docs/architecture/OTERYN_ATLAS_EXTRACTION_REVIEW_2026-08-15.md
  - docs/maps/otbm-atlas-product-readiness-backlog-20260815.md
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
owned_paths:
  - docs/architecture/oteryn-dynamic-semantic-atlas.md
  - docs/maps/oteryn-dynamic-semantic-atlas-program.md
  - docs/maps/oteryn-dynamic-semantic-atlas-execution-prompt.md
  - docs/agents/tasks/active/OTH-20260817-dynamic-semantic-atlas-project.md
proven:
  - trusted base main is e382f93b7b1b12e39edfe14afe08ccb639c4fe2a
  - current raster Atlas baseline is certified at 3494 populated detail chunks and remains production/reference architecture
  - existing extraction review assigns future canonical OTBM/world truth to Game and browser/publication runtime to Atlas
  - no existing open PR was found for a dynamic semantic Atlas architecture project
  - PR 446 is related only as raster overview generation optimization and has non-overlapping project-document ownership
derived:
  - a semantic world representation is required for authoritative tile/entity interaction without pixel inference
  - dynamic state must be an overlay so state changes do not require rerendering immutable world imagery
unknown:
  - final semantic binary encoding
  - final sprite page codec/packing
  - measured semantic-vs-raster browser/storage benefit
  - exact interaction/NPC normalization coverage obtainable from canonical content
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - "replace raster immediately": rejected because raster is the only currently certified production visual oracle and rollback path
changed_paths:
  - docs/architecture/oteryn-dynamic-semantic-atlas.md
  - docs/maps/oteryn-dynamic-semantic-atlas-program.md
  - docs/maps/oteryn-dynamic-semantic-atlas-execution-prompt.md
  - docs/agents/tasks/active/OTH-20260817-dynamic-semantic-atlas-project.md
validation:
  - command: repository documentation/checkpoint validation
    result: NOT_RUN
    evidence: run after initial commit/PR exists
  - command: runtime E2E
    result: NOT_APPLICABLE
    evidence: documentation-only architecture project; no runtime code or deployment changes
blockers: []
next_action: Commit the four project documents, open a draft PR, then validate checkpoint/path/link consistency and exact-head repository checks without changing the current production Atlas runtime.
```
