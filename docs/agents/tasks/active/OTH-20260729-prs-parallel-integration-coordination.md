---
task_id: OTH-20260729-prs-parallel-integration-coordination
status: active
branch: dudantas/prs-parallel-integration-checkpoint-2
base_branch: main
start_sha: 6a6007667dfd82010b0240342180961cd553466f
created: 2026-07-29
updated: 2026-07-29
related_issue: "205"
related_pr: pending
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs-parallel-integration-coordination.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/PRODUCTION_RESILIENCE_IMPLEMENTATION.md
  - docs/architecture/production-resilience-and-recovery.md
  - docs/architecture/prs-003-database-outage-state-machine-contract.md
search_first:
  - docs/agents/tasks/active/
  - docs/agents/tasks/archive/
  - src/database/database_outage_state.hpp
  - tests/unit/database/CMakeLists.txt
  - tests/unit/server/CMakeLists.txt
  - vcproj/canary.vcxproj
---

# Parallel PRS resilience integration coordination

## Goal

Coordinate PRS-003B, PRS-003C-A and PRS-004A as independently owned packages, prevent implementation and shared-registration conflicts, enforce exact-head merge gates and complete every issue/task/PR/archive/finalizer lifecycle before selecting the next package.

This task owns coordination state only. It does not authorize broad runtime, schema, persistence or deployment implementation.

## Current authoritative baseline

- current `main`: `1ec8c43c448f99e72f0319784b041bdab9e2231f`;
- PRS-003A remains terminal;
- PRS-004A feature PR `#212` exact head `1571e338bb9f7fc5d7943d4b393c5b34e10ee34a` merged as `b00507ec22542b8cf284040bea57bc70941d0964`;
- PRS-004A lifecycle PR `#215` merged as `87bc63889839960cc9dd7d4502cfb4e25a5eaadb` and finalizer PR `#216` merged as `a263e7c7370b39bbf65557ccb570cf29ed775e74`;
- PRS-003C-A feature PR `#213` exact head `d1a36eada901dacb4634f6b417ff7535e046d5b2` passed CI `30487806313`, Required `30487806104` and autofix `30487806142`, then merged as `3790aa4a0d5d43bbcc09f0e8725849fbcfe7d4fb`;
- PRS-003C-A lifecycle PR `#217` exact head `c7075607fa7eaefc6b356825116beea87736e146` passed Required `30489134990` and merged as current `main`;
- issue `#206` is closed completed; its archive finalizer metadata remains pending;
- PRS-003B issue `#208` owns feature PR `#214`; duplicate issue `#210` remains closed as duplicate.

## Package status

| package | issue | task ID | branch | owned paths | dependency status | PR | exact head | CI | merge | archive | blockers |
|---|---:|---|---|---|---|---:|---|---|---|---|---|
| PRS-003B | #208 | OTH-20260729-prs003b-database-failure-classification | dudantas/prs-003b-database-failure-classification | task; primary PRS-003 contract; `database.cpp`; classifier header; database test; database CMake | PRS-003A merged; runtime foundation | #214 | `f48ecc0b7dba6001c8d245972abe8faec34569b4` | autofix passed; CI/Required running | not merged | not started | exact-head CI/Required incomplete; branch behind lifecycle-only main commits |
| PRS-003C-A | #206 | OTH-20260729-prs003c-login-handoff-admission-policy | dudantas/prs-003c-login-handoff-admission-policy | five declared pure-policy paths | pure policy complete | #213 | `d1a36eada901dacb4634f6b417ff7535e046d5b2` | all exact-head gates passed | `3790aa4a...` | #217 merged; finalizer pending | terminal archive metadata not yet recorded |
| PRS-004A | #207 | OTH-20260729-prs004a-session-revision-fencing-contract | feat/OTH-20260729-prs004a-session-revision-fencing-contract | five declared pure-model paths | independent pure model complete | #212 | `1571e338bb9f7fc5d7943d4b393c5b34e10ee34a` | CI/Required/autofix passed | `b00507ec...` | #215 and #216 merged | none; terminal |

## Ownership and conflict matrix

| pair | observed overlap | disposition |
|---|---|---|
| PRS-003B / PRS-003C-A | no common feature path; separate database/server test registration files | no implementation conflict |
| PRS-003B / PRS-004A | `tests/unit/database/CMakeLists.txt` | PRS-004A merged first; PRS-003B refreshed onto final PRS-004A main and preserves its registration |
| PRS-003C-A / PRS-004A | no common feature path | no implementation conflict |

