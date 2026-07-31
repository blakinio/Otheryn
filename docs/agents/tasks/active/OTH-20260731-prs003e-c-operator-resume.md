---
task_id: OTH-20260731-prs003e-c-operator-resume
status: active
project_lane: otheryn-runtime
phase: implement
session_id: chat-github-20260731-prs003e-c-01
execution_mode: chat-github
execution_reason: exact new-file ownership can be implemented through the GitHub connector while the sandbox has no GitHub DNS
branch: dudantas/prs-003e-c-operator-resume
base_branch: main
start_sha: 86742d3b0ff6e31dc24b479179d48a6bd88f9145
issue: "269"
feature_pr: null
created: 2026-07-31
updated: 2026-07-31T09:25:00+02:00
lease_expires_at: 2026-07-31T10:10:00+02:00
owned_paths:
  - docs/agents/tasks/active/OTH-20260731-prs003e-c-operator-resume.md
  - docs/architecture/prs-003e-c-operator-resume.md
  - src/database/database_outage_operator_control.hpp
  - tests/integration/prs_003e/operator_resume_probe.cpp
  - tests/integration/prs_003e/run_operator_resume_probe.sh
  - .github/workflows/prs-003e-c-operator-resume.yml
required_reads:
  - AGENTS.md
  - docs/agents/EXECUTION_PROTOCOL.md
  - docs/agents/PROJECT_LANES.json
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
  - docs/agents/tasks/archive/OTH-20260730-prs003e-b-recovery-evidence.md
  - docs/agents/tasks/active/OTH-20260730-prs-program-coordination.md
search_first:
  - live main head and open pull requests
  - matching PRS-003E-C issues and branches
  - active task ownership
  - src/database/database_outage_state.hpp
  - src/database/database_outage_recovery_evidence.hpp
  - tests/integration/prs_003e/
---

# PRS-003E-C explicit operator resume control

## Current behavior inventory

- Terminal PRS-003E-B supplies bounded accepted recovery evidence without automatic resume.
- `DatabaseOutageStateMachine::operatorResume` already enforces degraded-or-maintenance state plus accepted recovery evidence and rejects stale sequence/time.
- No typed operator request contract currently requires authorization, explicit confirmation and an exact observed outage generation before invoking that method.
- The coordinator record is stale, but its conditional E-C gate is satisfied by live terminal E-B evidence.

## Accepted target contract

Add one database-independent, header-only operator-control API. A request must be authorized, explicitly confirmed and match the exact observed outage state, transition count and last event sequence. Only degraded or maintenance with accepted evidence is eligible. One accepted request invokes the existing state owner once and returns `ResumeGameLifecycle` only after an applied healthy transition. Every rejection is fixed and low-cardinality.

The controlled standalone probe proves status inspection, rejected authorization/confirmation/state/generation/evidence, degraded and maintenance success, later failure invalidation, duplicate/stale/concurrent exact-once behavior and active-interval clearing.

## Explicit non-goals

- no automatic resume;
- no production Lua, HTTP, console or permission-store transport;
- no direct game-lifecycle mutation;
- no reconnect, ping, retry or SQL replay;
- no production database source wiring or recovery-probe changes;
- no schema, credential, migration, deployment, login, handoff, mutation, drain or save change;
- no PRS-004+ work and no RPO/RTO claim.

## Failure-injection plan

- unauthorized request;
- unconfirmed request;
- wrong expected state;
- stale transition count;
- stale last event sequence;
- missing accepted evidence;
- qualifying failure after accepted evidence;
- duplicate event sequence;
- concurrent explicit requests;
- unsupported current state.

## Rollback plan

Revert the feature merge. The slice owns only six new E-C-specific files and adds no persistent state, production transport, schema, credential or deployment surface.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T09:25:00+02:00
phase: implement
session_id: chat-github-20260731-prs003e-c-01
execution_mode: chat-github
execution_reason: exact six-path new-file scope through GitHub connector; sandbox GitHub DNS unavailable
lease_expires_at: 2026-07-31T10:10:00+02:00
head: pending-first-task-record-commit
branch: dudantas/prs-003e-c-operator-resume
pr: null
status: active
project_lane: otheryn-runtime
context_routes:
  - production-resilience
  - database-outage
  - operator-control
  - controlled-runtime
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260731-prs003e-c-operator-resume.md
  - docs/architecture/prs-003e-c-operator-resume.md
  - src/database/database_outage_operator_control.hpp
  - tests/integration/prs_003e/operator_resume_probe.cpp
  - tests/integration/prs_003e/run_operator_resume_probe.sh
  - .github/workflows/prs-003e-c-operator-resume.yml
proven:
  - main 86742d3b0ff6e31dc24b479179d48a6bd88f9145 is the audited task start
  - PRS-003E-B is terminal and issue 262 is closed completed
  - no open pull request and no matching E-C branch existed before claim
  - issue 269 is the unique E-C execution issue
  - all six owned paths are new and E-C-specific
unknown:
  - exact implementation head and focused test result
  - exact feature PR and final check runs
conflicts: []
first_failure: null
rejected_hypotheses:
  - automatic resume after probes
  - direct Game.setGameState from the operator policy API
  - production Lua or HTTP transport in this slice
  - reconnecting or replaying the failed operation
  - modifying existing production source or shared CMake
changed_paths:
  - docs/agents/tasks/active/OTH-20260731-prs003e-c-operator-resume.md
validation:
  - command: live dependency, conflict and ownership preflight
    result: PASS
    evidence: issue 269 and exact six-path new-file ownership on main 86742d3b0ff6e31dc24b479179d48a6bd88f9145
blockers: []
last_completed_step: issue, canonical branch and durable active task record created after live preflight
next_action: implement the header-only operator API, deterministic probe, runner, workflow and architecture contract
```
