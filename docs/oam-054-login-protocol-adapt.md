# OAM-054 Login Protocol adaptation

## Disposition

```text
login-protocol → ADAPT
```

Otheryn retained account authentication integration, explicit current/11.00/8.60 request layouts, secure single-use login-session tokens and protocol-session handoff. OAM-054 adapted only the account-login response wire into a target-owned deterministic contract corresponding to the maintained-client parser.

## Pinned revisions

- Canary preflight merge: `d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61`;
- Otheryn task-start main: `9703da845384423ad85883216bf8853642c21bcd`;
- final synchronized main: `4ad8c0f2ed1c6bd60da9b747b8ff180ced60b593`;
- exact target feature head: `f6db2136248b39ccd7aa57178a1c63c788b9bcec`;
- target feature merge: `e077c51fe948652a4849e15f6c518059f4370717`;
- upstream Canary: `7644bcbcbbad4a09e52a5707ed531e4dd21d8a79`;
- maintained OTClient: `99ad5de5a19179f21e2e21e961c1ef121a30d08e`.

Relevant donors:

- modern-client login rejection repair: `d2e02a3d533bfdfdedc3a81a8f4e4801bc828f22`;
- secure opaque session-key handoff: `9cafe7e945391a6f170f5b96bf68713d91d758be`.

## Target gap and adapted behavior

The maintained client decodes modern opcode `0x64` as world list, character list, account status `u8`, subscription status `u8` and premium expiry `u32`. Legacy protocols decode a legacy character list followed by premium days `u16`.

At task start Otheryn had no explicit tested account-status contract corresponding to that parser. The target now contains a small serializer owning only:

- opcode `0x28` session-key response framing;
- modern world/character list framing;
- explicit modern account status/subscription/expiry tail;
- legacy character list and premium-days tail;
- one capped `u8` character snapshot shared by secure-token authorization, payload records and session hints;
- deterministic maintained-client-order decoding tests.

`ProtocolLogin` continues to own request parsing, profile/layout selection, RSA/XTEA setup, account loading/authentication, token issuance, session-hint registration, error handling, send and disconnect lifecycle.

## Deterministic regressions

Six tests consume each response to the exact message end:

- session-key opcode and token;
- modern premium response;
- modern free response;
- legacy response with premium days;
- modern count capped at 255;
- legacy count capped at 255.

Existing OAM-044 profile and OAM-045 session-handoff regressions remain in the same full CTest suite.

## Exact-final validation

Exact atomically synchronized head `f6db2136248b39ccd7aa57178a1c63c788b9bcec` passed:

- repository CI `30250360096`;
- `Required` `30250359982`;
- autofix `30250359933` without a follow-up commit;
- Fast Checks and Lua;
- Linux debug with runtime smoke, schema import and full CTest;
- Linux release;
- Docker image;
- macOS build/runtime smoke;
- Windows CMake/runtime smoke and Solution build.

PR #165 changed exactly six intended paths, had `behind_by=0`, no comments, reviews or review threads, and squash-merged with expected-head protection as `e077c51fe948652a4849e15f6c518059f4370717`.

## Evidence boundary

The green result proves exact target serialization and parser correspondence for registered fixtures. It does not prove password security, arbitrary-account authorization, every protocol version, game-world authentication, reconnect races, client UI behavior, sustained load or production safety.

## Lifecycle

The durable completed task is `docs/agents/tasks/archive/OTH-20260727-oam054-login-protocol-adapt.md`. A separate docs-only lifecycle PR records the feature evidence before Canary governance and final programme reconciliation.
