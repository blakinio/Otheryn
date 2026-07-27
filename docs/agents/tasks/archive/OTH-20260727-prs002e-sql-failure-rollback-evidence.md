---
task_id: OTH-20260727-prs002e-sql-failure-rollback-evidence
status: completed
branch: dudantas/prs-002e-sql-failure-rollback-evidence
base_branch: main
created: 2026-07-27
updated: 2026-07-27
related_issue: "168"
related_pr: "169"
---

# PRS-002E SQL failure rollback evidence

## Result

Completed and merged.

- Feature head: `e9cdf4a7ef041ae8154db9aaad8ec49feeb9bccf`
- Feature merge: `6bcf66e388db96a9a605db550643eeb12f8092b4`
- Exact-head CI: `30248139970` — PASS
- Exact-head Required: `30248139846` — PASS
- Exact-head autofix.ci: `30248139838` — PASS
- Issue `#168` closed as completed.

## Proven

- A real invalid MariaDB statement after an earlier valid InnoDB update causes `DBTransaction::executeWithinTransaction` to fail and roll back the earlier update.
- Routing that failed transaction through the merged checkpoint-attempt boundary accepts failure acknowledgement only for the captured generation.
- Failed SQL persistence leaves the exact-owner checkpoint dirty, releases the in-flight generation and requests no implicit follow-up.
- A later explicit generation can commit a valid transaction, acknowledge success and clear dirty state.
- The test owns and removes one dedicated integration probe table and does not change production schema or runtime behavior.
- Linux debug imported the MariaDB schema and completed the full test suite successfully; all applicable platform, formatting, Lua and smoke gates passed.

## Boundaries preserved

- No production/shared database access, credentials, schema migration or deployment change.
- No modification of `IOLoginData::savePlayer`, `SaveManager`, `Database` or `DBTransaction` production behavior.
- No retry timer, backoff, queue policy, metrics backend or RPO claim.
- This is transaction-boundary evidence, not a complete end-to-end `IOLoginData::savePlayer()` failure drill.
- KV post-commit failure, commit-before-ack crash proof and queue-overload behavior remain unproven.

## Next package

Continue only through a separately scoped PRS-002 Slice D issue for one remaining evidence gap. Do not combine KV post-commit behavior, process-crash proof and queue overload in one package.
