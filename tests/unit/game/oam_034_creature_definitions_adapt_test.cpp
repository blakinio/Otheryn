#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM034_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}

	void expectContains(const std::string &source, const std::string &needle) {
		EXPECT_NE(source.find(needle), std::string::npos) << needle;
	}

	void expectNotContains(const std::string &source, const std::string &needle) {
		EXPECT_EQ(source.find(needle), std::string::npos) << needle;
	}
} // namespace

TEST(Oam034CreatureDefinitionsAdaptTest, BestiaryRaceMetadataMatchesReviewedDefinitions) {
	const auto agresticChicken = readSource("data-otservbr-global/monster/birds/agrestic_chicken.lua");
	const auto terrifiedElephant = readSource("data-otservbr-global/monster/mammals/terrified_elephant.lua");
	const auto hauntedDragon = readSource("data-otservbr-global/monster/quests/the_first_dragon/haunted_dragon.lua");
	const auto cryptWarrior = readSource("data-otservbr-global/monster/undeads/crypt_warrior.lua");

	expectContains(agresticChicken, "race = BESTY_RACE_BIRD");
	expectContains(terrifiedElephant, "race = BESTY_RACE_MAMMAL");
	expectContains(hauntedDragon, "race = BESTY_RACE_DRAGON");
	expectContains(cryptWarrior, "monster.raceId = 1995");
	expectContains(cryptWarrior, "race = BESTY_RACE_UNDEAD");
}

TEST(Oam034CreatureDefinitionsAdaptTest, ReviewedSharedFormIdsDoNotCollideWithOtherCreatures) {
	const auto monkApparition = readSource("data-otservbr-global/monster/quests/soul_war/normal_monsters/monk's_apparition.lua");
	const auto eradicator = readSource("data-otservbr-global/monster/quests/heart_of_destruction/eradicator2.lua");

	expectContains(monkApparition, "monster.raceId = 2636");
	expectNotContains(monkApparition, "monster.raceId = 1946");
	expectContains(eradicator, "bossRaceId = 1226");
	expectNotContains(eradicator, "bossRaceId = 1225");
}
