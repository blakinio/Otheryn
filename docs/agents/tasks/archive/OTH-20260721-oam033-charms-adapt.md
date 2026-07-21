---
task_id: OTH-20260721-oam033-charms-adapt
status: archived
branch: dudantas/oam-033-charms-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: "67"
---

# OAM-033 Charms target adaptation — archived

Final disposition: `charms → ADAPT`.

The bounded target package applied exactly two reviewed Charm-owned corrections from merged legacy PR #188: `registerCharm.category` now gates on `mask.category`, and the all-Charm reset price charges the `11,000` surcharge only for levels above 100. Bestiary, Bosstiary, Cyclopedia Character, monster-data and maintained-client work remained outside OAM-033.

Otheryn PR #67 final head `e1fca0b372173db335118735f501f315d442888f` changed exactly seven intended paths. The first Linux-debug full suite passed `421/422`; its sole failure was the superseded OAM-031 Charm reset-price boundary assertion, while both OAM-033 focused proofs passed. That obsolete proof assertion was retired without further production change. Autofix.ci #192 run `29867543037`, Repository Audit #27 run `29867542987`, CI #233 run `29867543182`, Required #218 run `29867542998`, and Linux-debug full `Run Tests` succeeded. Test-log artifact `8510218346` digest is `sha256:1bc7425f036bb5f39c19539590da0704f026718e4bbd54ad2ede79c023300cbc`. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #67 merged by expected-head squash as `c887318a676998da5ef3224a3aa8d1e0df75e607`.

Canary governance merged as `5ecc72762feb6bda8f6549ac4238a75247752449`, authoritative lifecycle as `d83563943e298df33edd084e944812464b8a3ff2`, and durable program reconciliation as `ab2fb5548260544f42f786d11d4dd1b600c39a06`.
