---
task_id: OTH-20260726-modular-game-engine-contract
status: completed
branch: dudantas/modular-game-engine-contract
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "120"
related_pr: "121"
feature_merge: "e641bc9d4be6275d75d4f4af0d38a2179429a193"
lifecycle_pr: "124"
owned_paths:
  - docs/architecture/modular-game-engine-and-profiles.md
  - docs/agents/tasks/archive/OTH-20260726-modular-game-engine-contract.md
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

# Modular game engine and profile architecture contract — completed

## Result

PR #121 was expected-head squash-merged as `e641bc9d4be6275d75d4f4af0d38a2179429a193`. The repository now contains the active target contract for a modular monolith per game channel, explicit core/gameplay/content boundaries, typed C++ module ownership and lifecycle, declarative Lua game profiles, fail-closed profile validation, historical profile requirements and independent `MGE-001` through `MGE-008` continuation packages.

No runtime refactor, source relocation, module loader, dynamic plugin ABI, protocol behavior, Lua runtime behavior, datapack, asset, schema or deployment change was introduced.

## Final checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T12:15:00+02:00
head: e641bc9d4be6275d75d4f4af0d38a2179429a193
branch: main
pr: 121
status: completed
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
  - docs/agents/tasks/archive/OTH-20260726-modular-game-engine-contract.md
proven:
  - Task-start main was 4eedf835621e2a64d093dd5096b4b28e632e50f3.
  - Issue 120 authorized a documentation-only modular game-engine and historical-profile contract.
  - PR 121 final head was 1ad569b1c29bd786efd928d887d195484bebe6da.
  - PR 121 changed exactly the architecture document and active task checkpoint.
  - Final discussion audit found no comments, submitted reviews or review threads.
  - Required run 30195926663 passed on exact final head 1ad569b1c29bd786efd928d887d195484bebe6da.
  - PR 121 was expected-head squash-merged as e641bc9d4be6275d75d4f4af0d38a2179429a193.
  - Lifecycle PR 124 owns only the active-to-archive task move and final evidence record.
  - The merged contract defines one modular-monolith process per channel, not one service per gameplay feature.
  - It separates core-engine modules, gameplay-feature modules and content packages.
  - C++ owns legal module identity, dependencies, lifecycle, threading, persistence, safety validation and typed configuration schemas.
  - Lua declaratively selects profiles, optional modules, rulesets and content from C++-provided capabilities.
  - Historical parity cannot be claimed by disabling modern modules alone; protocol, rulesets, content, assets and physical-client evidence are also required.
  - MGE-001 through MGE-008 remain independent future packages; no MGE runtime implementation was introduced.
derived:
  - A shared hardened engine with profile-selected protocol, rules and content avoids long-lived per-version engine forks.
  - MGE-001 ownership and dependency inventory is the required next implementation-planning package.
unknown:
  - Exact current dependency cycles, singleton access and mutation ownership across gameplay source paths.
  - Exact typed GameProfile and ModuleRegistry APIs.
  - Safest first bounded vertical feature after MGE-001 evidence.
  - Exact evidence available for a future Tibia 7.6 protocol, ruleset, datapack, assets and physical-client parity claim.
conflicts: []
first_failure:
  marker: no-durable-modularity-contract
  result: RESOLVED_BY_DESIGN
  evidence: The repository now contains a durable architecture and continuation contract independent of chat history.
rejected_hypotheses:
  - Create one process or container for every gameplay feature.
  - Treat every quest, NPC, monster or spell as a separate C++ module.
  - Let Lua define dependencies, lifecycle, threading, persistence or security boundaries.
  - Hardcode historical profiles through scattered client-version conditionals.
  - Allow runtime hot toggling of the module graph.
  - Claim Tibia 7.6 parity by disabling Wheel, Prey and Forge alone.
  - Begin modularization by rewriting Game, Player or the entire source tree.
changed_paths:
  - docs/architecture/modular-game-engine-and-profiles.md
  - docs/agents/tasks/archive/OTH-20260726-modular-game-engine-contract.md
validation:
  - command: exact two-path scope audit
    result: PASS
    evidence: PR 121 contained only the architecture contract and active task checkpoint.
  - command: final discussion audit
    result: PASS
    evidence: PR 121 had no comments, reviews or review threads.
  - command: exact-head Required 30195926663
    result: PASS
    evidence: Required completed successfully on final head 1ad569b1c29bd786efd928d887d195484bebe6da.
  - command: expected-head squash merge
    result: PASS
    evidence: PR 121 merged as e641bc9d4be6275d75d4f4af0d38a2179429a193.
blockers: []
next_action: Merge lifecycle PR 124, close issue 120 as completed, then create a separate issue and active task for MGE-001 ownership and dependency inventory before any modular runtime refactor.
```
