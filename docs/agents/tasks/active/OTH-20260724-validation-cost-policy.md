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

## Acceptance criteria

- [x] Small task steps do not trigger compilation merely because they create a commit.
- [x] Multi-step OTBM/gameplay work compiles at coherent milestone completion by default.
- [x] Build-system, dependency, ABI and blocking-risk exceptions remain explicit.
- [x] Documentation and script-only work uses focused validation instead of C++ compilation.

## Ownership

```yaml
owned_paths:
  - AGENTS.md
  - docs/agents/tasks/active/OTH-20260724-validation-cost-policy.md
modules:
  - agent-governance
dependencies:
  - OTS-20260724-validation-cost-policy
blockers:
  - Required workflow failure without retrievable job logs
cross_repository_tasks:
  - CAN-20260724-validation-cost-policy
  - OTC-20260724-validation-cost-policy
  - OTERYN-20260724-validation-cost-policy
```

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T09:10:00+02:00
head: 2c48d4cd8d379c1afb196be75f189ad5f2c9d599
branch: dudantas/validation-cost-policy
pr: 93
status: validating
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.md
  - docs/agents/tasks/active/OTH-20260724-validation-cost-policy.md
proven:
  - Root AGENTS.md now states that a commit or small task step does not by itself justify compilation.
  - Multi-step OTBM or gameplay packages use cheap focused checks during each step and normally compile once after the steps form one reviewable milestone.
  - Early compilation remains required for CMake/build manifests, source registration, dependencies, toolchains, generated compile inputs, public headers/ABI, required binaries or material compile-break risk.
  - Documentation, task records, metadata and script-only commits explicitly avoid compilation.
  - PR 93 changes only AGENTS.md and this task record.
  - The base Required workflow classifies neither AGENTS.md nor docs/agents/tasks/** as a path requiring CI or repository-audit workflows.
derived:
  - Otheryn agents can complete multi-step packages without repeated full builds while preserving exact-final-head validation for compiled changes.
  - The observed Required failure is in the aggregator/infrastructure path rather than a compiled runtime test selected by these changed paths.
unknown:
  - Why Required runs 30073419795 and 30073505539 failed; the connector reports no steps and GitHub returns BlobNotFound for both job-log downloads.
conflicts: []
first_failure:
  marker: Required workflow
  evidence: Required run 30073419795 failed on head 2c48d4cd8d379c1afb196be75f189ad5f2c9d599; run 30073505539 and its rerun also failed, but job logs were unavailable through the GitHub API.
rejected_hypotheses:
  - A C++ or platform build failure is not supported because the PR changes no source, CMake, dependency, workflow, test, datapack or platform path and the Required path classifier selects no CI workflow for these files.
changed_paths:
  - AGENTS.md
  - docs/agents/tasks/active/OTH-20260724-validation-cost-policy.md
validation:
  - command: exact PR patch and changed-file audit
    result: PASS
    evidence: PR 93 changes only root agent instructions and the task record; no runtime, build-system, datapack or asset path changed.
  - command: Required workflow source review
    result: PASS
    evidence: Current required.yml treats this exact two-file scope as no applicable CI or Repository Audit workflow.
  - command: Required run and rerun inspection
    result: BLOCKED
    evidence: Both failed without exposed step data; job-log downloads return BlobNotFound, so the exact platform failure cannot be proven from available evidence.
blockers:
  - Required must succeed or expose a diagnosable error before merge.
next_action: Re-evaluate Required on the new checkpoint head; if it fails identically without logs, keep PR 93 open and report the GitHub Actions infrastructure blocker without weakening the gate.
```
