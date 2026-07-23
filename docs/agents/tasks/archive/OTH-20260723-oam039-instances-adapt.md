---
task_id: OTH-20260723-oam039-instances-adapt
status: archived
created: 2026-07-23
updated: 2026-07-23
related_pr: "81"
modules_touched:
  - instances
---

# OAM-039 Instances target adaptation — archived

Final disposition: `instances → ADAPT`.

Immutable target task-start main was `a275f1d788b50164ffc79b6f6143e13b9150c82e`. Canary OAM-039 preflight PR #771 merged as `5c0613fd853e85421a89f661e9b3774c4dd730ff` and selected canonical `instances` as an ADAPT candidate because clean Otheryn and fresh upstream lacked the canonical `InstanceManager` roots.

Otheryn target delivery PR #81 remained bounded to 19 intended task/evidence, canonical `src/game/instance/**`, CMake and focused unit-test paths. It did not import cross-module Game/Creature/Lua/talkaction/protocol/client/map-content/asset/schema/persistence wiring, and legacy hard-coded `data-canary` arena coordinates were deliberately not adopted.

Initial exact head `58c4d2cf2cb5f26d67974b78e9d8e16885eae702` exposed one owned Linux-debug failure in `InstanceManagerTest.CleanupRunsExactlyOnceAndDirtyRegionIsQuarantined`: a quarantined `Closing` instance returned early on retry and therefore could not release its reserved region after creature ownership was later drained. Bounded fix commit `0add27da10d73dd025798b22ae494822db14d780` changed `close()` so a `Closing` retry skips the cleanup callback but retries finalization and region release once ownership is empty, preserving exactly-once cleanup.

PR #81 final head `e216c3bb732bc6dc97374833bbfcb13a4f4ebc50` passed autofix `30002236999`, CI `30002237279`, Required `30002237057`, Fast Checks, Lua, Linux release/debug including full `Run Tests`, both Windows build paths, macOS and Docker. The final PR changed exactly the 19 intended paths; comments, reviews and review threads were empty; target `main` had no task-start drift; and PR #81 squash-merged as `a2a52e239d8e8a770ff7376fcbb9b5bfdcc8cc13`.

Canary governance PR #779 merged as `7f5fcfb77c35f83f0841ee1d57a70878b5e544d0`. Authoritative Canary lifecycle PR #786 merged as `5f434e9f1e792670545aaf818e34af47c40b2c88`. Separate durable program reconciliation PR #788 merged as `f7981992d047b2d718989500ba4a1ef46ec68e3d`.

With this target checkpoint archive, OAM-039 is formally complete. A fresh OAM-040 preflight may start from current live repository state; no OAM-040 package is selected by this archive.
