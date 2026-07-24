---
task_id: OTH-20260724-validation-cost-policy
status: completed
branch: dudantas/validation-cost-policy
base_branch: main
created: 2026-07-24
updated: 2026-07-24
completed: 2026-07-24T09:27:16+02:00
last_verified_commit: "00603f8953d19e175add1eb7a502f7d07666993b"
related_pr: "93"
owned_paths:
  - docs/agents/tasks/archive/OTH-20260724-validation-cost-policy.md
  - AGENTS.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - AGENTS.md
optional_reads: []
---

# Risk-based validation policy

## Goal

Make compilation and test scope proportional to changed paths, risk and coherent project milestones. Agents perform focused checks during individual steps, defer heavy compilation until a phase or implementation package is complete, and still build early for CMake, dependency, ABI or other blocking-risk changes.

## Acceptance criteria

- [x] Small task steps do not trigger compilation merely because they create a commit.
- [x] Multi-step OTBM/gameplay work compiles at coherent milestone completion by default.
- [x] Build-system, dependency, ABI and blocking-risk exceptions remain explicit.
- [x] Documentation and script-only work uses focused validation instead of C++ compilation.
- [x] PR #93 passed the required gate and was merged.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T09:27:16+02:00
head: 00603f8953d19e175add1eb7a502f7d07666993b
branch: main
pr: 93
status: completed
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.md
  - docs/agents/tasks/archive/OTH-20260724-validation-cost-policy.md
proven:
  - Root AGENTS.md states that a commit or small task step does not by itself justify compilation.
  - Multi-step OTBM or gameplay packages use focused checks during each step and normally compile once after the steps form one reviewable milestone.
  - Early compilation remains required for build-system, dependency, toolchain, generated-input, public-header/ABI, verified-binary or material compile-break risks.
  - Documentation, task records, metadata and script-only commits do not require compilation.
  - Required run 30073810677 succeeded after rerunning the previously unstarted failed job.
  - PR 93 was squash-merged as 00603f8953d19e175add1eb7a502f7d07666993b.
derived:
  - The earlier failures without steps or logs were runner/infrastructure failures rather than failures in the policy change.
unknown: []
conflicts: []
first_failure:
  marker: Required workflow did not start steps
  evidence: Earlier attempts exposed no steps and returned BlobNotFound for job logs.
rejected_hypotheses:
  - The failure was not caused by C++, CMake, dependencies, datapacks or platform code because PR 93 changed only AGENTS.md and its task record.
changed_paths:
  - AGENTS.md
  - docs/agents/tasks/archive/OTH-20260724-validation-cost-policy.md
validation:
  - command: Required workflow rerun 30073810677
    result: PASS
    evidence: Checkout and Require applicable CI workflows completed successfully on exact PR head 0e1d0595e32d334457bb726f714d56344625c28f.
  - command: squash merge PR 93
    result: PASS
    evidence: GitHub created merge commit 00603f8953d19e175add1eb7a502f7d07666993b.
blockers: []
next_action: NONE
```

## Completion

- Feature PR: #93.
- Feature head: `0e1d0595e32d334457bb726f714d56344625c28f`.
- Merge commit: `00603f8953d19e175add1eb7a502f7d07666993b`.
- Merged at: `2026-07-24T09:27:16+02:00`.
