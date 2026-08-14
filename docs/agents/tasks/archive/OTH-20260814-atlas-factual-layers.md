---
task_id: OTH-20260814-atlas-factual-layers
status: archived
owner: openai
branch: agent/oth-20260814-atlas-factual-layers
base_branch: main
created: 2026-08-14
updated: 2026-08-14T22:42:00+02:00
related_pr: "390"
merge_commit: 2bfacdd8349003aaa9675604269b8ae8004c19a6
ownership_released: true
---

# Atlas factual mechanics, raids/events, boss evidence and NPC services — archived

Final disposition: completed and merged.

PR #390 consumed the pinned `tools/otbm_atlas_facts` producer in the canonical chunked OTBM Atlas. The viewer now keeps direct OTBM teleports separate from proven scripted transitions, exposes only `RESOLVED` + `PROVEN_STATIC` scripted teleport evidence, renders raid/event point spawns and exact rectangular areas, exposes verified boss markers only from explicit resolved `rewardBoss=true`, and enriches base-map NPC spawns with resolved shop/bank/guild-bank/travel service evidence. `UNKNOWN`, `UNRESOLVED` and `AMBIGUOUS` evidence remains non-authoritative and is not promoted to navigable spatial truth.

All new spatial records remain chunked and viewport-bounded. Raid rectangles are included in every intersecting spatial chunk. Search/details and URL-preserved layer controls cover scripted teleports, raid areas/points, verified bosses and NPC services.

Final implementation head `06b467a33f267c31b1ac85fbe768f2b3b71aa1ef` passed CI #958, Required #1162, autofix.ci #804, OTBM Atlas Factual Layer Audit #5, OTBM Atlas Factual Layers #5 including the real Chromium factual-layer journey, OTBM Environment Animation E2E #65, and OTBM Atlas Tests #106 including canonical Thais scan/render, unit/runtime tests and real browser Thais E2E. Full-world jobs were skipped because `ci:final-gate` was not applied, matching the workflow policy.

PR #390 had zero review threads at final hygiene check and was squash-merged with `expected_head_sha` protection as `2bfacdd8349003aaa9675604269b8ae8004c19a6`. The merge commit was verified as the current `main` immediately after merge.
