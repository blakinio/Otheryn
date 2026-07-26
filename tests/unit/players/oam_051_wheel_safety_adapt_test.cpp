#include <gtest/gtest.h>

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
