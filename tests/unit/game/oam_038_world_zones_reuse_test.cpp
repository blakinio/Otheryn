#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM038_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

TEST(Oam038WorldZonesReuseTest, PreservesRegistryAndPositionIndexLifecycle) {
	const auto source = readSource("src/game/zones/zone.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("std::shared_ptr<Zone> Zone::addZone"), std::string::npos);
	EXPECT_NE(source.find("if (name == \"default\")"), std::string::npos);
	EXPECT_NE(source.find("zonesByID.contains(zoneID)"), std::string::npos);
	EXPECT_NE(source.find("zone->indexPositions()"), std::string::npos);
	EXPECT_NE(source.find("void Zone::addArea(Area area)"), std::string::npos);
	EXPECT_NE(source.find("void Zone::subtractArea(Area area)"), std::string::npos);
	EXPECT_NE(source.find("void Zone::indexPosition(const Position &position)"), std::string::npos);
	EXPECT_NE(source.find("auto &zonesAtPosition = zonesByPosition[position]"), std::string::npos);
	EXPECT_NE(source.find("void Zone::unindexPosition(const Position &position)"), std::string::npos);
	EXPECT_NE(source.find("zonesByPosition.erase(it)"), std::string::npos);
	EXPECT_NE(source.find("std::vector<std::shared_ptr<Zone>> Zone::getZones(const Position position)"), std::string::npos);
	EXPECT_NE(source.find("std::vector<std::shared_ptr<Zone>> Zone::getZones()"), std::string::npos);
}

TEST(Oam038WorldZonesReuseTest, PreservesSynchronizedWeakMembershipCachesAndCleanup) {
	const auto source = readSource("src/game/zones/zone.cpp");
	const auto header = readSource("src/game/zones/zone.hpp");
	ASSERT_FALSE(source.empty());
	ASSERT_FALSE(header.empty());

	EXPECT_NE(header.find("mutable std::mutex cacheMutex"), std::string::npos);
	EXPECT_NE(header.find("it = weakSet.erase(it)"), std::string::npos);
	EXPECT_NE(source.find("std::scoped_lock lock(cacheMutex)"), std::string::npos);
	EXPECT_NE(source.find("creaturesCache.erase(std::weak_ptr<Creature>(creature))"), std::string::npos);
	EXPECT_NE(source.find("playersCache.erase(std::weak_ptr<Player>(player))"), std::string::npos);
	EXPECT_NE(source.find("monstersCache.erase(std::weak_ptr<Monster>(monster))"), std::string::npos);
	EXPECT_NE(source.find("npcsCache.erase(std::weak_ptr<Npc>(npc))"), std::string::npos);
	EXPECT_NE(source.find("itemsCache.erase(std::weak_ptr<Item>(item))"), std::string::npos);
	EXPECT_NE(source.find("void Zone::refresh()"), std::string::npos);
	EXPECT_NE(source.find("void Zone::clearZones()"), std::string::npos);
	EXPECT_NE(source.find("if (!zone || zone->isStatic())"), std::string::npos);
	EXPECT_NE(source.find("zone->unindexPositions()"), std::string::npos);
	EXPECT_NE(source.find("zones[zone->name] = zone"), std::string::npos);
}

TEST(Oam038WorldZonesReuseTest, PreservesRemovalVariantAndXmlLoadingSurfaces) {
	const auto source = readSource("src/game/zones/zone.cpp");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("Position Zone::getRemoveDestination"), std::string::npos);
	EXPECT_NE(source.find("getTown()->getTemplePosition()"), std::string::npos);
	EXPECT_NE(source.find("void Zone::removePlayers()"), std::string::npos);
	EXPECT_NE(source.find("void Zone::removeMonsters()"), std::string::npos);
	EXPECT_NE(source.find("void Zone::removeNpcs()"), std::string::npos);
	EXPECT_NE(source.find("void Zone::setMonsterVariant(const std::string &variant)"), std::string::npos);
	EXPECT_NE(source.find("spawnMonster->setMonsterVariant(variant)"), std::string::npos);
	EXPECT_NE(source.find("bool Zone::loadFromXML(const std::string &fileName, uint16_t shiftID"), std::string::npos);
	EXPECT_NE(source.find("pugi::cast<uint32_t>(zoneNode.attribute(\"zoneid\").value()) << shiftID"), std::string::npos);
}
