---
task_id: OTH-20260729-prs-parallel-integration-coordination
status: active
branch: dudantas/prs-parallel-integration-checkpoint-1
base_branch: main
start_sha: 6a6007667dfd82010b0240342180961cd553466f
created: 2026-07-29
updated: 2026-07-29
related_issue: "205"
related_pr: "211"
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
  - tests/unit/game/CMakeLists.txt
  - vcproj/canary.vcxproj
---

# Parallel PRS resilience integration coordination

## Goal

Coordinate PRS-003B, PRS-003C-A and PRS-004A as independently owned packages, prevent implementation and shared-registration conflicts, enforce exact-head merge gates and keep every issue/task/PR/archive lifecycle terminal before selecting the next package.

This task owns coordination state only. It does not authorize broad runtime, schema, persistence or deployment implementation.

## Audited baseline

- exact task-start `main`: `6a6007667dfd82010b0240342180961cd553466f`;
- PRS-003A feature PR `#202` exact head `45ed0385be9e1626be42c60d396069d04ca36585` merged as `bc1aa5a8a9c0094f555a8b73b8a32679797bc20c`;
- PRS-003A exact-head CI `30477984422`, Required `30477983720` and autofix `30477983735` passed;
- PRS-003A issue `#201` is closed as completed;
- lifecycle PR `#203` merged as `36d514773710075315b5ebb99f85865e34eea9e6`;
- terminal archive finalizer PR `#204` merged as `6a6007667dfd82010b0240342180961cd553466f`;
- coordination PR `#209` exact head `b78286053df9b977f03c712f02f52d8de86efc66` passed Required `30484314153` and squash-merged as current `main` `beea2231a0ea66fd783260a3fdbfb71afec5d566`;
- no PRS-003A active task or open PR remains;
- parent production-resilience tracker `#116` remains open;
- package issues `#206`, `#207` and `#208` reserve the three parallel scopes;
- duplicate PRS-003B issue `#210` was closed as duplicate of `#208` before implementation ownership was declared;
- no package feature PR or exact owned-path declaration is published yet.

## Package status

| package | issue | task ID | branch | logical owner | exact owned paths | dependency status | PR | exact head | CI | merge | archive | blockers |
|---|---:|---|---|---|---|---|---:|---|---|---|---|---|
| PRS-003B | #208 | awaiting task declaration | awaiting declaration | Agent PRS-003B | awaiting exact declaration | PRS-003A merged; primary runtime foundation | — | — | not run | not merged | not started | exact task/branch/paths not yet published |
| PRS-003C-A | #206 | awaiting task declaration | awaiting declaration | Agent PRS-003C-A | awaiting exact declaration | PRS-003A merged; pure policy may proceed independently | — | — | not run | not merged | not started | exact task/branch/paths not yet published |
| PRS-004A | #207 | OTH-20260729-prs004a-session-revision-fencing-contract | awaiting declaration | Agent PRS-004A | awaiting exact declaration | pure model; independent of PRS-003 runtime wiring | — | — | not run | not merged | not started | exact branch/paths not yet published |

## Ownership and conflict matrix

Every executing agent must publish one active task record with exact `owned_paths` before implementation. The coordinator rejects undeclared or overlapping implementation paths.

| pair | expected overlap risk | coordinator rule |
|---|---|---|
| PRS-003B / PRS-003C-A | database unit-test registration and primary PRS-003 contract | implementations remain separate; serialize any shared registration; C-A must not wire protocols or publish runtime events |
| PRS-003B / PRS-004A | shared test/build registration only | 004A must not modify Database runtime, schema or persistence wiring; minimal registration overlap is rebased after the first merge |
| PRS-003C-A / PRS-004A | shared test/build registration only | preserve separate policy and fencing models; no combined abstraction or runtime adapter |

Coordinator-controlled or serialized paths:

- shared unit-test `CMakeLists.txt` files;
- Visual Studio project files;
- central architecture indexes and module catalogs;
- repository task indexes;
- `docs/architecture/prs-003-database-outage-state-machine-contract.md`.

No two open feature PRs may make broad edits to one shared path. When a minimal registration overlap is unavoidable, merge the package with the smallest dependency surface first, rebase the other package on updated `main`, resolve only the registration entry and rerun exact-head CI.

## Dependency and next-work rules

