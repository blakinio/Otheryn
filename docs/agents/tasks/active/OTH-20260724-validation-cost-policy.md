---
task_id: OTH-20260724-validation-cost-policy
status: validating
branch: dudantas/validation-cost-policy
base_branch: main
created: 2026-07-24
updated: 2026-07-24
related_pr: "93"
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-validation-cost-policy.md
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

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T08:52:00+02:00
branch: dudantas/validation-cost-policy
pr: 93
status: validating
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260724-validation-cost-policy.md
  - AGENTS.md
proven:
  - Root AGENTS.md now states that a commit or small task step does not by itself justify compilation.
  - Multi-step OTBM or gameplay packages use cheap focused checks during each step and normally compile once after the steps form one reviewable milestone.
  - Early compilation remains required for CMake/build manifests, source registration, dependencies, toolchains, generated compile inputs, public headers/ABI, required binaries or material compile-break risk.
  - Documentation, task records, metadata and script-only commits explicitly avoid compilation.
derived:
  - Otheryn agents can complete multi-step packages without repeated full builds while preserving exact-final-head validation for compiled changes.
unknown:
  - Exact current-head required-check conclusions until PR 93 is marked ready and workflows complete.
conflicts: []
changed_paths:
  - AGENTS.md
  - docs/agents/tasks/active/OTH-20260724-validation-cost-policy.md
validation:
  - command: exact PR patch and changed-file audit
    result: PASS
    evidence: PR 93 changes only root agent instructions and the task record; no runtime, build-system, datapack or asset path changed.
blockers: []
next_action: Mark PR 93 ready, inspect the exact-head required checks and merge only after the governance/documentation gates pass.
```
