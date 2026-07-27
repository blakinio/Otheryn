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

The maintained client decodes modern opcode `0x64` as:

1. world list;
2. character list;
3. account status `u8`;
4. subscription status `u8`;
5. premium expiry `u32`.

For legacy protocols it decodes the legacy character list followed by premium days `u16`.

At task start Otheryn wrote premium remaining days into the modern account-status byte, followed by a premium boolean and premium-last-day timestamp. Although the second and third values matched the intended subscription/expiry convention, the first field had no explicit status semantics and no direct server/client regression existed.

## Adapted boundary

The package will introduce a small login-wire serializer that owns only:

- opcode `0x28` session-key response framing;
- current world/character list response framing;
- explicit modern account status/subscription/expiry tail;
- legacy character list and premium-days tail;
- deterministic field-order tests based on the maintained-client parser.

`ProtocolLogin` retains request parsing, profile/layout selection, RSA/XTEA setup, account loading/authentication, token issuance, session-hint registration, error handling, send and disconnect lifecycle.

## Evidence boundary

A green result will prove exact target serialization and parser correspondence for registered fixtures. It will not prove password security, arbitrary-account authorization, all protocol versions, game-world authentication, reconnect races, client UI behavior, sustained load or production safety.

## Delivery evidence

Pending target implementation, exact-final validation, feature merge and lifecycle archive.
