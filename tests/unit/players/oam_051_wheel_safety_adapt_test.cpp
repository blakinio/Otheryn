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
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM051_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

class Oam051WheelSafetyAdaptTest : public ::testing::Test {
protected:
	static void SetUpTestSuite() {
		previousTestContainer = DI::getTestContainer();
		InMemoryLogger::install(injector);
		DI::setTestContainer(&injector);
	}

	static void TearDownTestSuite() {
		DI::setTestContainer(previousTestContainer);
	}

	static std::shared_ptr<Player> makePlayer(uint32_t level) {
		auto player = std::make_shared<Player>();
		player->setLevel(level);
		return player;
	}

	inline static di::extension::injector<> injector {};
	inline static di::extension::injector<>* previousTestContainer = nullptr;
};

TEST_F(Oam051WheelSafetyAdaptTest, LevelPointsStartAfterLevelFifty) {
	EXPECT_EQ(0, makePlayer(1)->wheel().getWheelPoints());
	EXPECT_EQ(0, makePlayer(50)->wheel().getWheelPoints());
	EXPECT_EQ(1, makePlayer(51)->wheel().getWheelPoints());
	EXPECT_EQ(50, makePlayer(100)->wheel().getWheelPoints());
}

TEST_F(Oam051WheelSafetyAdaptTest, OverspentStateSaturatesInsteadOfUnderflowing) {
	auto player = makePlayer(51);
	player->wheel().setPointsBySlotType(static_cast<uint8_t>(WheelSlots_t::SLOT_GREEN_50), 50);
	EXPECT_EQ(0, player->wheel().getUnusedPoints());
}

TEST_F(Oam051WheelSafetyAdaptTest, GemGradesRespectPrecedingSlotLimits) {
	EXPECT_EQ((std::array<uint8_t, 3> { 3, 0, 0 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Lesser, 3, 3, 3));
	EXPECT_EQ((std::array<uint8_t, 3> { 1, 1, 0 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Regular, 1, 3, 3));
	EXPECT_EQ((std::array<uint8_t, 3> { 3, 2, 2 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Greater, 3, 2, 3));
	EXPECT_EQ((std::array<uint8_t, 3> { 0, 0, 0 }), WheelGemUtils::getEffectiveGrades(WheelGemQuality_t::Greater, 0, 3, 3));
}

TEST_F(Oam051WheelSafetyAdaptTest, AllocationAndGemMutationPathsAreFailClosed) {
	const auto source = readSource("src/creatures/players/components/wheel/player_wheel.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("bool PlayerWheel::validateSlotAllocation"), std::string::npos);
	EXPECT_NE(source.find("decreasesPoints && getOptions(m_player.getID()) != 1"), std::string::npos);
	EXPECT_NE(source.find("MAX_REVEALED_WHEEL_GEMS = 225"), std::string::npos);
	EXPECT_NE(source.find("isValidModifierPosition(fragmentType, pos)"), std::string::npos);
	EXPECT_NE(source.find("Ignoring malformed Wheel blob"), std::string::npos);
	EXPECT_NE(source.find("m_activeGems.fill(emptyGem)"), std::string::npos);
}

TEST_F(Oam051WheelSafetyAdaptTest, CurrentProtocolParserRejectsTruncatedAndInvalidActions) {
	const auto source = readSource("src/server/network/protocol/protocolgame.cpp");
	ASSERT_FALSE(source.empty());

	const auto functionStart = source.find("void ProtocolGame::parseWheelGemAction");
	ASSERT_NE(functionStart, std::string::npos);
	const auto functionEnd = source.find("void ProtocolGame::sendOpenWheelWindow", functionStart);
	ASSERT_NE(functionEnd, std::string::npos);
	const auto function = source.substr(functionStart, functionEnd - functionStart);

	EXPECT_NE(function.find("if (!msg.canRead(1))"), std::string::npos);
	EXPECT_NE(function.find("if (!msg.canRead(sizeof(uint16_t)))"), std::string::npos);
	EXPECT_NE(function.find("if (!msg.canRead(2))"), std::string::npos);
	EXPECT_NE(function.find("quality > fmt::underlying(WheelGemQuality_t::Greater)"), std::string::npos);
	EXPECT_NE(function.find("fragmentType > fmt::underlying(WheelFragmentType_t::Lesser)"), std::string::npos);
}

TEST_F(Oam051WheelSafetyAdaptTest, PermanentPointSourcesLoadBeforeAllocationValidation) {
	const auto source = readSource("src/io/functions/iologindata_load_player.cpp");
	ASSERT_FALSE(source.empty());

	const auto grades = source.find("player->wheel().loadKVModGrades();");
	const auto scrolls = source.find("player->wheel().loadKVScrolls();");
	const auto slots = source.find("player->wheel().loadDBPlayerSlotPointsOnLogin();");
	ASSERT_NE(grades, std::string::npos);
	ASSERT_NE(scrolls, std::string::npos);
	ASSERT_NE(slots, std::string::npos);
	EXPECT_LT(grades, slots);
	EXPECT_LT(scrolls, slots);
}

TEST_F(Oam051WheelSafetyAdaptTest, ParitySensitiveEffectsRemainOutsideThisPackage) {
	const auto wheel = readSource("src/creatures/players/components/wheel/player_wheel.cpp");
	const auto gems = readSource("src/creatures/players/components/wheel/wheel_gems.cpp");
	ASSERT_FALSE(wheel.empty());
	ASSERT_FALSE(gems.empty());

	EXPECT_EQ(wheel.find("WheelBalance::"), std::string::npos);
	EXPECT_EQ(wheel.find("getFullResonanceBonus"), std::string::npos);
	EXPECT_EQ(gems.find("WheelBalance::"), std::string::npos);
	EXPECT_EQ(gems.find("getFullResonanceBonus"), std::string::npos);
	EXPECT_NE(wheel.find("return std::make_tuple(12000000, 15);"), std::string::npos);
}
