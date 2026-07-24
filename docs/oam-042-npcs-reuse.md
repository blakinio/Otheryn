# OAM-042 NPC target reuse proof

## Decision boundary

Canonical package: `npcs`.

Candidate disposition: `REUSE`, subject to exact-final-head target gates and the explicit evidence limits below.

This proof covers NPC definition and registration plumbing, Lua callbacks, dialogue state, shops, travel, quest hooks and the previously proven placement/definition correlation boundary. It does not claim generic quest progression, client protocol, persistence completeness or production gameplay parity.

## Exact reviewed source identity

The clean Otheryn target and current `opentibiabr/canary` expose identical Git blobs for the reviewed contract paths:

| Path | Blob |
|---|---|
| `src/creatures/npcs/npcs.cpp` | `5a5d37d4085c9b564936f721469c831b12fee6a4` |
| `src/creatures/npcs/npc.cpp` | `2aee02b7b0ff6b69c868365ac4ba102b5b115f40` |
| `data/npclib/load.lua` | `ad7cb718531212facdca6b842cbf03e63945f379` |
| `data/npclib/npc_system/modules.lua` | `40a58c2ca7c74e28c51565604390ad80dcdb30af` |
| `data-otservbr-global/npc/harlow.lua` | `c8eae6fe74881ab4c08305cd383e92517d14feae` |
| `data-otservbr-global/npc/rashid.lua` | `b1f8b022e07f83cbe401c410efb3efa10f3ec697` |
| `data-otservbr-global/world/otservbr-npc.xml` | `0a72085b7bbdfca73b794e631cc2bab790d8fcef` |

Blob identity is supporting evidence only. The source-contract test protects the semantics reviewed below.

## Registration and callback contract

`Npcs::load` loads the core `npclib/load.lua` bundle and then the active datapack `npc` directory. `Npcs::getNpcType` normalizes names with `asLowerCaseString`, so placement resolution remains case-insensitive.

`NpcType::loadCallback` binds the reviewed Lua events for think, appear, disappear, movement, speech, buy, sell, item inspection and channel close. `NpcType::loadShop` updates canonical item buy/sell prices, rejects duplicate shop entries and stores the normalized shop blocks used by runtime trade handling.

The Lua `Npc` interface exposes shop-window, interaction, speech, movement and sell-item methods and initializes both `ShopFunctions` and `NpcTypeFunctions`.

## Dialogue, travel and quest-hook contract

The core npclib bundle loads the NPC handler, keyword handler, standard/custom modules, dialog and bank system.

`StdModule.travel` requires a valid active interaction and preserves:

- premium and minimum-level restrictions;
- PZ-lock rejection;
- bank/money cost removal;
- non-negative travel discounts;
- the three-second NPC travel exhaustion boundary;
- function or literal destinations;
- teleport and visual effect;
- interaction reset after completion.

Harlow is the bounded travel example. The script requires `Storage.Quest.U8_4.BloodBrothers.VengothAccess == 1`, charges 100 gold and sends the player to `Position(32858, 31549, 7)`. It registers the standard callback set, focused dialog handler and final `npcConfig`.

Rashid is the bounded combined dialogue/shop/quest-hook example. The script preserves ordered travelling-trader storage transitions, item hand-ins, the recognised-trader achievement, a trade-request gate on Mission07 and the explicit shop catalogue before registering `npcConfig`.

These examples prove the target mechanisms and representative current-upstream data contracts. They do not assert that every individual NPC conversation is factually complete.

## Placement evidence reuse

OAM-041 external Canary evidence remains authoritative for static NPC placement and definition correlation. It covered the active datapack and retained duplicate Harlow definition ambiguity plus nonliteral dynamic creation calls as unresolved evidence.

OAM-042 does not copy the OTBM tooling into Otheryn and does not reinterpret unresolved findings as handled. A final `REUSE` disposition keeps those findings visible as bounded evidence gaps.

## Validation strategy

During implementation, use source review and the focused OAM-042 unit contract. Compile once at the coherent milestone after the task record, proof document, test and CMake registration are complete.

Final validation requires the exact PR head to pass the repository CI and `Required` aggregator. No runtime/datapack/map/binary/protocol/client/schema/deployment file is modified by this proof.
