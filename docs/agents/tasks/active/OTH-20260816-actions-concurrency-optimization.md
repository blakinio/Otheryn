---
task_id: OTH-20260816-actions-concurrency-optimization
status: active
owner: current-agent
branch: ci/OTH-20260816-actions-concurrency-optimization
base_branch: main
created: "2026-08-16T09:16:00+02:00"
updated: "2026-08-16T09:36:00+02:00"
project_lane: infrastructure
execution_mode: chat-github
related_pr: "417"
ownership_released: false
owned_paths:
  - .github/workflows/otbm-atlas-facts-tests.yml
  - .github/workflows/otbm-atlas-synology-preview.yml
  - .github/workflows/otbm-atlas-tests.yml
  - .github/workflows/otbm-creature-showcase.yml
  - .github/workflows/otbm-creature-animation-tests.yml
  - .github/workflows/otbm-creature-animation-audit.yml
  - .github/workflows/otbm-environment-animation-tests.yml
  - docs/agents/tasks/active/OTH-20260816-actions-concurrency-optimization.md
  - docs/agents/tasks/archive/OTH-20260816-actions-concurrency-optimization.md
---

# GitHub Actions concurrency optimization

## Goal

Reduce avoidable GitHub-hosted runner occupancy in OTBM Atlas validation without weakening real source/tool/deployment validation.

## Verified trigger waste

- Merged PR #416 changed only `docs/agents/tasks/active/OTH-20260815-otbm-atlas-product-readiness.md`.
- That task path was listed in `.github/workflows/otbm-atlas-synology-preview.yml`, so the docs-only handoff emitted and completed the heavy Docker preview workflow even though no deployment/tool/workflow input changed.
- `.github/workflows/otbm-atlas-facts-tests.yml` similarly listed active/archive task-record paths, so task bookkeeping could allocate two Atlas factual-source jobs without changing factual inputs.
- Core `.github/workflows/ci.yml` already has per-PR/ref `cancel-in-progress: true`; specialized Atlas workflows did not consistently have it.
- Live Actions state showed multiple Otheryn workflows in progress while other repositories were contending for the owner's GitHub Pro hosted-runner pool.
- Merged PR #415 changed preview/deployment paths plus four deployment-specific files under `tools/otbm_atlas/`: `_deployed_browser_probe_core.py`, `deploy_preflight.py`, `deployed_browser_probe.py`, and `tests/test_deploy_preflight.py`.
- Those four files matched broad `tools/otbm_atlas/**` triggers in unrelated Atlas/creature/environment workflows and therefore caused heavy general E2E/audit fanout in addition to the dedicated Synology preview validation.
- The dedicated Synology preview workflow now owns all four deployment-tool paths and directly compiles the probe core and public wrappers, while retaining the deployment preflight tests and immutable container contract.

## Implemented change

- Removed task/checkpoint Markdown paths from factual-source and Synology-preview trigger sets.
- Added per-PR/ref `concurrency` with `cancel-in-progress: true` to factual-source and Synology-preview workflows.
- Added `_deployed_browser_probe_core.py` to the dedicated preview trigger and compile check.
- Added exact negative filters for the four deployment-only tool paths to the broad Atlas suite, canonical creature showcase, creature animation E2E, independent creature animation audit, and environment animation E2E.
- Added per-PR/ref `concurrency` with `cancel-in-progress: true` to every broad workflow changed by this task.
- Preserved other `tools/otbm_atlas/**`, vendor, workflow-file and manual-dispatch triggers; a mixed deployment + functional change still emits the applicable heavy workflow.
- Preserved every real factual source/vendor path in the facts workflow.
- Core Otheryn CI and required semantics remain untouched.

## Acceptance inventory

- [x] Remove task/checkpoint Markdown paths from heavy Atlas workflow path triggers; real deploy/tool/vendor/workflow inputs remain covered.
- [x] Add per-PR/ref concurrency with `cancel-in-progress: true` to the factual-source and Synology-preview workflows.
- [x] Dedicated Synology preview covers all four deployment-only tool files and compiles the probe core plus wrappers.
- [x] Deployment-only changes are excluded from unrelated Atlas/creature/environment heavy workflows while mixed relevant changes still match their positive paths.
- [x] Every broad heavy workflow changed by this task cancels superseded runs for the same PR/ref.
- [x] Do not route required validation to self-hosted runners while live runner availability remains unproven.
- [x] Do not change core Otheryn CI scope or required semantics.
- [ ] Validate workflow syntax and exact changed-file diff.
- [ ] Observe the implementation PR's emitted checks and require repository-required checks on the exact final head.
- [ ] After merge, archive this task via a docs-only closeout PR and verify heavy Atlas workflows are not emitted solely because this task record moves to archive.
- [x] No owner-funded AI/Codex/OpenAI quota is used.

## Coordination

- Existing OTClient PR #280 owns dedicated Synology runner provisioning for `synology-otclient-01` and `synology-ots-01`; this task does not duplicate or redefine that runner stack.
- Current open Otheryn PRs were re-inventoried before expanding workflow ownership; none of PRs #369, #339, #341 or #347 owns the OTBM workflow paths claimed here.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-16T09:36:00+02:00
branch: ci/OTH-20260816-actions-concurrency-optimization
pr: 417
status: active
phase: validation
owned_paths:
  - .github/workflows/otbm-atlas-facts-tests.yml
  - .github/workflows/otbm-atlas-synology-preview.yml
  - .github/workflows/otbm-atlas-tests.yml
  - .github/workflows/otbm-creature-showcase.yml
  - .github/workflows/otbm-creature-animation-tests.yml
  - .github/workflows/otbm-creature-animation-audit.yml
  - .github/workflows/otbm-environment-animation-tests.yml
proven:
  - task-only trigger paths removed from factual-source and preview workflows
  - dedicated preview owns all four deployment-only tool files and compiles the probe core
  - deployment-only trigger waste independently observed from merged PR #415
  - five unrelated broad workflows exclude only those four exact deployment-tool paths
  - all seven changed specialized workflows cancel superseded same-PR/ref runs
  - core CI untouched
next_action: inspect PR #417 exact diff and exact-head emitted checks; remediate any validation failure before ready-for-review
```
