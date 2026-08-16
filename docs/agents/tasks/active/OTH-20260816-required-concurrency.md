---
task_id: OTH-20260816-required-concurrency
status: active
owner: current-agent
branch: ci/OTH-20260816-required-concurrency
base_branch: main
created: "2026-08-16T09:50:00+02:00"
updated: "2026-08-16T09:53:00+02:00"
project_lane: infrastructure
execution_mode: chat-github
related_pr: "420"
ownership_released: false
owned_paths:
  - .github/workflows/required.yml
  - docs/agents/tasks/active/OTH-20260816-required-concurrency.md
  - docs/agents/tasks/archive/OTH-20260816-required-concurrency.md
---

# Required workflow stale-run cancellation

## Objective

Ensure a superseded pull-request head cannot leave an obsolete `Required` job consuming a GitHub-hosted runner while it polls CI for up to 35 minutes.

## Verified evidence

- `.github/workflows/required.yml` runs on PR open/synchronize/reopen/ready-for-review and had no workflow-level concurrency control.
- Its `Required` job polls Actions every 10 seconds for up to 35 minutes while waiting for applicable workflows on the exact PR head.
- Core `.github/workflows/ci.yml` already cancels superseded same-PR work, so keeping an obsolete Required poller provides no latest-head validation value.
- No other open PR owned `.github/workflows/required.yml` when this task claimed it.
- Implementation head `a0132142a2e10f2ba9302739e603383c37a88ddc` emitted Required run #1271 (`31934841782`) before this task checkpoint creates the controlled newer synchronize head.

## Implemented change

- Added workflow concurrency group `${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}`.
- Enabled `cancel-in-progress: true`.
- Changed-path classification, applicable workflow names, exact-head matching, timeout, polling loop and success/failure semantics are byte-for-byte unchanged apart from the inserted concurrency block.

## Acceptance inventory

- [x] Add per-PR/ref `concurrency` with `cancel-in-progress: true` to `Required`.
- [x] Do not change changed-path classification, applicable workflow names, exact-head matching, timeout, polling or success/failure semantics.
- [ ] Exact-head repository CI/Required succeeds.
- [ ] Controlled synchronize evidence proves older Required #1271 becomes cancelled/superseded while the newest head retains its Required gate.
- [ ] No OTBM Atlas/creature/environment specialized workflow is triggered solely by this task/workflow change unless independently applicable.
- [x] No owner-funded AI/Codex/OpenAI quota is used.

## Context checkpoint

```yaml
state: PROVEN
phase: validation
branch: ci/OTH-20260816-required-concurrency
pr: 420
prior_head: a0132142a2e10f2ba9302739e603383c37a88ddc
prior_required_run: 31934841782
owned_paths:
  - .github/workflows/required.yml
  - docs/agents/tasks/active/OTH-20260816-required-concurrency.md
next_action: verify the prior Required run is cancelled by this newer synchronize head, then require exact-head CI/Required and closeout
```
