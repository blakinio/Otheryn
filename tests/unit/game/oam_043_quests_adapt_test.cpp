#include <gtest/gtest.h>

#include <filesystem>
#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM043_SOURCE_DIR) + "/" + relativePath);
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

	std::size_t countQuestFiles() {
		namespace fs = std::filesystem;
		const fs::path root(OAM043_SOURCE_DIR);
		const fs::path questRoots[] = {
			root / "data-otservbr-global/scripts/quests",
			root / "data/scripts/quests",
		};
		std::size_t count = 0;
		for (const auto &questRoot : questRoots) {
			if (!fs::exists(questRoot)) {
				continue;
			}
			for (const auto &entry : fs::recursive_directory_iterator(questRoot)) {
				if (entry.is_regular_file()) {
					++count;
				}
			}
		}
		return count;
	}
} // namespace

TEST(Oam043QuestsAdaptTest, RepairsConcreteQuestSourceDefects) {
	const auto hero = readSource("data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua");
	expectContains(hero, "player:addAchievement(\"The Professor's Nut\")");
	expectNotContains(hero, "player:addAchievement(\"The Professors Nut\")");

	const auto soulpit = readSource("data-otservbr-global/scripts/quests/soulpit/soulpit_fight.lua");
	expectContains(soulpit, "player:sendTextMessage(MESSAGE_EVENT_ADVANCE, \"Someone is fighting in the soulpit!\")");
	expectNotContains(soulpit, "creature:sendTextMessage(MESSAGE_EVENT_ADVANCE, \"Someone is fighting in the soulpit!\")");
	expectNotContains(soulpit, "function encounter:countMonsters()");

	const auto encounters = readSource("data/libs/systems/encounters.lua");
	expectContains(encounters, "function Encounter:countMonsters(name)");
	expectContains(encounters, "return self:getZone():countMonsters(name)");

	const auto oasis = readSource("data-otservbr-global/scripts/quests/the_ancient_tombs/actions_oasis_lever_door.lua");
	expectContains(oasis, "local openDoor = Tile(doorPosition):getItemById(1663)");
	expectContains(oasis, "openDoor:transform(1662)");
	expectContains(oasis, "theAncientOasisLever:aid(12107)");
	expectNotContains(oasis, "theAncientOasisLever:aid(12107, 12108)");
}

TEST(Oam043QuestsAdaptTest, RestoresMapBackedBeginningHandlers) {
	const auto hints = readSource("data-otservbr-global/scripts/quests/the_beginning/the_beginning_tutorial_moveevents.lua");
	expectContains(hints, "local tutorialStorage = Storage.Quest.U8_2.TheBeginningQuest");
	expectContains(hints, "tutorialHintTiles:aid(50058, 50059, 50060");
	expectContains(hints, "tutorialStopTiles:aid(50070, 50071, 50072, 50074, 50080, 50088)");

	const auto door = readSource("data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_door.lua");
	expectContains(door, "local ZIRELLA_DOOR_UID = 50085");
	expectContains(door, "local zirellaDoorPosition = Position(32058, 32266, 7)");
	expectContains(door, "zirellaDoor:uid(ZIRELLA_DOOR_UID)");
	expectContains(door, "item:transform(OPEN_DOOR_ITEM_ID)");
	expectContains(door, "item:transform(CLOSED_DOOR_ITEM_ID)");

	const auto wood = readSource("data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua");
	expectContains(wood, "local DEAD_TREE_ITEM_ID = 7753");
	expectContains(wood, "local BRANCH_ITEM_ID = 7772");
	expectContains(wood, "local ZIRELLA_CART_ITEM_ID = 7751");
	expectContains(wood, "tutorialDeadTree:id(DEAD_TREE_ITEM_ID)");
	expectContains(wood, "tutorialBranch:id(BRANCH_ITEM_ID)");
}

TEST(Oam043QuestsAdaptTest, RejectsUnavailableAccountWideQuestDonorSurface) {
	const auto apeCity = readSource("data-otservbr-global/scripts/quests/the_ape_city/movements_mission9_the_deepest_catacomb_teleport.lua");
	expectContains(apeCity, "Storage.Quest.U7_6.TheApeCity.Questline");
	expectNotContains(apeCity, "hasAccountQuestAccess");
	expectNotContains(apeCity, "unlockAccountQuestAccess");

	const auto emperor = readSource("data-otservbr-global/scripts/quests/wrath_of_the_emperor/movements_teleports_access.lua");
	expectContains(emperor, "player:getStorageValue(config[i].Access)");
	expectNotContains(emperor, "hasAccountQuestAccess");
	expectNotContains(emperor, "unlockAccountQuestAccess");
}

TEST(Oam043QuestsAdaptTest, PreservesRepresentativePersistenceHandoff) {
	const auto blueValley = readSource("data-otservbr-global/scripts/quests/the_way_of_the_monk/blue_valley_teleport.lua");
	expectContains(blueValley, "player:kv():set(\"blue-valley-destination\", teleport.from)");
	expectContains(blueValley, "player:kv():get(\"blue-valley-destination\") or \"peninsula\"");
}

TEST(Oam043QuestsAdaptTest, PreservesCompleteCanonicalQuestInventory) {
	EXPECT_EQ(countQuestFiles(), 981U);
}
