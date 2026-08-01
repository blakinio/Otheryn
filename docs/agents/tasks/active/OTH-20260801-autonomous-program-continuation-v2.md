# OTH-20260801 — Autonomous program continuation v2

## Objective

Make one short owner invocation authorize a long, low-noise autonomous programme run that checkpoints safely, completes and archives terminal tasks, crosses barriers, and continues with the next ready work until a real stop condition is reached.

## Scope

Documentation and agent-governance contracts only.

Owned paths:

- `docs/agents/PROMPTING_STANDARD.md`
- `docs/agents/PROMPTING_HANDOVER.md`
- `docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md`
- this task record

No runtime, production, database, protocol, asset, upstream, or deployment mutation is authorized.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-01T21:19:00Z
head: f386c07f934583e63eeab149ce0582e2fa7da1fc
branch: dudantas/autonomous-program-continuation-v2
pr: 296
status: validating
phase: validate
session_id: chat-20260801-autonomous-v2
session_role: coordinator
execution_mode: chat
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/tasks/active/OTH-20260801-autonomous-program-continuation-v2.md
proven:
  - The standard now distinguishes bounded worker sessions from a multi-task owner invocation.
  - The new contract requires terminal task finalization, archival, barrier review, and continuation with the next READY task.
  - The handover routes resolvable short commands into execution rather than returning a prompt.
  - Repository-specific Git, runtime, database, protocol, asset, and production restrictions remain authoritative.
derived:
  - One short programme command can now drive long foreground work without treating each checkpoint or completed task as an owner-interaction boundary.
unknown:
  - Required exact-head CI result for PR 296.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses: []
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
