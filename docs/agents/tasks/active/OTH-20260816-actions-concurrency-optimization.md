---
task_id: OTH-20260816-actions-concurrency-optimization
status: active
owner: current-agent
branch: ci/OTH-20260816-actions-concurrency-optimization
base_branch: main
created: "2026-08-16T09:16:00+02:00"
updated: "2026-08-16T09:20:00+02:00"
project_lane: infrastructure
execution_mode: chat-github
related_pr: "417"
ownership_released: false
owned_paths:
  - .github/workflows/otbm-atlas-facts-tests.yml
  - .github/workflows/otbm-atlas-synology-preview.yml
  - docs/agents/tasks/active/OTH-20260816-actions-concurrency-optimization.md
  - docs/agents/tasks/archive/OTH-20260816-actions-concurrency-optimization.md
---

# GitHub Actions concurrency optimization

## Goal

Reduce avoidable GitHub-hosted runner occupancy in OTBM Atlas validation without weakening real source/tool/deployment validation.

## Verified trigger waste

- PR #416 changes only `docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md`.
- That task path was listed in `.github/workflows/otbm-atlas-synology-preview.yml`, so the docs-only handoff emitted and completed the heavy Docker preview workflow even though no deployment/tool/workflow input changed.
- `.github/workflows/otbm-atlas-facts-tests.yml` similarly listed active/archive task-record paths, so task bookkeeping could allocate two Atlas factual-source jobs without changing factual inputs.
- Core `.github/workflows/ci.yml` already has per-PR/ref `cancel-in-progress: true`; the two specialized workflows did not.
- Live Actions state showed seven Otheryn workflows in progress while other repositories were also contending for the owner's GitHub Pro hosted-runner pool.
- Merged PR #415 changed preview/deployment paths plus four deployment-specific files under `tools/otbm_atlas/`, explaining why broad `tools/otbm_atlas/**` consumers also fanned out. Further narrowing of those broad consumers requires dependency-safe routing proof and is not silently assumed in this task.

## Implemented change

- Removed task/checkpoint Markdown paths from both heavy workflow trigger sets.
- Added per-PR/ref `concurrency` with `cancel-in-progress: true` to both specialized workflows.
- Preserved every real factual source/vendor path in the facts workflow.
- Preserved every explicit deploy/preflight/workflow path in the Synology preview workflow.
- Core Otheryn CI and required semantics are untouched.

## Acceptance inventory

- [x] Remove task/checkpoint Markdown paths from heavy Atlas workflow path triggers; real deploy/tool/vendor/workflow inputs remain covered.
- [x] Add per-PR/ref concurrency with `cancel-in-progress: true` to the two affected specialized workflows so superseded commits do not retain runner slots.
- [x] Do not route required validation to self-hosted runners while live runner availability remains unproven.
- [x] Do not change core Otheryn CI scope or required semantics.
- [ ] Validate workflow syntax and exact changed-file diff.
- [ ] Observe the implementation PR's emitted checks and require repository-required checks on the exact final head.
- [ ] After merge, archive this task via a docs-only closeout PR and verify the heavy Atlas workflows are not emitted solely because this task record moves to archive.
- [x] No owner-funded AI/Codex/OpenAI quota is used.

## Coordination

- Existing OTClient PR #280 owns dedicated Synology runner provisioning for `synology-otclient-01` and `synology-ots-01`; this task does not duplicate or redefine that runner stack.
- Existing Otheryn PR #416 owns only the Atlas product-readiness task record; this task does not edit that record.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-16T09:20:00+02:00
branch: ci/OTH-20260816-actions-concurrency-optimization
pr: 417
status: active
phase: validation
owned_paths:
  - .github/workflows/otbm-atlas-facts-tests.yml
  - .github/workflows/otbm-atlas-synology-preview.yml
  - docs/agents/tasks/active/OTH-20260816-actions-concurrency-optimization.md
proven:
  - task-only trigger paths removed from both heavy workflows
  - stale-run cancellation concurrency added to both heavy workflows
  - core CI untouched
next_action: inspect PR #417 exact diff and emitted checks; merge only after exact-head required CI and workflow validation are green
```
