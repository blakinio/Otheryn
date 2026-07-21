#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM032_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

TEST(Oam032TitlesReuseTest, PreservesIndependentTitleLifecycleSurface) {
	const auto header = readSource("src/creatures/players/components/player_title.hpp");
	ASSERT_FALSE(header.empty());

	EXPECT_NE(header.find("class PlayerTitle"), std::string::npos);
	EXPECT_NE(header.find("bool manage(bool canAdd, uint8_t id, uint32_t timestamp = 0);"), std::string::npos);
	EXPECT_NE(header.find("void remove(const Title &title);"), std::string::npos);
	EXPECT_NE(header.find("const std::vector<std::pair<Title, uint32_t>> &getUnlockedTitles();"), std::string::npos);
	EXPECT_NE(header.find("[[nodiscard]] uint8_t getCurrentTitle() const;"), std::string::npos);
	EXPECT_NE(header.find("void setCurrentTitle(uint8_t id) const;"), std::string::npos);
	EXPECT_NE(header.find("void loadUnlockedTitles();"), std::string::npos);
}

TEST(Oam032TitlesReuseTest, PreservesScopedKvAndCurrentTitleUnlockGate) {
	const auto source = readSource("src/creatures/players/components/player_title.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("m_player.kv()->scoped(\"titles\")->get(\"current-title\")"), std::string::npos);
	EXPECT_NE(source.find("m_player.kv()->scoped(\"titles\")->set(\"current-title\", id != 0 && isTitleUnlocked(id) ? id : 0);"), std::string::npos);
	EXPECT_NE(source.find("m_player.kv()->scoped(\"titles\")->scoped(\"unlocked\")"), std::string::npos);
}
