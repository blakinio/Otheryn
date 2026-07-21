---
task_id: OTH-20260721-oam034-creature-definitions-adapt
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-034
status: archived
created: 2026-07-21
updated: 2026-07-22
related_pr: "69"
modules_touched:
  - creature-definitions
---

# OAM-034 Creature definitions adaptation — archived

Final disposition: `creature-definitions → ADAPT`.

Task-start baselines were Canary `ab2fb5548260544f42f786d11d4dd1b600c39a06`, Otheryn `2fe646dfff3d4fc0672c3fbeca85708dabc4ce87`, fresh upstream `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `465b7a2192b176cf8cb9d58e000c38863e4a6e4c`.

OAM-034 adapted exactly six reviewed monster-definition corrections from merged legacy PR #192: numeric Bestiary race metadata for Agrestic Chicken, Terrified Elephant, Haunted Dragon and Crypt Warrior; Crypt Warrior Bestiary `raceId = 1995`; alternate Eradicator Bosstiary `bossRaceId 1225 → 1226`; and Monk's Apparition Bestiary `raceId 1946 → 2636`. Creature AI, spawns, raids, boss orchestration, PR #192 validator infrastructure and unrelated data/runtime remained outside the package.

Otheryn PR #69 final head `dabc868c5ff9ca8009f20f1eb90645937ff18e22` changed exactly ten intended paths. Autofix.ci run `29871761403`, Repository Audit run `29871761411`, CI run `29871761846`, Required run `29871761506`, runtime smoke, schema import and full Linux-debug `Run Tests` succeeded. The suite passed `423/423`, including both focused OAM-034 cases. Test-log artifact `8511786128` digest is `sha256:a53b92d60e34069d5fd0f52cd1ad94957edf757c2e8dd29c13ca5f2ec9ae30be`. PR #69 merged by expected-head squash as `566b3b001987f6f452663b77c380e6405bfc541b`.

Canary governance merged as `2a63c4b1efe2a20bf653b419ffd6baea6cb2ee0d`, authoritative lifecycle as `0ace0e6802501f1752405c4e15d75619171dd4cf`, and durable program reconciliation was completed by Canary PR #705 before this target archive.

OAM-035 was not started by this archive.
