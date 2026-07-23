#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM037_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

TEST(Oam037RaidsReuseTest, PreservesRegistrySelectionAndSchedulerLifecycle) {
	const auto source = readSource("src/lua/creature/raids.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("bool Raids::loadFromXml()"), std::string::npos);
	EXPECT_NE(source.find("raidNode.attribute(\"interval2\")"), std::string::npos);
	EXPECT_NE(source.find("raidNode.attribute(\"margin\")"), std::string::npos);
	EXPECT_NE(source.find("raidNode.attribute(\"repeat\")"), std::string::npos);
	EXPECT_NE(source.find("bool Raids::startup()"), std::string::npos);
	EXPECT_NE(source.find("DispatcherLane::Maintenance"), std::string::npos);
	EXPECT_NE(source.find("[Raids::startup] Failed to schedule raid checks"), std::string::npos);
	EXPECT_NE(source.find("void Raids::checkRaids()"), std::string::npos);
	EXPECT_NE(source.find("setRunning(raid)"), std::string::npos);
	EXPECT_NE(source.find("raid->startRaid()"), std::string::npos);
	EXPECT_NE(source.find("!raid->canBeRepeated()"), std::string::npos);
	EXPECT_NE(source.find("[Raids::checkRaids] Failed to reschedule raid checks"), std::string::npos);
	EXPECT_NE(source.find("void Raids::clear()"), std::string::npos);
	EXPECT_NE(source.find("raid->stopEvents()"), std::string::npos);
	EXPECT_NE(source.find("scriptInterface.reInitState()"), std::string::npos);
	EXPECT_NE(source.find("bool Raids::reload()"), std::string::npos);
}

TEST(Oam037RaidsReuseTest, PreservesOrderedRaidEventFailureAndCleanupLifecycle) {
	const auto source = readSource("src/lua/creature/raids.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("void Raid::startRaid()"), std::string::npos);
	EXPECT_NE(source.find("[Raid::startRaid] Failed to schedule the first event for raid"), std::string::npos);
	EXPECT_NE(source.find("void Raid::executeRaidEvent(const std::shared_ptr<RaidEvent> &raidEvent)"), std::string::npos);
	EXPECT_NE(source.find("nextEvent++"), std::string::npos);
	EXPECT_NE(source.find("newRaidEvent->getDelay() - raidEvent->getDelay()"), std::string::npos);
	EXPECT_NE(source.find("[Raid::executeRaidEvent] Failed to schedule the next event for raid"), std::string::npos);
	EXPECT_NE(source.find("void Raid::resetRaid()"), std::string::npos);
	EXPECT_NE(source.find("state = RAIDSTATE_IDLE"), std::string::npos);
	EXPECT_NE(source.find("g_game().raids.setRunning(nullptr)"), std::string::npos);
	EXPECT_NE(source.find("g_game().raids.setLastRaidEnd(OTSYS_TIME())"), std::string::npos);
	EXPECT_NE(source.find("void Raid::stopEvents()"), std::string::npos);
	EXPECT_NE(source.find("g_dispatcher().stopEvent(nextEventEvent)"), std::string::npos);
}

TEST(Oam037RaidsReuseTest, PreservesCanonicalRaidEventKindsAndDispatchSurfaces) {
	const auto source = readSource("src/lua/creature/raids.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("strcasecmp(eventNode.name(), \"announce\")"), std::string::npos);
	EXPECT_NE(source.find("strcasecmp(eventNode.name(), \"singlespawn\")"), std::string::npos);
	EXPECT_NE(source.find("strcasecmp(eventNode.name(), \"areaspawn\")"), std::string::npos);
	EXPECT_NE(source.find("strcasecmp(eventNode.name(), \"script\")"), std::string::npos);
	EXPECT_NE(source.find("g_game().broadcastMessage(message, messageType)"), std::string::npos);
	EXPECT_NE(source.find("Monster::createMonster(monsterName)"), std::string::npos);
	EXPECT_NE(source.find("g_game().placeCreature(monster, position, false, true)"), std::string::npos);
	EXPECT_NE(source.find("spawnMonsterList.emplace_back(name, minAmount, maxAmount)"), std::string::npos);
	EXPECT_NE(source.find("loadScript(g_configManager().getString(DATA_DIRECTORY) + \"/raids/scripts/\" + scriptName, scriptName)"), std::string::npos);
	EXPECT_NE(source.find("return \"onRaid\""), std::string::npos);
	EXPECT_NE(source.find("scriptInterface->callFunction(0)"), std::string::npos);
}
