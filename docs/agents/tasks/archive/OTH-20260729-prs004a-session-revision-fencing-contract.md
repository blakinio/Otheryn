---
task_id: OTH-20260729-prs004a-session-revision-fencing-contract
status: completed
branch: feat/OTH-20260729-prs004a-session-revision-fencing-contract
base_branch: main
start_sha: 6a6007667dfd82010b0240342180961cd553466f
feature_head: 1571e338bb9f7fc5d7943d4b393c5b34e10ee34a
feature_merge_sha: b00507ec22542b8cf284040bea57bc70941d0964
lifecycle_pr: "215"
lifecycle_head: 552d8fd5369481cda29a060ec29e75b83a922ff5
lifecycle_merge_sha: 87bc63889839960cc9dd7d4502cfb4e25a5eaadb
created: 2026-07-29
updated: 2026-07-29
completed: 2026-07-29
related_issue: "207"
related_pr: "212"
owned_paths:
  - docs/agents/tasks/archive/OTH-20260729-prs004a-session-revision-fencing-contract.md
  - docs/architecture/prs-004-session-revision-fencing-contract.md
  - src/database/session_revision_fence.hpp
  - tests/unit/database/session_revision_fence_test.cpp
  - tests/unit/database/CMakeLists.txt
---

# PRS-004A pure session/revision fencing contract — completed

## Result

PRS-004 Slice A is complete. The repository now contains one database-independent, header-only and mutex-serialized session/revision fencing state object with stable subject identity, monotonic ownership generation, an explicit current writer token, strict persistence revisions, caller-supplied event sequence, immutable snapshots and fixed decision reasons.

Feature PR #212 was squash-merged into `main` as `b00507ec22542b8cf284040bea57bc70941d0964`. Lifecycle PR #215 was squash-merged as `87bc63889839960cc9dd7d4502cfb4e25a5eaadb`. Exact feature head `1571e338bb9f7fc5d7943d4b393c5b34e10ee34a` passed all required checks. Issue #207 is closed as completed.

This package proves only the deterministic process-local contract. It does not establish durable stale-writer safety across process restart, database failover or writers in separate processes.

## Implemented contract

- stable non-zero subject/player identity;
- non-zero monotonic ownership generation that cannot move backward or be reused for another owner;
- one non-zero authorized writer token for the current ownership generation;
- explicit acquire, transfer, release and persistence-revision advance operations;
- explicit `VACANT`, `OWNED` and `RELEASED` states;
- exact current subject, generation and writer-token matching for authorization;
- strict exact-next persistence revision (`current + 1`);
- lower, equal, skipped and exhausted revisions rejected with fixed reasons;
- event sequence zero, stale sequence and duplicate sequence rejected;
- repeated active acquisition handled as a deterministic no-op;
- active ownership replacement requires explicit transfer;
- transfer atomically replaces authority while preserving the latest revision;
- release clears writer authority while preserving generation and revision;
- reacquisition after release requires a strictly newer generation;
- malformed, missing, wrong-subject, stale-generation and wrong-writer context fails closed;
- internally serialized concurrent duplicate acquisition/transfer with at most one effective transition;
- transition count changes only for effective ownership or revision changes;
- no wall-clock lease, sleep, scheduler, background thread, database or protocol dependency.

## Proven fencing invariants

1. Once generation `G+1` owns a subject, generation `G` cannot persist.
2. A lower persistence revision cannot overwrite a newer revision.
3. Equal revision is a rejected fencing duplicate, not another authorized mutation.
4. Duplicate acquisition and duplicate event sequences have fixed deterministic outcomes.
5. Stale and reordered event sequences do not mutate authority or revision.
6. Ownership cannot move backward or be silently replaced through acquisition.
7. A released writer cannot continue writing.
8. Reacquisition cannot reuse the released generation.
9. Channel handoff has one atomic before/after authority transfer with no state authorizing both writers.
10. A delayed completion from the previous owner fails generation or writer-token matching.
11. Zero, missing or malformed fencing context is never authorized.
12. Concurrent identical acquire/transfer operations produce at most one effective transition.
13. Before/after result snapshots remain immutable after later state changes.
14. Transition count changes only on effective state changes.

## Validation

Exact feature head: `1571e338bb9f7fc5d7943d4b393c5b34e10ee34a`.

