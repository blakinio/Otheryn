---
task_id: OTH-20260723-oam040-otbm-tooling-do-not-migrate
status: ready
branch: dudantas/oam-040-otbm-tooling-do-not-migrate
base_branch: main
created: 2026-07-23
updated: 2026-07-23
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260723-oam040-otbm-tooling-do-not-migrate.md
  - docs/oam-040-otbm-tooling-do-not-migrate.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - docs/oam-040-otbm-tooling-do-not-migrate.md
optional_reads: []
---

# OAM-040 OTBM tooling target disposition proof

## Goal

Prove whether the canonical `otbm-tooling` responsibility belongs inside clean Otheryn core or should remain in the Canary laboratory/evidence repository while downstream world-content packages consume its pinned evidence cross-repository.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T14:30:00+02:00
head: ea69c79c3a3ae905720c408fe6612a9f7b71e601
branch: dudantas/oam-040-otbm-tooling-do-not-migrate
pr: null
status: ready
context_routes:
  - agent-governance
  - cross-repo
  - otbm
owned_paths:
  - docs/agents/tasks/active/OTH-20260723-oam040-otbm-tooling-do-not-migrate.md
  - docs/oam-040-otbm-tooling-do-not-migrate.md
proven:
  - Target task-start main is 5eea55ca3dd7689d097fadef3ff92eee84f8c163.
  - Canary OAM-040 preflight PR 790 merged as 90b5054ebc8b2a19d52cc1bc2731e9dc6f3080f3 and selected canonical otbm-tooling as a DO_NOT_MIGRATE candidate.
  - Fresh upstream baseline is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a and maintained OTClient baseline is 1e5305395159142634f182d9e888e5f9164228c6.
  - Canonical otbm-tooling has no hard dependencies and owns no server client or data paths.
  - The canonical responsibility is deterministic OTBM analysis and evidence rather than Otheryn gameplay runtime behavior.
  - The Oteryn architecture contract assigns Canary the legacy laboratory evidence source and validation environment roles while Otheryn is the clean selectively populated target.
  - The architecture contract requires world-content migration to reuse the existing deterministic OTBM analysis stack.
  - The maintained OTBM roadmap is explicitly scoped to blakinio/canary and records phases 1 through 8 merged and archived.
  - Representative legacy tools/ai-agent/otbm_world_index.py exists as blob d1e23a9df27a070e2d77fd98210b8574f0c9e0bf while clean Otheryn and fresh upstream lack that root and the OTBM tooling roadmap.
  - Canonical spawns and npcs depend on otbm-tooling and quests depends on otbm-tooling plus player-persistence.
  - Those downstream dependencies can consume pinned Canary tool and report provenance as cross-repository evidence without importing the analysis stack into Otheryn core.
  - No identified Otheryn runtime service protocol client map-loader production build or data path requires a target-local OTBM analysis tool module.
  - No production test runtime protocol client data map asset schema deployment or build path is changed by this target proof.
derived:
  - The final target disposition is otbm-tooling DO_NOT_MIGRATE.
  - DO_NOT_MIGRATE excludes the tooling from Otheryn core but does not delete deprecate or freeze the maintained Canary evidence stack.
  - The canonical dependency graph remains intact because downstream world-content packages still depend on the external evidence responsibility and must pin their own exact tooling/report provenance.
  - EXPERIMENTAL_ONLY is weaker and inaccurate because the Canary tooling is an established deterministic evidence stack rather than merely experimental functionality.
unknown:
  - Exact final target PR head merge SHA and Required run evidence until this proof PR executes.
  - Exact evidence artifacts future spawns npcs or quests packages will consume; each downstream package must select and pin them independently.
conflicts: []
first_failure:
  marker: none
  evidence: This is a documentation-only target disposition proof; target Required has not executed yet.
rejected_hypotheses:
  - REUSE the tool suite in Otheryn; there is no target-local runtime/product responsibility requiring the transfer.
  - ADAPT or REWRITE a target-local OTBM stack; the existing Canary deterministic evidence stack already owns that responsibility.
  - EXPERIMENTAL_ONLY; the stack is established and maintained rather than experimental-only, while the target exclusion is explicit.
  - Remove otbm-tooling from the canonical registry; downstream world-content still depends on its external evidence responsibility.
changed_paths:
  - docs/agents/tasks/active/OTH-20260723-oam040-otbm-tooling-do-not-migrate.md
  - docs/oam-040-otbm-tooling-do-not-migrate.md
validation:
  - command: repository-role and canonical ownership proof
    result: PASS
    evidence: target architecture assigns evidence tooling to Canary laboratory roles and canonical otbm-tooling owns no server client or data paths
  - command: representative target upstream absence proof
    result: PASS
    evidence: representative World Index tooling and OTBM roadmap are absent from clean Otheryn and fresh upstream
  - command: downstream dependency impact analysis
    result: PASS
    evidence: spawns npcs and quests may consume pinned cross-repository Canary evidence without requiring a target-local tooling copy
blockers: []
next_action: Open the two-path OAM-040 target disposition PR, bind its PR number, require exact-current-head Required success, audit scope comments reviews threads and target-main drift, then expected-head squash merge before Canary governance closure.
```
