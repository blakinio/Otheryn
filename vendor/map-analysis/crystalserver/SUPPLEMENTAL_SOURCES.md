# CrystalServer atlas supplemental sources

Pinned source: `zimbadev/crystalserver@5e89bf8329ea406cb4ea8f4a18f32954f13e5418`.

Atlas-relevant supplemental source trees:

- `data-global/scripts/**` — upstream Git tree `0e3b0102c7d841345dc5b9d4a3b81631930dc362`; authoritative scripted actions, movements, quests, world changes and Lua raids used to resolve map mechanics against the same revision as `world.otbm`.
- `data-global/raids/**` — upstream Git tree `95da7008cf26e5b41ad9f6ef6b5666707feb295c`; authoritative XML raid registry and event spawn definitions, including delays, single positions and area bounds.
- `data/npclib/npc_system/**` — upstream Git tree `8c95fc6faf1dc2c6c573cb57973838897a458a28`; shared NPC helper semantics needed to interpret calls such as bank and travel modules in the already-vendored `data-global/npc/**` definitions.

These trees are provenance inputs. They must not be interpreted by directory name alone: atlas-derived facts should preserve the exact source path and use `RESOLVED`, `AMBIGUOUS` or `UNKNOWN` states whenever static analysis cannot prove runtime behavior.
