#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readBestiarySource() {
		std::ifstream input(std::string(OAM031_SOURCE_DIR) + "/src/io/iobestiary.cpp");
		EXPECT_TRUE(input.is_open());
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}

	std::string functionSlice(const std::string &source, const std::string &startMarker, const std::string &endMarker) {
		const auto start = source.find(startMarker);
		EXPECT_NE(start, std::string::npos);
		if (start == std::string::npos) {
			return {};
		}
		const auto end = source.find(endMarker, start);
		EXPECT_NE(end, std::string::npos);
		if (end == std::string::npos) {
			return {};
		}
		return source.substr(start, end - start);
	}
} // namespace

TEST(Oam031BestiaryAdaptTest, KillAttributionChecksPointersBeforeMonsterTypeDereference) {
	const auto source = readBestiarySource();
	ASSERT_FALSE(source.empty());

	const auto function = functionSlice(source, "void IOBestiary::addBestiaryKill", "PlayerCharmsByMonster IOBestiary::getCharmFromTarget");
	ASSERT_FALSE(function.empty());

	const auto guard = function.find("if (!player || !mtype)");
	const auto dereference = function.find("mtype->info.raceid");
	ASSERT_NE(guard, std::string::npos);
	ASSERT_NE(dereference, std::string::npos);
	EXPECT_LT(guard, dereference);
	EXPECT_EQ(function.find("uint16_t raceid = mtype->info.raceid;\n\tif (raceid == 0 || !player || !mtype)"), std::string::npos);
}

TEST(Oam031BestiaryAdaptTest, DifficultyCalculationPreservesFractionalThresholds) {
	const auto source = readBestiarySource();
	ASSERT_FALSE(source.empty());

	const auto function = functionSlice(source, "int8_t IOBestiary::calculateDifficult", "return 0;\n}");
	ASSERT_FALSE(function.empty());

	EXPECT_NE(function.find("const double chanceInPercent = static_cast<double>(chance) / 1000.0;"), std::string::npos);
	EXPECT_EQ(function.find("float chanceInPercent = chance / 1000;"), std::string::npos);
}

TEST(Oam031BestiaryAdaptTest, CharmResetPricingRemainsOutsideBestiaryPackage) {
	const auto source = readBestiarySource();
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("100000 + (playerLevel > 100 ? playerLevel * 11000 : 0)"), std::string::npos);
	EXPECT_EQ(source.find("100000 + (playerLevel > 100 ? (playerLevel - 100) * 11000 : 0)"), std::string::npos);
}
