---
task_id: OTH-20260724-oam041-spawns-reuse
status: archived
created: 2026-07-24
updated: 2026-07-24
related_pr: "92"
modules_touched:
  - spawns
---

# OAM-041 spawns target reuse proof — archived

Final disposition: `spawns → REUSE`.

The bounded target proof confirmed that Otheryn already preserves the canonical monster/NPC spawn contract: XML center-plus-offset placement, interval/default and rate scaling, player blocking, removed-creature cleanup, maintenance-lane scheduling, boss exclusivity and weighted monster selection. No production runtime, datapack, map, binary asset, protocol, client, schema, deployment or tooling implementation was changed.

Deterministic external Canary OTBM evidence run `30049543113` pinned Canary revision `d1ad83056ec7930f067986909f66b8f20f1a1f44`, map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` and World Index SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`. The complete bounded correlation confirmed `34/34` groups and `39/39` static placements with zero correlation findings. Duplicate Harlow definition ambiguity and `310` unresolved nonliteral dynamic creation calls remain explicit evidence boundaries.

Otheryn target PR #92 final head `2168ff23a7415b9aea8f66b7051995e7fd148691` changed exactly the task/proof/source-contract-test/CMake-registration paths. Autofix `30068408311`, CI `30068408471` and Required `30068408289` succeeded, including Linux release/runtime smokes, Linux debug full tests, macOS and both Windows build paths. Comments, reviews and review threads were empty, target `main` had no conflicting drift, and PR #92 squash-merged as `de061aa6c75114192f1ef6b33f7b4857e502936c`.

Canary governance PR #853 merged as `0dc3fa9d663af47f8808d2457c8108a63294c7c4`; Canary lifecycle PR #854 merged as `55f9e46ab0804ec2c7b58cfffc772a243234c956`; durable program reconciliation PR #856 merged as `bc4ae5861d7b9c172d9c15ce78181cb4c2be4ead`.

Target lifecycle delivery is Otheryn PR #94 and remains limited to the active-task removal plus this archived record.

With this target checkpoint archive, OAM-041 is formally complete. A fresh OAM-042 preflight may now select exactly one dependency-valid canonical package from current live repository state.