Coordinator-controlled or serialized paths remain shared unit-test CMake files, Visual Studio registration, central architecture indexes/catalogs, task indexes and the primary PRS-003 architecture contract.

PRS-003B currently differs from `main` only because PRS-003C-A feature/lifecycle commits landed after its final refresh. Those commits do not touch any PRS-003B changed path. A new refresh is required only if a shared or owned path changes before merge, or repository governance requires zero-behind final heads.

## Dependency state

- PRS-003B remains the runtime event-publication dependency.
- PRS-003C-A pure admission policy is feature-complete and archived, but not terminal until its archive finalizer records lifecycle metadata.
- PRS-004A is terminal.
- live PRS-003C-B protocol wiring remains blocked until PRS-003B is merged and terminal and PRS-003C-A is terminal.
- PRS-003D remains blocked on the required Slice B and admission foundations.
- PRS-003E remains blocked on the merged runtime event-publication seam.
- PRS-004 durable persistence integration remains separate from PRS-004A.

## Safety boundaries

No reviewed package introduced automatic reconnect, arbitrary SQL replay, unbounded retry/draining, schema or migration changes, production credentials/data/deployment changes, silent staff bypass, allow-by-default unknown operations, missing-context stale-writer acceptance or unsupported RPO/RTO claims.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T22:40:00+02:00
head: 1ec8c43c448f99e72f0319784b041bdab9e2231f
head_scope: current main after PRS-003C-A lifecycle merge; before this coordinator checkpoint update
branch: dudantas/prs-parallel-integration-checkpoint-2
pr: pending
status: active
context_routes:
  - production-resilience
  - database
  - authentication
  - fencing
  - testing
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260729-prs-parallel-integration-coordination.md
proven:
  - PRS-004A feature, issue, lifecycle and finalizer are terminal.
  - PRS-003C-A feature PR 213 passed exact-head CI, Required and autofix and merged as 3790aa4a0d5d43bbcc09f0e8725849fbcfe7d4fb.
  - PRS-003C-A issue 206 is closed completed and lifecycle PR 217 passed Required and merged as 1ec8c43c448f99e72f0319784b041bdab9e2231f.
  - PRS-003B PR 214 owns exactly six declared paths and preserves caller-visible false/nullptr, disabled reconnect and no replay.
  - PRS-003B has no changed-path conflict with merged PRS-003C-A.
  - PRS-003B exact head f48ecc0b7dba6001c8d245972abe8faec34569b4 has passing autofix; CI and Required remain active.
derived:
  - PRS-003B may be merged without a source conflict after exact-head gates complete, provided no shared/owned path changes and repository freshness policy permits the lifecycle-only behind state.
unknown:
  - PRS-003B terminal CI/Required result and merge SHA.
  - PRS-003C-A archive finalizer PR/head/merge/Required metadata.
conflicts:
  - duplicate issue 210 resolved by retaining issue 208 as sole PRS-003B owner
first_failure: null
rejected_hypotheses:
  - merge PRS-003B before exact-head CI and Required complete
  - combine live protocol wiring into PRS-003B or PRS-003C-A lifecycle work
  - treat PRS-003C-A as terminal before archive finalizer metadata is merged
  - refresh PRS-003B by combining unrelated feature changes
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs-parallel-integration-coordination.md
validation:
  - command: PRS-004A terminal lifecycle audit
    result: PASS
    evidence: PRs 212, 215 and 216 merged; issue 207 closed; archive finalized.
  - command: PRS-003C-A feature and lifecycle audit
    result: PASS
    evidence: PR 213 exact-head gates passed and merged; issue 206 closed; PR 217 Required passed and lifecycle merge completed.
  - command: PRS-003B ownership, full patch, discussion and freshness audit
    result: PASS
    evidence: Six declared paths only; no reviews/comments/threads; no prohibited scope; no overlap with PRS-003C-A paths; exact-head CI/Required still running.
  - command: coordinator checkpoint exact-head Required
    result: NOT_RUN
    evidence: This checkpoint update creates the candidate head.
blockers:
  - PRS-003B exact-head CI and Required are not terminal.
  - PRS-003C-A archive finalizer metadata is not yet merged.
next_action: Finalize the PRS-003C-A archive metadata, then re-audit PRS-003B exact-head CI, discussions and main drift and merge only if every gate remains satisfied.
```
