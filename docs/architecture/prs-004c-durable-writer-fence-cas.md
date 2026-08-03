# PRS-004C durable writer-fence CAS

## Authority

MariaDB table `player_writer_fence` is the durable authority. Redis and process memory may cache observations later, but they do not authorize a write.

Each operation runs inside one `DBTransaction` on the shared recursive database lock. The repository issues exactly one conditional `UPDATE`, then reads `ROW_COUNT()` before commit while no other statement can interleave on that connection.

Typed outcomes are:

- `Applied` — exactly one authority row changed and commit succeeded;
- `StaleConflict` — the conditional update changed zero rows and commit succeeded;
- `MalformedContext` — validation rejected before SQL;
- `DatabaseFailure` — begin, query, row-count read or commit failed, or more than one row was affected.

No failed or unknown-outcome operation is retried or replayed.

## Released-state compatibility correction

The accepted PRS-004A model retains ownership generation and persistence revision after release while clearing the writer token. Database version 60 changes only the check constraint:

- initial vacant: generation `0`, token `NULL`, revision `0`;
- owned: generation `> 0`, token non-null;
- released: generation `> 0`, token `NULL`, prior revision retained.

This preserves monotonic generation history. Reacquisition must provide a generation strictly greater than the stored generation and the exact stored revision.

## CAS operations

### Acquire

Requires non-zero subject/generation/token. Applies only when the row is unowned, requested generation is strictly newer than stored generation and requested revision equals stored revision.

### Transfer

Requires exact current subject/generation/token/revision, a strictly newer generation and a different non-zero token. Revision is retained.

### Release

Requires the exact current tuple. It clears only the token; generation and revision remain durable.

### Advance revision

Requires exact current tuple and `next_revision == current_revision + 1`. The update and revision advance are one authoritative statement.

## Boundaries

No player-save integration, channel handoff, Redis authority, reconnect, ping, retry, SQL replay, production credential/data access, deployment or RPO/RTO claim is included. Those remain later gated slices.
