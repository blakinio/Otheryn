---
task_id: OTH-20260816-required-concurrency
status: active
owner: current-agent
branch: ci/OTH-20260816-required-concurrency
base_branch: main
created: "2026-08-16T09:50:00+02:00"
updated: "2026-08-16T09:50:00+02:00"
project_lane: infrastructure
execution_mode: chat-github
related_pr: pending
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

- `.github/workflows/required.yml` runs on PR open/synchronize/reopen/ready-for-review and has no workflow-level concurrency control.
- Its `Required` job polls Actions every 10 seconds for up to 35 minutes while waiting for applicable workflows on the exact PR head.
- Core `.github/workflows/ci.yml` already cancels superseded same-PR work, so keeping an obsolete Required poller provides no latest-head validation value.
- No open PR currently owns `.github/workflows/required.yml`.

## Acceptance inventory

- [ ] Add per-PR/ref `concurrency` with `cancel-in-progress: true` to `Required`.
- [ ] Do not change changed-path classification, applicable workflow names, exact-head matching, timeout, polling or success/failure semantics.
- [ ] Exact-head repository CI/Required succeeds.
- [ ] Controlled synchronize evidence proves an older Required run becomes cancelled/superseded while the newest head retains its Required gate.
- [ ] No OTBM Atlas/creature/environment specialized workflow is triggered solely by this task/workflow change unless independently applicable.
- [ ] No owner-funded AI/Codex/OpenAI quota is used.

## Context checkpoint

```yaml
state: PROVEN
phase: implementation
branch: ci/OTH-20260816-required-concurrency
pr: pending
owned_paths:
  - .github/workflows/required.yml
  - docs/agents/tasks/active/OTH-20260816-required-concurrency.md
next_action: open an early draft PR and add only same-PR stale-run concurrency to Required
```
