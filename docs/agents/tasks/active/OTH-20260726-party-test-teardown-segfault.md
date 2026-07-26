---
task_id: OTH-20260726-party-test-teardown-segfault
status: validating
branch: dudantas/fix-party-test-teardown
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "125"
related_pr: "126"
owned_paths:
  - .github/workflows/party-test-sanitizer.yml
  - tests/unit/players/party_test.cpp
  - docs/agents/tasks/active/OTH-20260726-party-test-teardown-segfault.md
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - tests/unit/players/party_test.cpp
  - tests/unit/players/CMakeLists.txt
  - src/creatures/players/grouping/party.cpp
  - src/creatures/players/grouping/party.hpp
  - src/creatures/players/player.cpp
  - src/creatures/players/player.hpp
  - src/lua/scripts/lua_environment.cpp
  - src/lua/scripts/luascript.cpp
  - src/lua/creature/raids.hpp
  - src/game/game.cpp
  - .github/workflows/ci.yml
  - .github/workflows/reusable-build-linux.yml
  - CMakePresets.json
search_first:
  - tests/unit
  - src/creatures/players/grouping
  - src/lib/di
  - src/lua
  - .github/workflows
optional_reads:
  - docs/oam-023-parties-reuse.md
  - tests/unit/game/oam_023_parties_reuse_test.cpp
---

# Party unit-test teardown SIGSEGV

## Goal

Identify and fix the deterministic post-test segmentation fault in `PartyTest.GetPlayersAndDisbandHandleNullEntries` without weakening the test, skipping it, changing PRS-001, or broadening into unrelated Party/gameplay behavior.

## Task-start target

```text
blakinio/Otheryn@38bb62192d25984d63f96c2637348b4adc82f6cd
```

## Reproduction evidence

Ready-head CI for PR 123 failed twice on the same exact source head. The test body printed `OK`, then CTest recorded `SEGFAULT` during process teardown:

```text
PartyTest.GetPlayersAndDisbandHandleNullEntries
```

Evidence:

- CI run `30197504976`;
- initial job `89781674816`;
- rerun job `89782999565`;
- both attempts passed 482 of 483 Linux debug tests;
- all other ready-head CI platform jobs passed;
- PRS-001 contains no Party runtime or Party test changes.

## Root cause

Focused ASAN workflow run `30198967320`, job `89785504123`, reproduced the failure after 25 successful repetitions and identified a heap-use-after-free during process exit.

The causal sequence is:

1. `Party::disband()` materializes `Events`, `EventsCallbacks` and `Game` inside the suite-scoped runtime test injector.
2. The test body and all 25 repetitions pass.
3. The process begins static destruction and destroys `LuaScriptInterfaceRegistry`.
4. The static `PartyTest::injector_` is destroyed afterward.
5. Destroying the injector destroys `Game`, then `Raids`, then its `LuaScriptInterface`.
6. `LuaScriptInterface::closeState()` calls `LuaEnvironment::getInstance()`.
7. Constructing that Lua environment attempts to register a new interface in the already-destroyed registry, producing the ASAN heap-use-after-free.

This is a fixture-owned cross-translation-unit static destruction-order defect. It is not a Party assertion failure, reciprocal invitation defect, Player ownership cycle or production `Party::disband()` defect.

## Selected fix

- Replace the static value injector with a suite-owned `std::unique_ptr`.
- Create and install it in `SetUpTestSuite()`.
- Clear the global DI test-container pointer and explicitly destroy the injector in `TearDownTestSuite()`.
- This destroys `Game` and its Lua-backed members while `LuaScriptInterfaceRegistry` is still alive.
- Preserve the original null-entry setup, full `Party::disband()` call and every post-disband assertion.

## Explicit non-goals

- no PRS-001 file changes;
- no skipped or disabled Party test;
- no weakening of repository `Required`;
- no production Party, Player, Lua, Game or DI runtime mutation;
- no broad Party feature refactor;
- no protocol, client, persistence, schema or deployment changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T13:22:00+02:00
head: cac32dcc5819076562ee5099806a0a9a92515e42
branch: dudantas/fix-party-test-teardown
pr: 126
status: validating
context_routes:
  - testing
  - player-lifecycle
  - party
  - lua-lifecycle
  - ci
  - agent-governance
owned_paths:
  - .github/workflows/party-test-sanitizer.yml
  - tests/unit/players/party_test.cpp
  - docs/agents/tasks/active/OTH-20260726-party-test-teardown-segfault.md
proven:
  - Task-start main is 38bb62192d25984d63f96c2637348b4adc82f6cd.
  - Issue 125 and draft PR 126 own only the repeated Party unit-test teardown SIGSEGV.
  - Two standard Linux debug attempts reproduced the same post-success process-exit failure.
  - Focused ASAN run 30198967320 reproduced a heap-use-after-free after 25 successful test repetitions.
  - LuaScriptInterfaceRegistry was destroyed before the static PartyTest injector.
  - Static injector destruction then destroyed Game and Raids; LuaScriptInterface::closeState constructed LuaEnvironment and touched the freed registry.
  - The defect is in fixture destruction ordering, not production Party behavior.
  - The selected change destroys the test injector explicitly during TearDownTestSuite while the Lua registry is alive.
  - Original null-entry coverage, full disband execution and post-disband assertions are unchanged.
derived:
  - Early deterministic fixture cleanup removes reliance on cross-translation-unit static destruction order.
  - No production Party, Player, Game, Lua or DI runtime change is required.
unknown:
  - Exact-head result of the fixed focused ASAN repetition.
  - Exact-head repository CI and Required results after the fixture fix.
conflicts: []
first_failure:
  marker: party-test-post-success-segfault
  command: Party Test Sanitizer run 30198967320 job 89785504123
  result: DIAGNOSED
  evidence: ASAN reports heap-use-after-free in LuaScriptInterface::RegistryEntry during exit, caused by static injector destruction after LuaScriptInterfaceRegistry destruction.
rejected_hypotheses:
  - Skip or disable the failing test.
  - Weaken Required or ignore Linux debug.
  - Modify PRS-001 to absorb the Party fix.
  - Change production Party::disband behavior.
  - Treat reciprocal invitation state or Player ownership as the root cause.
  - Leak the test injector to suppress teardown.
changed_paths:
  - .github/workflows/party-test-sanitizer.yml
  - tests/unit/players/party_test.cpp
  - docs/agents/tasks/active/OTH-20260726-party-test-teardown-segfault.md
validation:
  - command: standard Linux debug CI run 30197504976
    result: FAIL_EXPECTED
    evidence: Two attempts reproduce the same post-success SEGFAULT and isolate the original blocker.
  - command: Party Test Sanitizer run 30198967320 job 89785504123
    result: FAIL_EXPECTED
    evidence: Baseline ASAN run identifies the exact exit-order heap-use-after-free after 25 successful repetitions.
  - command: fixed focused ASAN repetition
    result: NOT_RUN
    evidence: Run on the refreshed exact head after this checkpoint update.
  - command: exact-head repository CI and Required
    result: NOT_RUN
    evidence: Run after the fixed focused diagnostic is green.
blockers:
  - fixed focused ASAN repetition on the refreshed exact head
  - exact-head repository CI and Required
  - final changed-path, discussion and main-drift audit before merge
next_action: Confirm the refreshed Party Test Sanitizer run passes all 25 repetitions without ASAN or UBSAN findings, then mark PR 126 ready and run exact-head repository gates.
```
