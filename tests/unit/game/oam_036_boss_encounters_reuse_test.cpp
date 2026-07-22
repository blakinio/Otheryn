#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM036_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

TEST(Oam036BossEncountersReuseTest, PreservesRewardContainerAndParticipantStateLifecycle) {
	const auto rewardBoss = readSource("data/libs/systems/reward_boss.lua");
	ASSERT_FALSE(rewardBoss.empty());

	EXPECT_NE(rewardBoss.find("function InsertRewardItems(playerGuid, timestamp, itemList)"), std::string::npos);
	EXPECT_NE(rewardBoss.find("ITEM_REWARD_CONTAINER"), std::string::npos);
	EXPECT_NE(rewardBoss.find("db.query(insertItemsQuery)"), std::string::npos);
	EXPECT_NE(rewardBoss.find("function GetPlayerStats(bossId, playerGuid, autocreate)"), std::string::npos);
	EXPECT_NE(rewardBoss.find("_G.GlobalBosses[bossId][playerGuid]"), std::string::npos);
	EXPECT_NE(rewardBoss.find("function ResetAndSetTargetList(creature)"), std::string::npos);
	EXPECT_NE(rewardBoss.find("creature:getTargetList()"), std::string::npos);
	EXPECT_NE(rewardBoss.find("stats.active = true"), std::string::npos);
}

TEST(Oam036BossEncountersReuseTest, PreservesBossDeathScoringRewardAndCleanupLifecycle) {
	const auto rewardChest = readSource("data/scripts/systems/reward_chest.lua");
	ASSERT_FALSE(rewardChest.empty());

	EXPECT_NE(rewardChest.find("CreatureEvent(\"BossDeath\")"), std::string::npos);
	EXPECT_NE(rewardChest.find("monsterType:isRewardBoss()"), std::string::npos);
	EXPECT_NE(rewardChest.find("ResetAndSetTargetList(creature)"), std::string::npos);
	EXPECT_NE(rewardChest.find("totalDamageOut, totalDamageIn, totalHealing"), std::string::npos);
	EXPECT_NE(rewardChest.find("con.score = score / 3"), std::string::npos);
	EXPECT_NE(rewardChest.find("monsterType:getBossReward"), std::string::npos);
	EXPECT_NE(rewardChest.find("reward:addRewardBossItems(playerLoot)"), std::string::npos);
	EXPECT_NE(rewardChest.find("player:save()"), std::string::npos);
	EXPECT_NE(rewardChest.find("_G.GlobalBosses[bossId] = nil"), std::string::npos);
	EXPECT_NE(rewardChest.find("CreatureEvent(\"BossParticipation\")"), std::string::npos);
	EXPECT_NE(rewardChest.find("GetPlayerStats(stats.bossId, attacker:getGuid(), true)"), std::string::npos);
}
