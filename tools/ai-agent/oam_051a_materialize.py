#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

DONOR_COMMIT = "35ff51ac022e36d215db9d0fa86053b326a0bdf0"
DONOR_URL = "https://github.com/blakinio/canary.git"
SELECTED_DONOR_PATHS = [
    "src/creatures/players/components/wheel/player_wheel.cpp",
    "src/creatures/players/components/wheel/player_wheel.hpp",
    "src/creatures/players/components/wheel/wheel_gems.cpp",
    "src/creatures/players/components/wheel/wheel_gems.hpp",
    "src/io/functions/iologindata_load_player.cpp",
]


def run(*args: str, capture: bool = False) -> str:
    result = subprocess.run(
        list(args),
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return result.stdout.strip() if capture else ""


def replace_once(path: str, old: str, new: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one replacement anchor, found {count}")
    file_path.write_text(text.replace(old, new, 1), encoding="utf-8")


def remove_once(path: str, block: str) -> None:
    replace_once(path, block, "")


run("git", "fetch", "--no-tags", "--depth=2", DONOR_URL, DONOR_COMMIT)
donor = run("git", "rev-parse", "FETCH_HEAD", capture=True)
parent = run("git", "rev-parse", f"{donor}^", capture=True)
patch_path = Path("/tmp/oam-051a-selected.patch")
patch = subprocess.run(
    ["git", "diff", "--binary", parent, donor, "--", *SELECTED_DONOR_PATHS],
    check=True,
    stdout=subprocess.PIPE,
).stdout
patch_path.write_bytes(patch)
run("git", "apply", "--3way", str(patch_path))

player_cpp = "src/creatures/players/components/wheel/player_wheel.cpp"
player_hpp = "src/creatures/players/components/wheel/player_wheel.hpp"
gems_cpp = "src/creatures/players/components/wheel/wheel_gems.cpp"
gems_hpp = "src/creatures/players/components/wheel/wheel_gems.hpp"
protocol_cpp = "src/server/network/protocol/protocolgame.cpp"
players_cmake = "tests/unit/players/CMakeLists.txt"
test_cpp = "tests/unit/players/oam_051_wheel_safety_adapt_test.cpp"

# Keep safety/state hardening but restore all parity-sensitive values and effects.
replace_once(
    player_cpp,
    "\t\tcase 2:\n\t\t\treturn std::make_tuple(12500000, 15);",
    "\t\tcase 2:\n\t\t\treturn std::make_tuple(12000000, 15);",
)

remove_once(
    player_cpp,
    """\n\t\tconst uint8_t fullResonanceBonus = WheelGemUtils::getFullResonanceBonus(quality, resonanceCount);
\t\tm_playerBonusData.stats.damage += fullResonanceBonus;
\t\tm_playerBonusData.stats.healing += fullResonanceBonus;""",
)

replace_once(
    player_cpp,
    """\t\tfor (uint8_t i = 0; i < stageValue; ++i) {
\t\t\taddSpellToVector("Drain_Body_Spells");
\t\t}""",
    """\t\tfor (uint8_t i = 0; i <= stageValue; ++i) {
\t\t\taddSpellToVector("Drain_Body_Spells");
\t\t}""",
)
replace_once(
    player_cpp,
    """\t\tfor (uint8_t i = 0; i < stageValue; ++i) {
\t\t\taddSpellToVector("Divine Empowerment");
\t\t}""",
    """\t\tfor (uint8_t i = 0; i <= stageValue; ++i) {
\t\t\taddSpellToVector("Divine Empowerment");
\t\t}""",
)
replace_once(
    player_cpp,
    """\tconstexpr uint16_t newHolyBonus = WheelBalance::BALLISTIC_PIERCE_PERCENT;
\tconstexpr uint16_t newPhysicalBonus = WheelBalance::BALLISTIC_PIERCE_PERCENT;""",
    """\tconstexpr uint16_t newHolyBonus = 2; // 2%
\tconstexpr uint16_t newPhysicalBonus = 2; // 2%""",
)
remove_once(
    player_cpp,
    """\tconst int32_t mana = (m_player.getMaxMana() * getGiftOfLifeValue()) / 100;
\tm_player.changeMana(mana);
""",
)

replace_once(
    player_cpp,
    """double PlayerWheel::checkBlessingGroveHealingByTarget(const std::shared_ptr<Creature> &target) const {
\tif (!target || target == m_player.getPlayer()) {
\t\treturn 0;
\t}

\tconst uint8_t stage = getStage(WheelStage_t::BLESSING_OF_THE_GROVE);
\tif (stage == 0 || stage > WheelBalance::BLESSING_GROVE_HEALING_PERCENT.size()) {
\t\treturn 0;
\t}

\tconst double healthPercent = (static_cast<double>(target->getHealth()) * 100.0) / static_cast<double>(target->getMaxHealth());
\tif (healthPercent > 60.0) {
\t\treturn 0;
\t}

\tdouble healingBonus = WheelBalance::BLESSING_GROVE_HEALING_PERCENT[stage - 1];
\tif (healthPercent <= 30.0) {
\t\thealingBonus *= 2.0;
\t}

\treturn healingBonus;
}""",
    """int32_t PlayerWheel::checkBlessingGroveHealingByTarget(const std::shared_ptr<Creature> &target) const {
\tif (!target || target == m_player.getPlayer()) {
\t\treturn 0;
\t}

\tint32_t healingBonus = 0;
\tconst uint8_t stage = getStage(WheelStage_t::BLESSING_OF_THE_GROVE);
\tconst int32_t healthPercent = std::round((static_cast<double>(target->getHealth()) * 100) / static_cast<double>(target->getMaxHealth()));
\tif (healthPercent <= 30) {
\t\tif (stage >= 3) {
\t\t\thealingBonus = 24;
\t\t} else if (stage >= 2) {
\t\t\thealingBonus = 18;
\t\t} else if (stage >= 1) {
\t\t\thealingBonus = 12;
\t\t}
\t} else if (healthPercent <= 60) {
\t\tif (stage >= 3) {
\t\t\thealingBonus = 12;
\t\t} else if (stage >= 2) {
\t\t\thealingBonus = 9;
\t\t} else if (stage >= 1) {
\t\t\thealingBonus = 6;
\t\t}
\t}

\treturn healingBonus;
}""",
)

replace_once(
    player_cpp,
    """int32_t PlayerWheel::checkAvatarSkill(WheelAvatarSkill_t skill) const {""",
    """int32_t PlayerWheel::checkBattleHealingAmount() const {
\tdouble amount = static_cast<double>(m_player.getSkillLevel(SKILL_SHIELD)) * 0.2;
\tconst uint8_t healthPercent = (m_player.getHealth() * 100) / m_player.getMaxHealth();
\tif (healthPercent <= 30) {
\t\tamount *= 3;
\t} else if (healthPercent <= 60) {
\t\tamount *= 2;
\t}
\treturn static_cast<int32_t>(amount);
}

int32_t PlayerWheel::checkAvatarSkill(WheelAvatarSkill_t skill) const {""",
)

remove_once(
    player_cpp,
    """\t\tif (damage.primary.type == COMBAT_HEALING && getInstant("Battle Healing")) {
\t\t\tstd::shared_ptr<Item> shield;
\t\t\tstd::shared_ptr<Item> weapon;
\t\t\tm_player.getShieldAndWeapon(shield, weapon);
\t\t\tdamage.healingMultiplier += shield ? 30 : 10;
\t\t}
""",
)
replace_once(
    player_cpp,
    """\t\tif (getHealingLinkUpgrade(spellName)) {
\t\t\tdamage.healingLink += WheelBalance::HEALING_LINK_PERCENT;
\t\t}""",
    """\t\tif (getHealingLinkUpgrade(spellName)) {
\t\t\tdamage.healingLink += 10;
\t\t}""",
)
replace_once(
    player_cpp,
    """void PlayerWheel::adjustDamageBasedOnResistanceAndSkill(int32_t &damage, CombatType_t combatType) const {""",
    """void PlayerWheel::healIfBattleHealingActive() const {
\tif (getInstant("Battle Healing")) {
\t\tCombatDamage damage;
\t\tdamage.primary.value = checkBattleHealingAmount();
\t\tdamage.primary.type = COMBAT_HEALING;
\t\tg_game().combatChangeHealth(m_player.getPlayer(), m_player.getPlayer(), damage);
\t}
}

void PlayerWheel::adjustDamageBasedOnResistanceAndSkill(int32_t &damage, CombatType_t combatType) const {""",
)

replace_once(
    player_hpp,
    """\tint32_t checkBeamMasteryDamage() const;
\tdouble checkBlessingGroveHealingByTarget(const std::shared_ptr<Creature> &target) const;""",
    """\tint32_t checkBeamMasteryDamage() const;
\tint32_t checkBattleHealingAmount() const;
\tint32_t checkBlessingGroveHealingByTarget(const std::shared_ptr<Creature> &target) const;""",
)
replace_once(
    player_hpp,
    """\tuint8_t getBeamAffectedTotal(const CombatDamage &tmpDamage) const;
\tvoid updateBeamMasteryDamage(CombatDamage &tmpDamage, uint8_t &beamAffectedTotal, uint8_t &beamAffectedCurrent) const;
\t/**
\t * @brief Adjusts the incoming damage based on the player's resistance and avatar skill.""",
    """\tuint8_t getBeamAffectedTotal(const CombatDamage &tmpDamage) const;
\tvoid updateBeamMasteryDamage(CombatDamage &tmpDamage, uint8_t &beamAffectedTotal, uint8_t &beamAffectedCurrent) const;
\t/**
\t * @brief Checks if the player has the "Battle Healing" instant active and, if so, heals the player.
\t *
\t * This function checks if a creature is a player and if the player is not removed from the game world.
\t * If the player has the "Battle Healing" instant active, the player is healed by an amount defined by the
\t * checkBattleHealingAmount() function.
\t *
\t * @param creature The creature to check and potentially heal.
\t */
\tvoid healIfBattleHealingActive() const;
\t/**
\t * @brief Adjusts the incoming damage based on the player's resistance and avatar skill.""",
)

remove_once(
    gems_cpp,
    """uint8_t WheelGemUtils::getFullResonanceBonus(WheelGemQuality_t quality, uint16_t resonanceCount) {
\tswitch (quality) {
\t\tcase WheelGemQuality_t::Lesser:
\t\t\treturn resonanceCount >= 1 ? 1 : 0;
\t\tcase WheelGemQuality_t::Regular:
\t\t\treturn resonanceCount >= 2 ? 1 : 0;
\t\tcase WheelGemQuality_t::Greater:
\t\t\treturn resonanceCount >= 3 ? 2 : 0;
\t\tdefault:
\t\t\treturn 0;
\t}
}

""",
)
replace_once(
    gems_cpp,
    "WheelBalance::GEM_MITIGATION_BASE * gradeMultiplier",
    "500 * gradeMultiplier",
)
remove_once(
    gems_hpp,
    "\tstatic uint8_t getFullResonanceBonus(WheelGemQuality_t quality, uint16_t resonanceCount);\n",
)

# Rebase the current-protocol parser onto Otheryn's protocol-profile structure.
replace_once(
    protocol_cpp,
    """\t\tconst auto action = static_cast<WheelGemAction_t>(msg.getByte());
\t\tswitch (action) {
\t\t\tcase WheelGemAction_t::Destroy:
\t\t\t\tplayer->wheel().destroyGem(msg.get<uint16_t>());
\t\t\t\tbreak;
\t\t\tcase WheelGemAction_t::Reveal:
\t\t\t\tplayer->wheel().revealGem(static_cast<WheelGemQuality_t>(msg.getByte(true)));
\t\t\t\tbreak;
\t\t\tcase WheelGemAction_t::SwitchDomain:
\t\t\t\tplayer->wheel().switchGemDomain(msg.get<uint16_t>());
\t\t\t\tbreak;
\t\t\tcase WheelGemAction_t::ToggleLock:
\t\t\t\tplayer->wheel().toggleGemLock(msg.get<uint16_t>());
\t\t\t\tbreak;
\t\t\tcase WheelGemAction_t::ImproveGrade: {
\t\t\t\tconst auto fragmentType = static_cast<WheelFragmentType_t>(msg.getByte(true) != 0 ? 1 : 0);
\t\t\t\tconst auto position = msg.getByte(true);
\t\t\t\tplayer->wheel().improveGemGrade(fragmentType, position);
\t\t\t\tbreak;
\t\t\t}
\t\t\tdefault:
\t\t\t\tg_logger().error("[{}] player {} is trying to do invalid action {} on wheel", __FUNCTION__, player->getName(), fmt::underlying(action));
\t\t\t\tbreak;
\t\t}""",
    """\t\tif (!msg.canRead(1)) {
\t\t\tg_logger().warn("[{}] Player {} sent a truncated Wheel gem action", __FUNCTION__, player->getName());
\t\t\treturn;
\t\t}

\t\tconst auto action = static_cast<WheelGemAction_t>(msg.getByte());
\t\tswitch (action) {
\t\t\tcase WheelGemAction_t::Destroy:
\t\t\tcase WheelGemAction_t::SwitchDomain:
\t\t\tcase WheelGemAction_t::ToggleLock: {
\t\t\t\tif (!msg.canRead(sizeof(uint16_t))) {
\t\t\t\t\tg_logger().warn("[{}] Player {} sent a truncated Wheel gem index for action {}", __FUNCTION__, player->getName(), fmt::underlying(action));
\t\t\t\t\treturn;
\t\t\t\t}
\t\t\t\tconst auto index = msg.get<uint16_t>();
\t\t\t\tif (action == WheelGemAction_t::Destroy) {
\t\t\t\t\tplayer->wheel().destroyGem(index);
\t\t\t\t} else if (action == WheelGemAction_t::SwitchDomain) {
\t\t\t\t\tplayer->wheel().switchGemDomain(index);
\t\t\t\t} else {
\t\t\t\t\tplayer->wheel().toggleGemLock(index);
\t\t\t\t}
\t\t\t\tbreak;
\t\t\t}
\t\t\tcase WheelGemAction_t::Reveal: {
\t\t\t\tif (!msg.canRead(1)) {
\t\t\t\t\tg_logger().warn("[{}] Player {} sent a truncated Wheel gem quality", __FUNCTION__, player->getName());
\t\t\t\t\treturn;
\t\t\t\t}
\t\t\t\tconst auto quality = msg.getByte(true);
\t\t\t\tif (quality > fmt::underlying(WheelGemQuality_t::Greater)) {
\t\t\t\t\tg_logger().warn("[{}] Player {} sent invalid Wheel gem quality {}", __FUNCTION__, player->getName(), quality);
\t\t\t\t\treturn;
\t\t\t\t}
\t\t\t\tplayer->wheel().revealGem(static_cast<WheelGemQuality_t>(quality));
\t\t\t\tbreak;
\t\t\t}
\t\t\tcase WheelGemAction_t::ImproveGrade: {
\t\t\t\tif (!msg.canRead(2)) {
\t\t\t\t\tg_logger().warn("[{}] Player {} sent a truncated Wheel grade action", __FUNCTION__, player->getName());
\t\t\t\t\treturn;
\t\t\t\t}
\t\t\t\tconst auto fragmentType = msg.getByte(true);
\t\t\t\tconst auto position = msg.getByte(true);
\t\t\t\tif (fragmentType > fmt::underlying(WheelFragmentType_t::Lesser)) {
\t\t\t\t\tg_logger().warn("[{}] Player {} sent invalid Wheel fragment type {}", __FUNCTION__, player->getName(), fragmentType);
\t\t\t\t\treturn;
\t\t\t\t}
\t\t\t\tplayer->wheel().improveGemGrade(static_cast<WheelFragmentType_t>(fragmentType), position);
\t\t\t\tbreak;
\t\t\t}
\t\t\tdefault:
\t\t\t\tg_logger().error("[{}] player {} is trying to do invalid action {} on wheel", __FUNCTION__, player->getName(), fmt::underlying(action));
\t\t\t\treturn;
\t\t}""",
)

# Register one bounded target test without replacing target-specific manifests.
replace_once(
    players_cmake,
    """target_sources(
    canary_ut
    PRIVATE character_progression_test.cpp""",
    """target_compile_definitions(
    canary_ut
    PRIVATE OAM051_SOURCE_DIR="${PROJECT_SOURCE_DIR}"
)

target_sources(
    canary_ut
    PRIVATE character_progression_test.cpp""",
)
replace_once(
    players_cmake,
    """            oam_020_exaltation_forge_adapt_test.cpp
            party_test.cpp""",
    """            oam_020_exaltation_forge_adapt_test.cpp
            oam_051_wheel_safety_adapt_test.cpp
            party_test.cpp""",
)

Path(test_cpp).write_text(
    r"""#include <gtest/gtest.h>

#include <array>
#include <fstream>
#include <sstream>
#include <string>

#include "creatures/players/components/wheel/wheel_gems.hpp"
#include "creatures/players/player.hpp"
#include "enums/player_wheel.hpp"
#include "lib/di/container.hpp"
#include "lib/logging/in_memory_logger.hpp"

namespace {
\tstd::string readSource(const std::string &relativePath) {
\t\tstd::ifstream input(std::string(OAM051_SOURCE_DIR) + "/" + relativePath);
\t\tEXPECT_TRUE(input.is_open()) << relativePath;
\t\tstd::ostringstream buffer;
\t\tbuffer << input.rdbuf();
\t\treturn buffer.str();
\t}
} // namespace

class Oam051WheelSafetyAdaptTest : public ::testing::Test {
protected:
\tstatic void SetUpTestSuite() {
\t\tpreviousTestContainer = DI::getTestContainer();
\t\tInMemoryLogger::install(injector);
\t\tDI::setTestContainer(&injector);
\t}

\tstatic void TearDownTestSuite() {
\t\tDI::setTestContainer(previousTestContainer);
\t}

\tstatic std::shared_ptr<Player> makePlayer(uint32_t level) {
\t\tauto player = std::make_shared<Player>();
\t\tplayer->setLevel(level);
\t\treturn player;
\t}

\tinline static di::extension::injector<> injector {};
\tinline static di::extension::injector<>* previousTestContainer = nullptr;
};

TEST_F(Oam051WheelSafetyAdaptTest, LevelPointsStartAfterLevelFifty) {
\tEXPECT_EQ(0, makePlayer(1)->wheel().getWheelPoints());
\tEXPECT_EQ(0, makePlayer(50)->wheel().getWheelPoints());
\tEXPECT_EQ(1, makePlayer(51)->wheel().getWheelPoints());
\tEXPECT_EQ(50, makePlayer(100)->wheel().getWheelPoints());
}

TEST_F(Oam051WheelSafetyAdaptTest, OverspentStateSaturatesInsteadOfUnderflowing) {
\tauto player = makePlayer(51);
\tplayer->wheel().setPointsBySlotType(static_cast<uint8_t>(WheelSlots_t::SLOT_GREEN_50), 50);
\tEXPECT_EQ(0, player->wheel().getUnusedPoints());
}

TEST_F(Oam051WheelSafetyAdaptTest, GemGradesRespectPrecedingSlotLimits) {
\tEXPECT_EQ((std::array<uint8_t, 3> { 3, 0, 0 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Lesser, 3, 3, 3));
\tEXPECT_EQ((std::array<uint8_t, 3> { 1, 1, 0 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Regular, 1, 3, 3));
\tEXPECT_EQ((std::array<uint8_t, 3> { 3, 2, 2 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Greater, 3, 2, 3));
\tEXPECT_EQ((std::array<uint8_t, 3> { 0, 0, 0 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Greater, 0, 3, 3));
}

TEST_F(Oam051WheelSafetyAdaptTest, AllocationAndGemMutationPathsAreFailClosed) {
\tconst auto source = readSource("src/creatures/players/components/wheel/player_wheel.cpp");
\tASSERT_FALSE(source.empty());

\tEXPECT_NE(source.find("bool PlayerWheel::validateSlotAllocation"), std::string::npos);
\tEXPECT_NE(source.find("decreasesPoints && getOptions(m_player.getID()) != 1"), std::string::npos);
\tEXPECT_NE(source.find("MAX_REVEALED_WHEEL_GEMS = 225"), std::string::npos);
\tEXPECT_NE(source.find("isValidModifierPosition(fragmentType, pos)"), std::string::npos);
\tEXPECT_NE(source.find("Ignoring malformed Wheel blob"), std::string::npos);
\tEXPECT_NE(source.find("m_activeGems.fill(emptyGem)"), std::string::npos);
}

TEST_F(Oam051WheelSafetyAdaptTest, CurrentProtocolParserRejectsTruncatedAndInvalidActions) {
\tconst auto source = readSource("src/server/network/protocol/protocolgame.cpp");
\tASSERT_FALSE(source.empty());

\tconst auto functionStart = source.find("void ProtocolGame::parseWheelGemAction");
\tASSERT_NE(functionStart, std::string::npos);
\tconst auto functionEnd = source.find("void ProtocolGame::sendOpenWheelWindow", functionStart);
\tASSERT_NE(functionEnd, std::string::npos);
\tconst auto function = source.substr(functionStart, functionEnd - functionStart);

\tEXPECT_NE(function.find("if (!msg.canRead(1))"), std::string::npos);
\tEXPECT_NE(function.find("if (!msg.canRead(sizeof(uint16_t)))"), std::string::npos);
\tEXPECT_NE(function.find("if (!msg.canRead(2))"), std::string::npos);
\tEXPECT_NE(function.find("quality > fmt::underlying(WheelGemQuality_t::Greater)"), std::string::npos);
\tEXPECT_NE(function.find("fragmentType > fmt::underlying(WheelFragmentType_t::Lesser)"), std::string::npos);
}

TEST_F(Oam051WheelSafetyAdaptTest, PermanentPointSourcesLoadBeforeAllocationValidation) {
\tconst auto source = readSource("src/io/functions/iologindata_load_player.cpp");
\tASSERT_FALSE(source.empty());

\tconst auto grades = source.find("player->wheel().loadKVModGrades();");
\tconst auto scrolls = source.find("player->wheel().loadKVScrolls();");
\tconst auto slots = source.find("player->wheel().loadDBPlayerSlotPointsOnLogin();");
\tASSERT_NE(grades, std::string::npos);
\tASSERT_NE(scrolls, std::string::npos);
\tASSERT_NE(slots, std::string::npos);
\tEXPECT_LT(grades, slots);
\tEXPECT_LT(scrolls, slots);
}

TEST_F(Oam051WheelSafetyAdaptTest, ParitySensitiveEffectsRemainOutsideThisPackage) {
\tconst auto wheel = readSource("src/creatures/players/components/wheel/player_wheel.cpp");
\tconst auto gems = readSource("src/creatures/players/components/wheel/wheel_gems.cpp");
\tASSERT_FALSE(wheel.empty());
\tASSERT_FALSE(gems.empty());

\tEXPECT_EQ(wheel.find("WheelBalance::"), std::string::npos);
\tEXPECT_EQ(wheel.find("getFullResonanceBonus"), std::string::npos);
\tEXPECT_EQ(gems.find("WheelBalance::"), std::string::npos);
\tEXPECT_EQ(gems.find("getFullResonanceBonus"), std::string::npos);
\tEXPECT_NE(wheel.find("return std::make_tuple(12000000, 15);"), std::string::npos);
}
""",
    encoding="utf-8",
)

for forbidden_path in [
    "data/scripts/spells/attack/flurry_of_blows.lua",
    "data/scripts/spells/attack/front_sweep.lua",
    "src/creatures/monsters/monster.cpp",
    "src/creatures/players/components/wheel/wheel_definitions.hpp",
    "src/game/game.cpp",
    "src/io/io_wheel.cpp",
]:
    if run("git", "diff", "--name-only", "--", forbidden_path, capture=True):
        raise RuntimeError(f"out-of-scope path changed: {forbidden_path}")

for path in [player_cpp, gems_cpp]:
    text = Path(path).read_text(encoding="utf-8")
    if "WheelBalance::" in text or "getFullResonanceBonus" in text:
        raise RuntimeError(f"parity-sensitive code leaked into {path}")

run("git", "diff", "--check")
