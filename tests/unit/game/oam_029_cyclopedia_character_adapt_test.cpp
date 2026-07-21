#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readPlayerCyclopediaSource() {
		std::ifstream input(std::string(OAM029_SOURCE_DIR) + "/src/creatures/players/components/player_cyclopedia.cpp");
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

TEST(Oam029CyclopediaCharacterAdaptTest, RecentPvpCountUsesSameSeventyDayWindowAsRows) {
	const auto source = readPlayerCyclopediaSource();
	ASSERT_FALSE(source.empty());

	const std::string predicate = "`time` >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 70 DAY))";
	EXPECT_EQ(countOccurrences(source, predicate), 2u);
	EXPECT_NE(source.find("(select count(*) FROM `player_deaths` WHERE ((`killed_by` = {} AND `is_player` = 1) OR (`mostdamage_by` = {} AND `mostdamage_is_player` = 1)) AND `time` >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 70 DAY))) as `entries`"), std::string::npos);
}
