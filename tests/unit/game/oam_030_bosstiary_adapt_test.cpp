#include <gtest/gtest.h>

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
