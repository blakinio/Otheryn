# OAM-054 Login Protocol adaptation

## Disposition

```text
login-protocol → ADAPT
```

Otheryn already owns account authentication integration, explicit current/11.00/8.60 login layouts, secure single-use login-session tokens and protocol-session handoff. OAM-054 adapts only the login response wire into a target-owned, deterministic contract corresponding to the maintained-client parser.

## Pinned revisions

- Canary preflight merge: `d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61`;
- Otheryn task-start main: `9703da845384423ad85883216bf8853642c21bcd`;
- Canary reconciliation baseline: `9d395a5563531dfc3d83f4a24361237137715000`;
- upstream Canary: `7644bcbcbbad4a09e52a5707ed531e4dd21d8a79`;
- maintained OTClient: `99ad5de5a19179f21e2e21e961c1ef121a30d08e`.

Relevant donors:

- modern-client login rejection repair: `d2e02a3d533bfdfdedc3a81a8f4e4801bc828f22`;
- secure opaque session-key handoff: `9cafe7e945391a6f170f5b96bf68713d91d758be`.

## Target gap

The maintained client decodes modern opcode `0x64` as world list, character list, account status `u8`, subscription status `u8` and premium expiry `u32`. Legacy protocols decode the legacy character list followed by premium days `u16`.

At task start Otheryn wrote premium remaining days into the modern account-status byte, followed by a premium boolean and premium-last-day timestamp. The second and third values resembled subscription/expiry semantics, but the first field had no explicit status contract and no direct server/client regression existed.

## Adapted behavior

The target now contains a small login-wire serializer owning only:

- opcode `0x28` session-key response framing;
- current world/character list response framing;
- explicit modern account status/subscription/expiry tail;
- legacy character list and premium-days tail;
- bounded `u8` character count shared by secure-token authorization, serialized payload and session hints;
- deterministic field-order tests based on the maintained-client parser.

`ProtocolLogin` retains request parsing, profile/layout selection, RSA/XTEA setup, account loading/authentication, token issuance, session-hint registration, error handling, send and disconnect lifecycle.

## Deterministic regressions

Six target tests decode exact response order and consume each message to the end:

- session-key opcode and token string;
- modern premium response;
- modern free response;
- legacy response with premium days;
- modern character count capped at 255;
- legacy character count capped at 255.

Existing OAM-044 profile and OAM-045 session-handoff regressions remain in the same full CTest suite.

## Implementation validation

Implementation head `c6fe5d8a2f48e6c8425c3db39ff2372a7cde3c3f` passed:

- repository CI `30245438536`;
- `Required` `30245438107`;
- autofix `30245438145` with no follow-up commit;
- Fast Checks and Lua;
- Linux debug with full tests and schema import;
- Linux release;
- Docker image;
- macOS build and runtime smoke;
- Windows builds.

## Evidence boundary

The green result proves exact target serialization and parser correspondence for registered fixtures. It does not prove password security, arbitrary-account authorization, all protocol versions, game-world authentication, reconnect races, client UI behavior, sustained load or production safety.

## Delivery evidence

Implementation is validated. Exact-final checkpoint gates, merge and lifecycle archive remain pending.
