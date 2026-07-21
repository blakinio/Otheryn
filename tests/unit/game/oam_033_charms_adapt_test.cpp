#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM033_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

TEST(Oam033CharmsAdaptTest, CategoryRegistrationUsesCategoryPresence) {
	const auto source = readSource("data/scripts/lib/register_bestiary_charm.lua");
	ASSERT_FALSE(source.empty());

	const auto categoryBlock = source.find("registerCharm.category = function(charm, mask)");
	ASSERT_NE(categoryBlock, std::string::npos);
	const auto typeBlock = source.find("registerCharm.type = function(charm, mask)", categoryBlock);
	ASSERT_NE(typeBlock, std::string::npos);
	const auto block = source.substr(categoryBlock, typeBlock - categoryBlock);

	EXPECT_NE(block.find("if mask.category then"), std::string::npos);
	EXPECT_EQ(block.find("if mask.type then"), std::string::npos);
	EXPECT_NE(block.find("charm:category(mask.category)"), std::string::npos);
}

TEST(Oam033CharmsAdaptTest, ResetAllCharmPriceChargesOnlyLevelsAboveOneHundred) {
	const auto source = readSource("src/io/iobestiary.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("100000 + (playerLevel > 100 ? (playerLevel - 100) * 11000 : 0)"), std::string::npos);
	EXPECT_EQ(source.find("100000 + (playerLevel > 100 ? playerLevel * 11000 : 0)"), std::string::npos);
}
