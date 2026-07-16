# OAM-005A — Login session primitive

This bounded target adaptation adds the reusable `LoginSessionManager` authentication primitive required by the OAM-005 account-authentication disposition.

## Scope

- 256-bit CSPRNG-generated, hex-encoded tokens;
- only SHA-256 token hashes retained in memory;
- single-use redemption;
- account, allowed-character-set and protocol-profile binding;
- TTL and bounded active-token capacity;
- constant-time hash comparison;
- focused unit coverage including replay, expiry, binding, eviction, uniqueness and concurrent redemption.

## Explicit boundary

This slice does not wire the primitive into `ProtocolLogin`, `ProtocolGame`, or `IOLoginData`. Wire/session/client compatibility remains OAM-006 work. The existing password and DB-backed `account_sessions` behavior is unchanged.

## Provenance

- target task-start: `67212530b03c10175da2c0d9eabcee8991a05924`;
- legacy evidence: `blakinio/canary` PR #77, merged as `3c5268fe86fd9785e3feea192d70c8bd3d51ef87`;
- OAM-005 tracking: Otheryn issues #15 and #17.

## Known gap

The Windows Visual Studio project file is not part of this bounded CMake-driven target slice. Repository CI is authoritative for the supported target build gate; any separate Visual Studio project synchronization remains a build-tooling concern rather than authentication semantics.
