#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/io/io_bosstiary.cpp"
CMAKE = ROOT / "tests/unit/game/CMakeLists.txt"
TEST = ROOT / "tests/unit/game/oam_030_bosstiary_adapt_test.cpp"
DOC = ROOT / "docs/oam-030-bosstiary-adapt.md"
TASK = ROOT / "docs/agents/tasks/active/OTH-20260721-oam030-bosstiary-adapt.md"

source = SOURCE.read_text(encoding="utf-8")
old_early = '''\tDBResult_ptr result = database.storeQuery(query);\n\tif (!result) {\n\t\tg_logger().error("[{}] Failed to detect boosted boss database. (CODE 01)", __FUNCTION__);\n\t\treturn;\n\t}\n'''
new_early = '''\tDBResult_ptr result = database.storeQuery(query);\n'''
if old_early not in source:
    raise SystemExit("OAM-030 expected early-return block not found")
source = source.replace(old_early, new_early, 1)
old_missing = '''\tif (!result) {\n\t\tg_logger().warn("[{}] No boosted boss found in g_database(). A new one will be selected.", __FUNCTION__);\n\t} else {\n'''
new_missing = '''\tif (!result) {\n\t\tg_logger().warn("[{}] No boosted boss row found. A new one will be selected.", __FUNCTION__);\n\t\tif (!database.executeQuery("INSERT INTO `boosted_boss` (`boostname`, `date`, `raceid`) VALUES ('default', '0', '0')")) {\n\t\t\tg_logger().error("[{}] Failed to initialize the boosted boss database row. (CODE 01)", __FUNCTION__);\n\t\t\treturn;\n\t\t}\n\t} else {\n'''
if old_missing not in source:
    raise SystemExit("OAM-030 expected missing-row branch not found")
source = source.replace(old_missing, new_missing, 1)
SOURCE.write_text(source, encoding="utf-8")

cmake = CMAKE.read_text(encoding="utf-8")
cmake = cmake.replace('            OAM029_SOURCE_DIR="${PROJECT_SOURCE_DIR}"\n', '            OAM029_SOURCE_DIR="${PROJECT_SOURCE_DIR}"\n            OAM030_SOURCE_DIR="${PROJECT_SOURCE_DIR}"\n', 1)
cmake = cmake.replace('            oam_029_cyclopedia_character_adapt_test.cpp\n', '            oam_029_cyclopedia_character_adapt_test.cpp\n            oam_030_bosstiary_adapt_test.cpp\n', 1)
CMAKE.write_text(cmake, encoding="utf-8")

TEST.write_text(r'''#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readBosstiarySource() {
		std::ifstream input(std::string(OAM030_SOURCE_DIR) + "/src/io/io_bosstiary.cpp");
		EXPECT_TRUE(input.is_open());
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}

	std::size_t countOccurrences(const std::string &text, const std::string &needle) {
		std::size_t count = 0;
		std::size_t position = 0;
		while ((position = text.find(needle, position)) != std::string::npos) {
			++count;
			position += needle.size();
		}
		return count;
	}
} // namespace

TEST(Oam030BosstiaryAdaptTest, MissingBoostedBossRowIsInitializedBeforeReroll) {
	const auto source = readBosstiarySource();
	ASSERT_FALSE(source.empty());

	EXPECT_EQ(countOccurrences(source, "if (!result)"), 1u);
	EXPECT_EQ(source.find("Failed to detect boosted boss database. (CODE 01)"), std::string::npos);
	EXPECT_NE(source.find("No boosted boss row found. A new one will be selected."), std::string::npos);
	EXPECT_NE(source.find("INSERT INTO `boosted_boss` (`boostname`, `date`, `raceid`) VALUES ('default', '0', '0')"), std::string::npos);
	EXPECT_NE(source.find("Failed to initialize the boosted boss database row. (CODE 01)"), std::string::npos);
}
''', encoding="utf-8")

