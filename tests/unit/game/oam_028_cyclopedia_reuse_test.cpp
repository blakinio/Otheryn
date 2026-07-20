#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM028_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

TEST(Oam028CyclopediaReuseTest, PreservesBroadUmbrellaProtocolSurface) {
	const auto protocol = readSource("src/server/network/protocol/protocolgame.hpp");
	ASSERT_FALSE(protocol.empty());

	EXPECT_NE(protocol.find("void parseCyclopediaCharacterInfo(NetworkMessage &msg);"), std::string::npos);
	EXPECT_NE(protocol.find("void parseCyclopediaMapAction(NetworkMessage &msg);"), std::string::npos);
	EXPECT_NE(protocol.find("void parseBestiarySendRaces();"), std::string::npos);
	EXPECT_NE(protocol.find("void sendBestiaryCharms();"), std::string::npos);
	EXPECT_NE(protocol.find("void sendBosstiaryData();"), std::string::npos);
	EXPECT_NE(protocol.find("void sendCyclopediaCharacterBaseInformation();"), std::string::npos);
	EXPECT_NE(protocol.find("void sendHousesInfo();"), std::string::npos);
	EXPECT_NE(protocol.find("void sendCyclopediaHouseList(HouseMap houses);"), std::string::npos);
}

TEST(Oam028CyclopediaReuseTest, PreservesIndependentTsd004ChildRoots) {
	const auto bestiary = readSource("src/io/iobestiary.hpp");
	const auto bosstiary = readSource("src/io/io_bosstiary.hpp");
	const auto character = readSource("src/creatures/players/components/player_cyclopedia.hpp");
	const auto titles = readSource("src/creatures/players/components/player_title.hpp");

	EXPECT_NE(bestiary.find("class IOBestiary"), std::string::npos);
	EXPECT_NE(bosstiary.find("class IOBosstiary"), std::string::npos);
	EXPECT_NE(character.find("class PlayerCyclopedia"), std::string::npos);
	EXPECT_NE(titles.find("class PlayerTitle"), std::string::npos);
}
