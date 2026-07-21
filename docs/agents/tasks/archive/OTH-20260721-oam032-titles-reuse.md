---
task_id: OTH-20260721-oam032-titles-reuse
status: archived
branch: dudantas/oam-032-titles-reuse
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: "65"
---

# OAM-032 Titles target reuse proof — archived

Final disposition: `titles → REUSE`.

The bounded target package preserved the existing canonical `PlayerTitle` implementation and added focused proof only. Task-start target, legacy and fresh upstream shared exact `player_title.cpp/.hpp` blobs, while reviewed Cyclopedia remediation PR #188 contained no Titles-root path, PR #192 was monster-data remediation, and PR #243 was validator/workflow control. TSD-004 ownership plus donor-history and open-PR audits selected `REUSE`; blob identity alone was not treated as sufficient proof.

Otheryn PR #65 final head `3244c8b0993047d9fe72ed56125a6f9e218defbb` changed exactly four proof/task paths and no production path. Autofix.ci #188 run `29863062941`, CI #228 run `29863063433`, Required #213 run `29863063406`, and Linux-debug full `Run Tests` succeeded. Test-log artifact `8508497986` digest is `sha256:2c2b98f96fe73bd8b2e9123f662779534a70ec7b0a5b7ebe895f1769b05ae9b3`. Comments/reviews/threads were empty and target `main` had no task-start drift. PR #65 merged by expected-head squash as `f5f21347c578a382cf0c52dbb4c69673ab3b05a9`.

Canary governance merged as `212d5e5c4ecbb0bd392880019747e2370299c748`, authoritative lifecycle as `fda6d01b93929ea998965354908062eb6e4e1424`, and durable program reconciliation as `f05ea5e916af00ab1469a2332aaec2d3c9df7478`.