- CI run `30485079235`: PASS;
- Required run `30485079033`: PASS;
- autofix run `30485078997`: PASS;
- Fast Checks, formatting, analysis, YAML and Lua tests: PASS;
- Linux debug compile, database schema import and full tests: PASS;
- Linux release build and runtime smoke tests: PASS;
- Windows CMake build and runtime smoke test: PASS;
- Windows Solution build: PASS;
- macOS build and runtime smoke test: PASS;
- Docker build, image export and image validation: PASS;
- deterministic ownership, revision, stale-event, malformed-context, snapshot and concurrency tests: PASS;
- changed-path audit: exactly five declared feature paths;
- feature base-drift audit: `behind_by=2`, limited to coordinator task documentation commits; no shared implementation or `tests/unit/database/CMakeLists.txt` conflict;
- PR was mergeable immediately before merge;
- feature PR reviews and unresolved review threads: none;
- feature PR discussion contained only the final exact-head validation evidence comment;
- lifecycle Required run `30486677175`: PASS on exact lifecycle head `552d8fd5369481cda29a060ec29e75b83a922ff5`;
- lifecycle changed-path audit: active record removed and matching archive record added only;
- lifecycle drift audit: `behind_by=0` immediately before lifecycle merge;
- lifecycle PR was mergeable immediately before merge;
- lifecycle PR comments, reviews and unresolved threads: none.

The first superseded feature head failed only the formatting-diff gate. Repository autofix formatted `tests/unit/database/CMakeLists.txt` and `tests/unit/database/session_revision_fence_test.cpp` without changing logic. Replacement exact-head CI, Required and autofix all passed.

## Safety boundaries preserved

- no database schema or migration;
- no SQL conditional-update or compare-and-swap wiring;
- no production player-save integration;
- no account/game login or protocol wiring;
- no live channel-switch or handoff runtime change;
- no runtime database failure classification or outage-event publication change;
- no reconnect, arbitrary SQL replay, retry loop or drain orchestration;
- no time lease or wall-clock expiry;
- no distributed lock service or external consensus;
- no database failover or split-brain claim;
- no PRS-005 idempotency or PRS-006 reconciliation implementation;
- no production credential, deployment, RPO or RTO claim.

## Rollback

Revert feature merge `b00507ec22542b8cf284040bea57bc70941d0964`. The package changes only one isolated pure header, deterministic tests, one minimal unit-test registration entry, architecture documentation and its task record. Revert lifecycle merge `87bc63889839960cc9dd7d4502cfb4e25a5eaadb` only to restore the active/archive record placement.

## Remaining durable/runtime fencing gaps

The following remain separate bounded packages:

- durable schema representation for ownership generation, writer token and persistence revision;
- authoritative database compare-and-swap acquire, transfer, release and revision advance;
- zero-row conditional-update handling as stale-writer rejection;
- production player-save transaction integration;
- channel-handoff source quiesce, durable transfer and destination activation;
- restart behavior that loads or acquires durable authority before enabling writes;
- database failover and split-brain evidence;
- stale-generation, stale-token and stale-revision observability;
- PRS-005 business-operation idempotency;
- PRS-006 SQL/KV reconciliation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T22:03:00+02:00
head: 87bc63889839960cc9dd7d4502cfb4e25a5eaadb
head_scope: terminal lifecycle merge on main; this record-only correction adds known lifecycle merge metadata
status: completed
feature_pr: 212
feature_head: 1571e338bb9f7fc5d7943d4b393c5b34e10ee34a
feature_merge_sha: b00507ec22542b8cf284040bea57bc70941d0964
lifecycle_pr: 215
lifecycle_head: 552d8fd5369481cda29a060ec29e75b83a922ff5
lifecycle_merge_sha: 87bc63889839960cc9dd7d4502cfb4e25a5eaadb
lifecycle_required_run: 30486677175
issue: 207
issue_state: closed_completed
ci_run: 30485079235
required_run: 30485079033
autofix_run: 30485078997
first_failure:
  marker: formatting_diff
  evidence: Superseded head a53c6a6008b5d403ca3772b932f808485c386fbe required repository autofix for the CMake registration and test formatting; autofix commit 1571e338bb9f7fc5d7943d4b393c5b34e10ee34a passed all replacement checks.
unknown: []
blockers: []
next_action: none; no further action is required for this completed package
```
