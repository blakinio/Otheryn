#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM041_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

TEST(Oam041SpawnsReuseTest, PreservesMonsterXmlPlacementAndLifecycle) {
	const auto source = readSource("src/creatures/monsters/spawns/spawn_monster.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("bool SpawnsMonster::loadFromXML(const std::string &filemonstername)"), std::string::npos);
	EXPECT_NE(source.find("spawnMonsterNode.attribute(\"centerx\")"), std::string::npos);
	EXPECT_NE(source.find("spawnMonsterNode.attribute(\"centery\")"), std::string::npos);
	EXPECT_NE(source.find("spawnMonsterNode.attribute(\"centerz\")"), std::string::npos);
	EXPECT_NE(source.find("childMonsterNode.attribute(\"x\")"), std::string::npos);
	EXPECT_NE(source.find("childMonsterNode.attribute(\"y\")"), std::string::npos);
	EXPECT_NE(source.find("centerPos.z"), std::string::npos);
	EXPECT_NE(source.find("g_configManager().getNumber(DEFAULT_RESPAWN_TIME)"), std::string::npos);
	EXPECT_NE(source.find("spawnMonster->addMonster(nameAttribute.as_string(), pos, dir, scheduleInterval * 1000, weight)"), std::string::npos);
	EXPECT_NE(source.find("void SpawnsMonster::startup()"), std::string::npos);
	EXPECT_NE(source.find("void SpawnsMonster::clear()"), std::string::npos);
	EXPECT_NE(source.find("Spectators().find<Player>(pos)"), std::string::npos);
	EXPECT_NE(source.find("PlayerFlags_t::IgnoredByMonsters"), std::string::npos);
	EXPECT_NE(source.find("void SpawnMonster::cleanup()"), std::string::npos);
	EXPECT_NE(source.find("monster->isRemoved()"), std::string::npos);
}

TEST(Oam041SpawnsReuseTest, PreservesMonsterSchedulingScalingBossAndWeightRules) {
	const auto source = readSource("src/creatures/monsters/spawns/spawn_monster.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("SpawnMonster::checkSpawnMonster\", DispatcherLane::Maintenance"), std::string::npos);
	EXPECT_NE(source.find("SpawnMonster::scheduleSpawn\", DispatcherLane::Maintenance"), std::string::npos);
	EXPECT_NE(source.find("g_eventsScheduler().getSpawnMonsterSchedule()"), std::string::npos);
	EXPECT_NE(source.find("g_game().getBoostedMonsterName()"), std::string::npos);
	EXPECT_NE(source.find("g_configManager().getNumber(RATE_SPAWN)"), std::string::npos);
	EXPECT_NE(source.find("MONSTER_MINSPAWN_INTERVAL"), std::string::npos);
	EXPECT_NE(source.find("MONSTER_MAXSPAWN_INTERVAL"), std::string::npos);
	EXPECT_NE(source.find("monsterType->isBoss() && !sb->monsterTypes.empty()"), std::string::npos);
	EXPECT_NE(source.find("if (sb->hasBoss())"), std::string::npos);
	EXPECT_NE(source.find("uniform_random(0, totalWeight - 1)"), std::string::npos);
	EXPECT_NE(source.find("orderedMonsterTypes.emplace_back(mType, weight)"), std::string::npos);
	EXPECT_NE(source.find("if (randomWeight < weight)"), std::string::npos);
}

TEST(Oam041SpawnsReuseTest, PreservesNpcPlacementIntervalAndRespawnLifecycle) {
	const auto source = readSource("src/creatures/npcs/spawns/spawn_npc.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("bool SpawnsNpc::loadFromXml(const std::string &fileNpcName)"), std::string::npos);
	EXPECT_NE(source.find("spawnNode.attribute(\"centerx\")"), std::string::npos);
	EXPECT_NE(source.find("spawnNode.attribute(\"centery\")"), std::string::npos);
	EXPECT_NE(source.find("spawnNode.attribute(\"centerz\")"), std::string::npos);
	EXPECT_NE(source.find("childNode.attribute(\"x\")"), std::string::npos);
	EXPECT_NE(source.find("childNode.attribute(\"y\")"), std::string::npos);
	EXPECT_NE(source.find("centerPos.z"), std::string::npos);
	EXPECT_NE(source.find("interval >= MINSPAWN_INTERVAL && interval <= MAXSPAWN_INTERVAL"), std::string::npos);
	EXPECT_NE(source.find("g_npcs().getNpcType(name)"), std::string::npos);
	EXPECT_NE(source.find("PlayerFlags_t::IgnoredByNpcs"), std::string::npos);
	EXPECT_NE(source.find("if (findPlayer(pos))"), std::string::npos);
	EXPECT_NE(source.find("SpawnNpc::checkSpawnNpc\", DispatcherLane::Maintenance"), std::string::npos);
	EXPECT_NE(source.find("__FUNCTION__, DispatcherLane::Maintenance"), std::string::npos);
	EXPECT_NE(source.find("void SpawnNpc::cleanup()"), std::string::npos);
	EXPECT_NE(source.find("npc->isRemoved()"), std::string::npos);
	EXPECT_NE(source.find("void SpawnNpc::stopEvent()"), std::string::npos);
}
