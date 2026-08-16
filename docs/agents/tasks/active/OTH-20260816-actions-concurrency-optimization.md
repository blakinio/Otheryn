---
task_id: OTH-20260816-actions-concurrency-optimization
status: active
owner: current-agent
branch: ci/OTH-20260816-actions-concurrency-optimization
base_branch: main
created: "2026-08-16T09:16:00+02:00"
updated: "2026-08-16T09:46:00+02:00"
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
- Merged PR #415 changed preview/deployment paths plus four deployment-specific files under `tools/otbm_atlas/`: `_deployed_browser_probe_core.py`, `deploy_preflight.py`, `deployed_browser_probe.py`, and `tests/test_deploy_preflight.py`.
- Those four files matched broad `tools/otbm_atlas/**` triggers in unrelated Atlas/creature/environment workflows and caused heavy general E2E/audit fanout in addition to dedicated Synology preview validation.
- On head `1d7993156b07a0af83dafd96725d2c4f1974d6b2`, unrelated label `programme:infrastructure` caused `OTBM Atlas Tests` run #160 to replace #159 and re-run standard unit/Thais/browser work because the workflow listened to every `pull_request:labeled` event.
- On head `0f484cceac2fcae8c178b9f1905610c991418f79`, controlled temporary label `type:repair` produced OTBM Atlas Tests run #167 with zero jobs and conclusion `skipped`, proving standard jobs no longer allocate runners for a non-final label. That label run still canceled standard run #164 because both events shared the same workflow-level concurrency group, exposing a second-order cancellation bug.

## Implemented change

- Removed task/checkpoint Markdown paths from factual-source and Synology-preview trigger sets.
- Added per-PR/ref `concurrency` with `cancel-in-progress: true` to factual-source and Synology-preview workflows.
- Added `_deployed_browser_probe_core.py` to the dedicated preview trigger and compile check.
- Added exact negative filters for the four deployment-only tool paths to the broad Atlas suite, canonical creature showcase, creature animation E2E, independent creature animation audit, and environment animation E2E.
- Added superseded-run cancellation to every broad heavy workflow changed by this task.
- Standard Atlas unit, canonical Thais and browser E2E jobs skip `labeled` events; `labeled` remains only for the existing `ci:final-gate` full-world path.
- Atlas Tests concurrency now separates ordinary validation (`standard`) from labeled events and isolates each label by `github.event.label.name`. An unrelated label can therefore neither allocate standard Atlas runners nor cancel an in-flight standard/final-gate run.
- Preserved other `tools/otbm_atlas/**`, vendor, workflow-file and manual-dispatch triggers; mixed deployment + functional changes still emit applicable heavy validation.
- Preserved every real factual source/vendor path in the facts workflow.
- Core Otheryn CI and Required semantics remain untouched.

## Acceptance inventory

- [x] Remove task/checkpoint Markdown paths from heavy Atlas workflow path triggers; real deploy/tool/vendor/workflow inputs remain covered.
- [x] Add superseded-run cancellation to specialized factual/preview and broad heavy workflows.
- [x] Dedicated Synology preview covers all four deployment-only tool files and compiles the probe core plus wrappers.
- [x] Deployment-only changes are excluded from unrelated Atlas/creature/environment heavy workflows while mixed relevant changes still match positive paths.
- [x] Unrelated PR label events allocate no standard Atlas unit/canonical/browser runner jobs; `ci:final-gate` retains its full-world launch path.
- [x] Label-event concurrency is isolated from standard validation and by label name, preventing unrelated labels from canceling standard or final-gate work.
- [x] Do not route required validation to self-hosted runners while live runner availability remains unproven.
- [x] Do not change core Otheryn CI scope or Required semantics.
- [ ] Validate exact final workflow syntax and changed-file diff.
- [ ] On the final head, prove a non-final label run is skipped without canceling the simultaneously active standard Atlas run.
- [ ] Require repository-required and applicable specialized checks on the exact final head before merge.
- [ ] After merge, archive this task via a docs-only closeout PR and verify heavy Atlas workflows are not emitted solely because this task record moves to archive.
- [x] No owner-funded AI/Codex/OpenAI quota is used.

## Coordination

- Existing OTClient PR #280 owns dedicated Synology runner provisioning for `synology-otclient-01` and `synology-ots-01`; this task does not duplicate or redefine that runner stack.
- Current open Otheryn PRs were re-inventoried before expanding workflow ownership; none of the other open PRs owns the OTBM workflow paths claimed here.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-08-16T09:46:00+02:00
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
  - task-only trigger waste from PR #416
  - deployment-only broad trigger waste from PR #415
  - dedicated preview owns all four deployment-only tool files and compiles the probe core
  - five unrelated broad workflows exclude only those four deployment-tool paths
  - all seven specialized workflows changed here cancel superseded same-scope work
  - non-final label run #167 emitted zero jobs, but exposed cross-scope workflow cancellation
  - Atlas Tests concurrency now isolates standard validation and each label name
  - core CI untouched
next_action: run the final exact-head non-final-label isolation proof while standard Atlas validation is active, then complete exact-head CI/review/merge gates
```
