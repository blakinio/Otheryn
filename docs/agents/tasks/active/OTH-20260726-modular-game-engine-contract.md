---
task_id: OTH-20260726-modular-game-engine-contract
status: ready
branch: dudantas/modular-game-engine-contract
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "120"
related_pr: "121"
owned_paths:
  - docs/architecture/modular-game-engine-and-profiles.md
  - docs/agents/tasks/active/OTH-20260726-modular-game-engine-contract.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/architecture/modular-game-engine-and-profiles.md
  - docs/architecture/production-resilience-and-recovery.md
search_first:
  - src/config/configmanager.cpp
  - src/config/configmanager.hpp
  - src/lua
  - src/server
  - src/game
  - src/creatures/players
  - docs/oam-046-configuration-adapt.md
  - docs/oam-044-protocol-compatibility-reuse.md
optional_reads: []
---

# Modular game engine and profile architecture contract

## Goal

Persist the agreed modular-monolith, gameplay-module, C++/Lua configuration and historical-profile architecture so a future agent can continue without relying on chat history. This task is documentation-only and does not authorize runtime refactoring, source relocation, profile loading, protocol changes, datapack changes, dynamic plugins, schema changes or deployment changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T11:18:00+02:00
head: 84851148ce82ccd77952bd040599125029668f58
branch: dudantas/modular-game-engine-contract
pr: 121
status: ready
context_routes:
  - architecture
  - engine-foundation
  - gameplay
  - configuration
  - lua
  - protocol
  - multichannel
  - agent-governance
owned_paths:
  - docs/architecture/modular-game-engine-and-profiles.md
  - docs/agents/tasks/active/OTH-20260726-modular-game-engine-contract.md
proven:
  - Task-start main is 4eedf835621e2a64d093dd5096b4b28e632e50f3.
  - Issue 120 owns a documentation-only modular game-engine and historical-profile contract.
  - No open Otheryn pull request existed at task start and repository search found no existing GameProfile or ModuleRegistry architecture document.
  - Otheryn already uses typed C++ configuration loaded from Lua, but current configuration does not prove a complete safe module graph or historical profile system.
  - The production resilience architecture is merged and remains authoritative for persistence, stale-writer fencing and multichannel recovery boundaries.
  - The architecture document defines one modular-monolith process per channel rather than one service or container per gameplay feature.
  - It separates core-engine modules, gameplay-feature modules and content packages.
  - It assigns legal module identity, dependencies, lifecycle, threading, persistence and safety validation to C++.
  - It assigns declarative profile selection, optional module choices, ruleset identifiers and content identifiers to Lua.
  - It requires Lua profile data to become a typed validated startup snapshot rather than a continuously queried runtime authority.
  - It records that disabling modern modules alone does not prove a Tibia 7.6 profile; protocol, rulesets, content, assets and physical-client evidence are also required.
  - It defines MGE-001 through MGE-008 as separate future packages and authorizes MGE-001 ownership/dependency inventory as the next package.
  - PR 121 is ready for review and changes exactly the two owned documentation paths.
  - Required runs 30195823218 and 30195885601 passed on audited head 84851148ce82ccd77952bd040599125029668f58.
  - PR 121 has no conversation comments, submitted reviews or review threads.
derived:
  - A shared hardened engine with profile-selected protocol, rules and content avoids long-lived 7.6, 8.6 and current-version engine forks.
  - Static libraries may later enforce proven dependencies, but dynamic plugin ABI is unnecessary for the initial architecture.
  - The first runtime extraction should be a bounded vertical feature rather than a broad Game, Player or source-tree rewrite.
unknown:
  - Exact current dependency cycles, singleton access and mutation ownership across gameplay source paths.
  - Exact typed GameProfile and ModuleRegistry APIs.
  - Which feature is the safest first vertical extraction after MGE-001 evidence.
  - Exact protocol, datapack, item registry and physical-client evidence available for a future 7.6 profile.
conflicts: []
first_failure:
  marker: no-durable-modularity-contract
  result: RESOLVED_BY_DESIGN
  evidence: Prior modularity decisions existed only in chat; this package records them as a bounded repository architecture and future-agent checkpoint.
rejected_hypotheses:
  - Create one network service or Docker container for each gameplay feature.
  - Treat every quest, NPC, monster or spell as a separate C++ module.
  - Let Lua define module dependencies, lifecycle, threading, persistence or security boundaries.
  - Hardcode every profile decision as scattered client-version branches.
  - Allow runtime hot toggling of the module graph.
  - Claim historical 7.6 parity by disabling Wheel, Prey and Forge alone.
  - Begin by moving the complete source tree or rewriting Game and Player.
changed_paths:
  - docs/architecture/modular-game-engine-and-profiles.md
  - docs/agents/tasks/active/OTH-20260726-modular-game-engine-contract.md
validation:
  - command: current main, open-PR ownership and existing-document search
    result: PASS
    evidence: Main was pinned, no open PR existed and no existing modular-profile contract was found.
  - command: architecture scope and safety review
    result: PASS
    evidence: Only documentation is added; no runtime, build, protocol, Lua behavior, schema, datapack or deployment path is changed.
  - command: checkpoint schema and compactness review
    result: PASS
    evidence: The task contains one checkpoint, required fields, accepted evidence states, bounded lists and exactly one concrete next action.
  - command: exact two-path, discussion and ready-head audit
    result: PASS
    evidence: PR 121 contains exactly the two owned paths and has no comments, reviews or review threads.
  - command: exact-head Required
    result: PASS
    evidence: Required run 30195885601 completed successfully on 84851148ce82ccd77952bd040599125029668f58 after the PR became ready.
blockers: []
next_action: Revalidate PR 121 on its final checkpoint head, then expected-head squash-merge it and archive this task before creating a separate MGE-001 ownership-inventory issue.
```