DOC.write_text(r'''# OAM-030 Bosstiary Adaptation

Final disposition: `bosstiary → ADAPT`.

Immutable target base: `68d48deea999990b1eab30858f3a85fc9fef7067`.
Legacy/governance task-start baseline: `419d0848448c641561e7bc06392a4b17b95213b2`.
Fresh upstream: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`.
Maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`.

Canonical `bosstiary` owns `src/io/io_bosstiary.*` and depends on completed `cyclopedia` and `player-persistence`. Task-start Otheryn and fresh upstream shared exact `io_bosstiary.cpp` blob `8e89ce79316e5c193e918661c50278f50d476c83`.

Merged legacy PR #188 contains one isolated Bosstiary production correction. The target/upstream implementation returned immediately when the `boosted_boss` query had no row, which made its later `if (!result)` recovery branch unreachable. OAM-030 removes that early return and initializes the missing singleton row before selecting and persisting a new boosted boss.

Later legacy multichannel leader-election changes are deliberately not imported by this bounded donor. Bestiary, Charms, monster-data, protocol and maintained-client changes are also excluded.

Focused proof guards that exactly one missing-result branch remains, the stale early error path is absent, and the deterministic missing-row insert plus failure handling are present.

This package does not claim exhaustive Bosstiary parity, boosted-boss cluster-singleton correctness, boss slot persistence, point/loot arithmetic parity, schema migration correctness, packet compatibility, maintained-client rendering, physical-client Bosstiary E2E closure or full Real Tibia parity.
''', encoding="utf-8")

TASK.write_text(r'''---
task_id: OTH-20260721-oam030-bosstiary-adapt
status: implementing
branch: dudantas/oam-030-bosstiary-adapt
base_branch: main
created: 2026-07-21
updated: 2026-07-21
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/OTH-20260721-oam030-bosstiary-adapt.md
  - docs/oam-030-bosstiary-adapt.md
  - src/io/io_bosstiary.cpp
  - tests/unit/game/oam_030_bosstiary_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
required_reads:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
search_first:
  - src/io/io_bosstiary.cpp
optional_reads: []
---

# OAM-030 Bosstiary target adaptation

## Goal

Apply only the reviewed legacy PR #188 missing `boosted_boss` row initialization correction and add focused proof without importing later multichannel, Bestiary, Charms, protocol or maintained-client changes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T09:55:00+02:00
head: 68d48deea999990b1eab30858f3a85fc9fef7067
branch: dudantas/oam-030-bosstiary-adapt
pr: none
status: implementing
context_routes:
  - docs/oam-030-bosstiary-adapt.md
owned_paths:
  - docs/agents/tasks/active/OTH-20260721-oam030-bosstiary-adapt.md
  - docs/oam-030-bosstiary-adapt.md
  - src/io/io_bosstiary.cpp
  - tests/unit/game/oam_030_bosstiary_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
proven:
  - Target task-start main is 68d48deea999990b1eab30858f3a85fc9fef7067.
  - Target and fresh upstream share io_bosstiary.cpp blob 8e89ce79316e5c193e918661c50278f50d476c83.
  - Merged legacy PR 188 changes exactly one canonical bosstiary production site in IOBosstiary::loadBoostedBoss.
  - The accepted donor removes an early no-row return and initializes the missing boosted_boss row before reroll.
  - Later current-legacy multichannel leadership logic is independent and excluded.
derived:
  - OAM-030 target disposition is bosstiary ADAPT with one production recovery correction plus focused proof.
unknown:
  - Exact final target CI evidence until PR gating completes.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Copy current legacy io_bosstiary.cpp wholesale.
  - Import Bestiary Charms monster-data protocol or maintained-client changes.
changed_paths:
  - docs/agents/tasks/active/OTH-20260721-oam030-bosstiary-adapt.md
  - docs/oam-030-bosstiary-adapt.md
  - src/io/io_bosstiary.cpp
  - tests/unit/game/oam_030_bosstiary_adapt_test.cpp
  - tests/unit/game/CMakeLists.txt
validation:
  - command: exact donor and ownership preflight
    result: PASS
    evidence: PR 188 has one isolated io_bosstiary.cpp hunk applicable to exact target/upstream code
blockers: []
next_action: Materialize the bounded adaptation and focused proof, remove temporary materialization helpers, open the target PR, then require exact-head autofix CI Required Linux-debug Run Tests scope review and no-main-drift before expected-head squash merge.
```
''', encoding="utf-8")
