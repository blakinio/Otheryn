# OAM-025 chat communication adaptation

## Disposition

```text
chat-communication → ADAPT
```

## Immutable task-start baselines

- legacy / governance Canary: `9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5`
- Otheryn: `86a598426f65e51ff2864ccd1d0a1dbf818b526c`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `87124861eb0faa9134bdda062c881df70f17d495`

## Canonical boundary

Canonical ownership is limited to:

```text
src/creatures/interactions/chat.cpp
src/creatures/interactions/chat.hpp
data/chatchannels/**
```

The canonical registry declares only completed `character-lifecycle` as a dependency. Guild membership lifecycle, party membership lifecycle, wire packet framing/opcodes, NPC conversation state, generic moderation policy, message privacy/delivery guarantees and unrelated physical-client E2E remain outside OAM-025.

## Evidence-driven classification

At task start, `chat.cpp`, `chat.hpp`, `chatchannels.xml` and every configured chat-channel Lua script were blob-identical across legacy, target and fresh upstream. Blob identity was treated only as supporting evidence.

Semantic and history review identified one bounded privilege-domain defect in `data/chatchannels/scripts/help.lua`. Upstream commit `e17d77ac11635c7ddb53c36f6347d88bd3d35223` intentionally migrated chat authorization and message-color decisions from account type to player group because account-level privilege could incorrectly affect a character using a lower in-game group. The same change converted the acting Help moderator to `playerGroupType`, but left both target authorization checks as:

```lua
playerGroupType > target:getAccountType()
```

Those checks compare two different privilege domains. A moderator can therefore be incorrectly authorized or denied whenever the target character's group and account type differ. No broader chat-core defect or stronger independent legacy donor was identified.

The smallest valid disposition is `ADAPT`: preserve the existing chat implementation and data while comparing both sides of Help-channel `!mute` and `!unmute` authorization in the same player-group domain.

## Target adaptation

Both Help moderation checks now use:

```lua
playerGroupType > target:getGroup():getId()
```

No channel IDs, message types, mute duration, KV key, channel membership lifecycle, chat C++ API, guild/party lifecycle, protocol serializer/parser, maintained client, schema, map, asset or deployment behavior is changed.

## Boundary classification

| Boundary | Classification | Evidence |
|---|---|---|
| ownership/lifecycle | applicable | existing `Chat`/`ChatChannel` runtime ownership and channel maps are unchanged |
| build/toolchain | applicable | only focused unit-test registration is added; no production build entry changes |
| configuration | applicable | existing `CORE_DIRECTORY` and `data/chatchannels/chatchannels.xml` loading remain unchanged |
| service/API | applicable | existing `Chat`, `ChatChannel` and `PrivateChatChannel` interfaces remain unchanged |
| scheduling/concurrency | applicable | existing dispatcher-backed guild MOTD scheduling and in-process channel maps are unchanged |
| persistence | applicable | existing Help-channel KV exhaustion state is unchanged; no schema or persistence contract is added |
| protocol/session | not-applicable to adaptation | no packet, opcode, serializer, session or maintained-client change |
| identifiers/assets | applicable | existing channel IDs and script names are unchanged |
| world/map | not-applicable | no OTBM or world-content dependency |
| runtime | applicable | authorization remains synchronous Lua callback behavior within the existing chat lifecycle |
| tests | applicable | focused Lua-execution tests exercise conflicting account/group privilege scenarios |
| physical-client E2E | not-applicable to adaptation | the changed boundary is deterministic server-side authorization with no wire/client contract change |
| operations | not-applicable | no deployment, configuration rollout or operational state change |
| security/privacy | applicable | the adaptation closes a privilege-domain mismatch in moderator authorization |

No applicable boundary remains unresolved for this bounded adaptation.

## Focused proof

`Oam025ChatCommunicationAdaptTest` executes the real `help.lua` file inside a Lua state with deterministic player/group/account stubs and proves both changed authorization sites:

1. a Senior Tutor group cannot mute a higher-group target even when that target exposes a lower account type;
2. a Senior Tutor group can unmute a lower-group target even when that target exposes a higher account type.

The scenarios deliberately make account type conflict with group rank, so either stale `target:getAccountType()` comparison fails the proof while the group-to-group policy succeeds.

## Explicit non-claims

OAM-025 does not claim Real Tibia chat parity, guild or party membership lifecycle, wire packet compatibility, client UI behavior, generic moderation policy, message privacy or delivery guarantees, NPC conversations, distributed chat, physical-client chat E2E closure, generic persistence redesign, or changes to maintained OTClient, maps, OTBM, `items.otb`, assets, schema or deployment.

The final target merge gate must use the exact final PR head and include changed-file, CI, review/comment/thread and target-main drift audits before expected-head squash merge.
