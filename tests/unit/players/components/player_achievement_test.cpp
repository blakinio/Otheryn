/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#include "creatures/players/player.hpp"
#include "game/game.hpp"
#include "injection_fixture.hpp"

class PlayerAchievementTest : public ::testing::Test {
protected:
	static constexpr uint16_t TWO_POINT_ID = 65000;
	static constexpr uint16_t THREE_POINT_ID = 65001;
	static constexpr std::string_view TWO_POINT_NAME = "Point Reconciliation Two";
	static constexpr std::string_view THREE_POINT_NAME = "Point Reconciliation Three";

	void SetUp() override {
		g_game().registerAchievement(TWO_POINT_ID, std::string(TWO_POINT_NAME), "", false, 1, 2);
		g_game().registerAchievement(THREE_POINT_ID, std::string(THREE_POINT_NAME), "", false, 1, 3);
	}

	static std::shared_ptr<Player> createPlayer() {
		return std::make_shared<Player>();
	}

	static void setStoredPoints(const std::shared_ptr<Player> &player, uint16_t points) {
		player->kv()->scoped("achievements")->set("points", points);
	}

	static void setUnlocked(const std::shared_ptr<Player> &player, std::string_view name, int timestamp) {
		player->achiev().getUnlockedKV()->set(std::string(name), timestamp);
	}

	static uint32_t timestampFor(const PlayerAchievement &component, uint16_t id) {
		const auto unlocked = component.getUnlockedAchievements();
		const auto it = std::ranges::find_if(unlocked, [id](const auto &entry) {
			return entry.first == id;
		});
		return it == unlocked.end() ? 0 : it->second;
	}

private:
	InjectionFixture fixture_ {};
};

TEST_F(PlayerAchievementTest, LoadReconcilesUpwardAndPreservesTimestamps) {
	auto player = createPlayer();
	setUnlocked(player, TWO_POINT_NAME, 111);
	setUnlocked(player, THREE_POINT_NAME, 222);
	setStoredPoints(player, 1);

	player->achiev().loadUnlockedAchievements();

	EXPECT_EQ(5, player->achiev().getPoints());
	EXPECT_EQ(111, timestampFor(player->achiev(), TWO_POINT_ID));
	EXPECT_EQ(222, timestampFor(player->achiev(), THREE_POINT_ID));
}

TEST_F(PlayerAchievementTest, LoadReconcilesDownward) {
	auto player = createPlayer();
	setUnlocked(player, TWO_POINT_NAME, 111);
	setStoredPoints(player, 20);

	player->achiev().loadUnlockedAchievements();

	EXPECT_EQ(2, player->achiev().getPoints());
}

TEST_F(PlayerAchievementTest, RepeatedLoadIsIdempotentAndDuplicateFree) {
	auto player = createPlayer();
	setUnlocked(player, TWO_POINT_NAME, 111);
	setUnlocked(player, THREE_POINT_NAME, 222);
	setStoredPoints(player, 0);

	player->achiev().loadUnlockedAchievements();
	player->achiev().loadUnlockedAchievements();

	EXPECT_EQ(5, player->achiev().getPoints());
	EXPECT_EQ(2, player->achiev().getUnlockedAchievements().size());
}

TEST_F(PlayerAchievementTest, EmptyUnlockSetReconcilesToZero) {
	auto player = createPlayer();
	setStoredPoints(player, 9);

	player->achiev().loadUnlockedAchievements();

	EXPECT_EQ(0, player->achiev().getPoints());
	EXPECT_TRUE(player->achiev().getUnlockedAchievements().empty());
}

TEST_F(PlayerAchievementTest, UnknownStoredNameBlocksReconciliation) {
	auto player = createPlayer();
	setUnlocked(player, TWO_POINT_NAME, 111);
	setUnlocked(player, "Historical Unknown Achievement", 333);
	setStoredPoints(player, 99);

	player->achiev().loadUnlockedAchievements();

	EXPECT_EQ(99, player->achiev().getPoints());
	EXPECT_TRUE(player->achiev().getUnlockedKV()->get("Historical Unknown Achievement").has_value());
	EXPECT_EQ(1, player->achiev().getUnlockedAchievements().size());
}

TEST_F(PlayerAchievementTest, AddAndRemoveRemainCorrectAfterReconciliation) {
	auto player = createPlayer();
	setUnlocked(player, TWO_POINT_NAME, 111);
	setStoredPoints(player, 42);
	player->achiev().loadUnlockedAchievements();

	ASSERT_EQ(2, player->achiev().getPoints());
	EXPECT_TRUE(player->achiev().add(THREE_POINT_ID, false, 222));
	EXPECT_EQ(5, player->achiev().getPoints());
	EXPECT_TRUE(player->achiev().remove(TWO_POINT_ID));
	EXPECT_EQ(3, player->achiev().getPoints());
}

TEST_F(PlayerAchievementTest, CalculateUnlockedPointsUsesCurrentDefinitions) {
	auto player = createPlayer();
	setUnlocked(player, TWO_POINT_NAME, 111);
	setUnlocked(player, THREE_POINT_NAME, 222);
	player->achiev().loadUnlockedAchievements();

	const auto calculated = player->achiev().calculateUnlockedPoints();
	ASSERT_TRUE(calculated.has_value());
	EXPECT_EQ(5, calculated.value());
	EXPECT_TRUE(player->achiev().reconcilePoints());
}