- PRS-003B is the runtime event-publication dependency.
- PRS-003C-A may merge independently because it is pure policy.
- PRS-004A may merge independently because it is a pure fencing model.
- live PRS-003C protocol wiring waits for merged PRS-003B and PRS-003C-A.
- PRS-003D mutation admission and bounded draining waits for required Slice B and admission foundations.
- PRS-003E controlled failure injection waits for a real runtime event-publication seam.
- PRS-004 durable/runtime persistence integration remains separate from PRS-004A.

After all three packages are terminal, fresh-audit actual dependencies and select exactly one smallest unblocked next package. Do not start all remaining candidates simultaneously.

## Merge and lifecycle gate

For every package:

1. verify issue, active task scope and PR scope match;
2. inspect all changed filenames and every relevant patch;
3. reject prohibited runtime/schema/deployment changes;
4. verify exact-final-head CI and all repository-required checks;
5. verify reviews, comments and unresolved threads;
6. compare the exact head with current `main` and refresh after shared-path drift;
7. merge with expected-head protection using the repository-standard method;
8. verify merge SHA and issue closure;
9. verify active task removal, complete archive record and any required finalizer merge;
10. verify no stale branch or duplicate PR remains.

Code completion alone is not terminal.

## Safety boundaries

Reject any package that introduces outside explicit scope:

- automatic reconnect or arbitrary SQL replay;
- unbounded retry or draining behavior;
- schema or migration changes;
- production credentials, production database mutation or deployment changes;
- silent staff bypass;
- allow-by-default unclassified operations;
- acceptance of a stale writer when fencing context is absent or malformed;
- unsupported RPO/RTO claims.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T21:31:00+02:00
head: 75f7d8c5b4bbead28e5564d22e47d410ac5e892f
head_scope: checkpoint content head before recording PR 211 and duplicate issue 210 disposition
branch: dudantas/prs-parallel-integration-checkpoint-1
pr: 211
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
  - PRS-003A feature, issue, archive and finalizer lifecycle are terminal.
  - Issue 205 owns integration coordination only.
  - Coordination PR 209 exact head b78286053df9b977f03c712f02f52d8de86efc66 passed Required 30484314153 and merged as beea2231a0ea66fd783260a3fdbfb71afec5d566.
  - Issues 206, 207 and 208 reserve PRS-003C-A, PRS-004A and PRS-003B respectively.
  - Duplicate PRS-003B issue 210 is closed as duplicate of 208 and owns no implementation.
  - Shared registration and primary PRS-003 architecture paths are serialized by the coordinator.
  - No package feature PR or exact owned-path declaration is currently published.
derived:
  - The three packages can proceed in parallel only after each publishes exact owned paths and preserves the declared pure/runtime boundaries.
unknown:
  - Package task paths, branches, exact owned paths, PRs and implementation heads.
  - Exact-head Required result for PR 211.
conflicts:
  - duplicate issue 210 was resolved by keeping issue 208 as the definitive PRS-003B owner
first_failure: null
rejected_hypotheses:
  - combine all three packages into one PR
  - start live protocol wiring before Slice B and pure admission policy merge
  - treat code-written state as lifecycle completion
  - allow overlapping broad edits to shared build or architecture files
changed_paths:
  - docs/agents/tasks/active/OTH-20260729-prs-parallel-integration-coordination.md
validation:
  - command: fresh repository, main, PR, issue and PRS-003A lifecycle audit
    result: PASS
    evidence: Exact main and terminal PRS-003A issue/feature/archive/finalizer evidence verified through live GitHub state.
  - command: coordination PR 209 exact-head scope, discussion, freshness and Required audit
    result: PASS
    evidence: One task-record path, no reviews/comments/threads, behind_by zero, and Required 30484314153 succeeded on exact head b78286053df9b977f03c712f02f52d8de86efc66.
  - command: coordination PR 209 squash merge
    result: PASS
    evidence: Expected-head protected merge created beea2231a0ea66fd783260a3fdbfb71afec5d566.
  - command: duplicate ownership audit
    result: PASS
    evidence: Issue 210 is closed as duplicate; issue 208 remains the sole PRS-003B scope owner.
  - command: PR 211 exact-head Required
    result: NOT_RUN
    evidence: This metadata update creates the replacement PR head.
blockers:
  - All three executing agents must publish exact task records, branches and owned_paths before coordinator implementation review can begin.
next_action: Inspect each newly published active task record and branch, record exact owned paths in the conflict matrix, and stop any overlap before implementation review.
```
