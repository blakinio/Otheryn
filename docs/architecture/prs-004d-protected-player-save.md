# PRS-004D protected player-save integration

## Authority and runtime ownership

MariaDB `player_writer_fence` remains the durable authority. An initial world login loads the released authority row, generates a CSPRNG token and performs one strictly newer acquire before Player placement. `SaveManager` binds the resulting complete context to the exact live Player object. A row still owned by another token fails login closed; this slice does not add crash takeover.

Channel reconnect reuses the existing Player and authority context unchanged. Source quiesce and durable transfer to a newer generation/token remain PRS-004E.

## Protected save transaction

`IOLoginData::savePlayer` accepts the exact subject, ownership generation, writer token and current revision. `PlayerWriterFencedSaveTransaction` opens one `DBTransaction`, executes the existing selected SQL-backed player save callback, then performs the exact-next revision CAS on the same recursively locked MariaDB connection.

- callback failure rolls back all earlier player mutations;
- malformed context fails before the callback;
- zero affected rows is a stale conflict and rolls back all player mutations;
- commit failure leaves caller context unchanged;
- successful commit updates caller context to exactly the next revision;
- post-commit KV staging remains a separate persistence domain and never changes the SQL commit decision.

No stale, failed or unknown-outcome operation is retried or replayed automatically.

## Release boundary

A final or offline save first completes the protected save and revision commit. It then performs one exact release CAS. Release failure remains explicit, retains the current process context and is not retried. Initial placement failure performs the same single exact release attempt.

## Boundaries

This slice does not add channel-handoff transfer, Redis authority, automatic crash takeover, reconnect/replay, broad economy-write fencing, production credentials/data access, deployment, PRS-005+ behavior or RPO/RTO claims.
