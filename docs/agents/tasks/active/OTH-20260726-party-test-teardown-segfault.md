---
task_id: OTH-20260726-party-test-teardown-segfault
status: investigating
branch: dudantas/fix-party-test-teardown
base_branch: main
created: 2026-07-26
updated: 2026-07-26
related_issue: "125"
related_pr: ""
owned_paths:
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
  - .github/workflows/ci.yml
  - .github/workflows/reusable-build-linux.yml
search_first:
  - tests/unit
  - src/creatures/players/grouping
  - src/lib/di
  - src/lua/creature
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

Ready-head CI for PR 123 failed twice on the same exact source head. The test body printed `OK`, then CTest recorded `SEGFAULT` during or after teardown:

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

## Current source inventory

- `party_test.cpp` installs a suite-scoped in-memory logger injector and sets the global DI test container.
- The test directly constructs `Party` and three unit-test `Player` objects, manually inserts null/member/invitee entries, then invokes full `Party::disband()`.
- `Party::disband()` enters production global event, callback and game services before clearing Party/player relationships.
- The test assertions complete successfully; the process crashes only afterward.
- Other fixtures use the same DI logger pattern, so the injector alone is not yet proven as the cause.
- The prior OAM-023 proof does not call the full disband path with real Player objects.

## Bounded investigation plan

1. Add a focused Linux diagnostic that runs only the failing test repeatedly with AddressSanitizer and UndefinedBehaviorSanitizer where repository toolchains permit.
2. Capture the first actionable stack or lifetime report.
3. Decide whether the defect is:
   - a test fixture/global-singleton lifetime problem;
   - an invalid test setup that bypasses reciprocal Party invariants;
   - a production Party teardown bug exposed by null entries;
   - a Player/Party ownership-cycle cleanup defect.
4. Apply the smallest deterministic fix at the proven boundary.
5. Preserve null-entry coverage and full post-disband state assertions.
6. Pass focused repeated execution, sanitizer evidence, full exact-head CI and `Required`.

## Explicit non-goals

- no PRS-001 file changes;
- no skipped or disabled Party test;
- no weakening of repository `Required`;
- no broad Party feature refactor;
- no protocol, client, persistence, schema or deployment changes;
- no speculative production mutation before a diagnostic identifies the fault boundary.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T12:45:00+02:00
head: 38bb62192d25984d63f96c2637348b4adc82f6cd
branch: dudantas/fix-party-test-teardown
pr: none
status: investigating
context_routes:
  - testing
  - player-lifecycle
  - party
  - ci
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/OTH-20260726-party-test-teardown-segfault.md
proven:
  - Task-start main is 38bb62192d25984d63f96c2637348b4adc82f6cd.
  - Issue 125 owns only the repeated Party unit-test teardown SIGSEGV.
  - Two Linux debug attempts reproduced the same post-success SEGFAULT on PartyTest.GetPlayersAndDisbandHandleNullEntries.
  - The remaining 482 Linux debug tests and all other ready-head CI platform jobs passed.
  - PRS-001 does not change Party runtime or Party test files.
  - The failing test invokes full Party::disband after manually constructing Party membership and invitation lists.
  - The test body assertions pass before the process crashes.
  - Other unit fixtures use the same suite-scoped DI logger pattern without this known failure.
derived:
  - The failure is a lifetime or teardown defect rather than an assertion failure.
  - A focused sanitizer/repetition diagnostic is required before selecting a production or fixture fix.
unknown:
  - Exact crashing frame and object lifetime.
  - Whether reciprocal invitation state is required for valid disband setup.
  - Whether the failure is in production Party teardown, test-only global services, or Player destruction.
conflicts: []
first_failure:
  marker: party-test-post-success-segfault
  command: CI run 30197504976 jobs 89781674816 and 89782999565
  result: OPEN
  evidence: The named test prints OK and then both attempts terminate with SIGSEGV during or after teardown.
rejected_hypotheses:
  - Skip or disable the failing test.
  - Weaken Required or ignore Linux debug.
  - Modify PRS-001 to absorb the Party fix.
  - Assume the suite-scoped injector is the cause without diagnostic evidence.
changed_paths:
  - docs/agents/tasks/active/OTH-20260726-party-test-teardown-segfault.md
validation:
  - command: repeated ready-head Linux debug evidence review
    result: PASS
    evidence: Two independent attempts reproduced the same single-test post-success SEGFAULT.
  - command: initial source and ownership inventory
    result: PASS
    evidence: Failing test, Party disband path, Player ownership and CI execution boundary were inspected.
  - command: focused sanitizer diagnostic
    result: NOT_RUN
    evidence: Add after exact workflow and compiler flags are selected.
blockers: []
next_action: Add a focused sanitizer and repeated-execution diagnostic for PartyTest.GetPlayersAndDisbandHandleNullEntries, then use its first actionable stack to select the smallest valid fix.
```
