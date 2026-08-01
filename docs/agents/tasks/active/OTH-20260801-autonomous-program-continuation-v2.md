---
task_id: OTH-20260801-autonomous-program-continuation-v2
status: validating
project_lane: otheryn-governance
policy_version: 2
task_kind: integration
implementation_authorized: false
decomposition_decision: single
decomposition_reason: one shared governance contract and its local handover integration form one coherent documentation package
context_pressure: medium
context_growth: stable
context_score: 6
estimate_confidence: high
phase: validate
session_id: chat-20260801-autonomous-v2
session_role: coordinator
execution_mode: chat-github
branch: dudantas/autonomous-program-continuation-v2
base_branch: main
start_sha: 869899dff4b430cfa80f203df5d15c6d1b6ae845
issue: ""
feature_pr: "296"
created: 2026-08-01
updated: 2026-08-01T23:22:00+02:00
lease_expires_at: 2026-08-02T01:22:00+02:00
owned_paths:
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/tasks/active/OTH-20260801-autonomous-program-continuation-v2.md
---

# OTH-20260801 — Autonomous program continuation v2

## Goal

Make one short owner invocation authorize a long, low-noise autonomous programme run that checkpoints safely, completes and archives terminal tasks, crosses barriers, and continues with the next ready work until a real stop condition is reached.

## Scope and invariants

Exactly four governance/documentation paths. No runtime, production, database, protocol, asset, upstream, or deployment mutation is authorized. Repository-specific safety and merge gates remain authoritative.

## Acceptance criteria

- [x] Distinguish one bounded worker session from one long owner invocation.
- [x] Define autonomous continuation until a real stop.
- [x] Require terminal task finalization, archival, ownership release, barrier review, and next-READY continuation.
- [x] Route resolvable short commands into execution instead of returning a long prompt.
- [ ] Pass exact-head governance and required CI.
- [ ] Merge and archive this task.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-01T23:22:00+02:00
status: validating
phase: validate
head: 2b086e8aae22524386ef381dbe43fb921aaf0e82
branch: dudantas/autonomous-program-continuation-v2
pr: 296
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
owned_paths:
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/tasks/active/OTH-20260801-autonomous-program-continuation-v2.md
proven:
  - The standard distinguishes bounded worker sessions from a multi-task owner invocation.
  - The autonomous contract requires terminal task finalization, archival, barrier review, and continuation with the next READY task.
  - The handover routes resolvable short commands into execution rather than returning a prompt.
  - Repository-specific Git, runtime, database, protocol, asset, and production restrictions remain authoritative.
derived:
  - One short programme command can drive long foreground work without treating each checkpoint or completed task as an owner-interaction boundary.
unknown:
  - Required exact-head governance and CI results for PR 296 after front-matter normalization.
conflicts: []
first_failure:
  marker: none
  evidence: no exact-head failure has been classified on the normalized task head
rejected_hypotheses:
  - weaken worker stop conditions to obtain long programme continuation
  - treat checkpoints as mandatory pauses
  - claim hidden background execution after the final response
changed_paths:
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/tasks/active/OTH-20260801-autonomous-program-continuation-v2.md
validation:
  - command: compare main...dudantas/autonomous-program-continuation-v2
    result: PASS
    evidence: four authorized documentation/governance paths only
blockers: []
next_action: verify required exact-head checks for PR 296 and complete the repository merge gate
```
