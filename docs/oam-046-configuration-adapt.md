# OAM-046 configuration target adaptation

## Final disposition

`configuration → ADAPT`

The target retains the existing typed configuration model and accepted composition/Forge deltas. One bounded package-owned invariant required correction: each successful `load()` appended `OTCRFeatures` values to retained member vectors instead of replacing the prior configuration snapshot.

## Exact baselines

- Canary preflight merge: `a1af14078de0450eb138a2f087e71104c03da4ca`
- Otheryn task-start: `e8f683e61427e9967cbc180b837220d4b7487d85`
- reviewed upstream: `opentibiabr/canary@7323503b3dc61ed86bf1f04a611b2d0aec64b35a`
- live legacy Canary at preflight: `930e0a15767b7e5348bb36c679fa5e458a76f184`

Pre-adaptation canonical roots:

| Path | Otheryn | Upstream | Live legacy |
|---|---|---|---|
| `src/config/CMakeLists.txt` | `7a5a5058a22447091dd20e6190911e7f95937a98` | same | same |
| `src/config/configmanager.hpp` | `c3027c491cbc326a3f66d2ed39a19ad7856ca6cf` | same | `8c1e90a7f0f1f894879b54a2de9971ffaeb48e1f` |
| `src/config/config_enums.hpp` | `1676d0ac445e4cd83e91fc57ca405b4a0dccfb55` | same | `4753549d77a2e97a774c90b3d2aed371f06f4e0d` |
| `src/config/configmanager.cpp` | `48c0637ba870cb25d119c16fc21d4134d6bdac15` | `b8d433b6a7f178864f4bd07c131fd78d5bccc832` | `74c8a6f558257aa8bddf57f56116838390dcb25c` |
| `src/config/forge_config_defaults.hpp` | `f5fab42df536304baa8fe034d2a7e8ac245204fd` | absent | `7ebf71e9b6c47f3213aff229002aab9d5d116d60` |
| `config.lua.dist` | `add3df239fb22592b7c63d166f880d0c31098ba2` | `08ffe407ac4dadcfe787a13cc54df9c705565226` | `021dc3e49aadbecead4d5b6d7d3b7ca6243b776e` |

## Isolated defect

`ConfigManager::loadLuaOTCFeatures()` wrote directly to `enabledFeaturesOTC` and `disabledFeaturesOTC` through `push_back`. A second successful load therefore duplicated retained IDs, preserved IDs removed from a later custom table and left a prior disabled snapshot in place when `OTCRFeatures` was subsequently omitted.

A failed `luaL_dofile` already returns before this parser is invoked, so this task does not change failed-load retention behavior.

## Bounded adaptation

The parser now builds local enabled/disabled vectors and moves both into the retained members only after the current Lua snapshot has been parsed. The fallback snapshot is exactly enabled `{101, 102, 103, 118}` with an empty disabled list. No key enum, default distribution, public getter, controlled feature behavior or reload orchestration was redesigned.

Adapted source blob:

- `src/config/configmanager.cpp`: `18a52bb1095576cc2147bf8581d1007fcef90215`

Focused contract roots:

- `tests/unit/config/oam_046_configuration_test.cpp`: `18fc3a2d7b59f7b1dc3ce7e2218983af8ee2a79d`
- `tests/unit/config/CMakeLists.txt`: `0d84e69040ef3e4d1f58612062f004a76bbb0336`
- `tests/unit/CMakeLists.txt`: `aaa940ff32c124b640e6e62acb91d652913c3012`

The fixture proves:

1. a first custom enabled/disabled snapshot loads exactly;
2. a second successful custom load replaces rather than appends or preserves stale IDs;
3. omission of `OTCRFeatures` replaces both lists with the bounded fallback snapshot;
4. repeating the fallback load remains idempotent.

## Explicit boundaries

OAM-046 does not claim:

- exhaustive one-to-one correspondence for every enum, Lua identifier or default across target/upstream/legacy;
- concurrent reload/read safety, atomic replacement of the complete configuration map or lock-free correctness;
- production configuration correctness, secret handling, environment-variable policy or deployment parity;
- correctness of gameplay, protocol, transport, login, economy or client behavior controlled by configuration values;
- maintained-client interpretation or physical-client effects for every OTCR feature ID;
- full rollback/transaction semantics when later parsing or deferred callbacks fail;
- full Oteryn production readiness.

## Unknowns retained

- Complete cache/read synchronization during concurrent reload remains unproven.
- Exhaustive key/default drift remains unclassified.
- Environment-specific and production-secret behavior remains untested.
- Physical-client behavior for the configured feature IDs remains unproven.

`next_action`: Run exact-head Otheryn Autofix, CI and Required gates for the focused adaptation, audit all discussions and target-main drift, then squash-merge with the expected head.
