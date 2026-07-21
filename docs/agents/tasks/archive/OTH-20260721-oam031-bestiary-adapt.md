---
task_id: OTH-20260721-oam031-bestiary-adapt
status: archived
branch: dudantas/oam-031-bestiary-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: "63"
---

# OAM-031 Bestiary target adaptation — archived

Final disposition: `bestiary → ADAPT`.

The bounded target change imported exactly two reviewed legacy PR #188 Bestiary-owned corrections in `src/io/iobestiary.cpp`: fail-safe `player`/`mtype` validation before race-id dereference in `IOBestiary::addBestiaryKill`, and floating-point chance division in `IOBestiary::calculateDifficult`. Charm reset pricing and PR #192 monster-definition data remained excluded.

Otheryn PR #63 final head `c49796d696448aa168c34629dc9ebcd9fd7a9465` passed autofix.ci #187 run `29825053904`, CI #226 run `29825054221`, Required #211 run `29825053840`, and Linux debug full `Run Tests`; artifact `8493329878` digest is `sha256:e99f341683bc432512ddd0dc235204f8b13510cd48eaf9f06c9cdf53d7dbc432`. The PR had exactly five intended paths, zero comments/reviews/threads and no target-main drift, then merged by expected-head squash as `86e4b08c28ede2f35c215a7c2327a579f4a61419`.

Canary governance merged as `e55e0d548d6013da6676cc7b06cbb8d459ccdd1f`, authoritative lifecycle as `0fca8ced2d952eab744238f826af81cb9ee135b1`, and durable program reconciliation as `819e4f9d19f71a06dacb4d395734f47ebc03422d`.
