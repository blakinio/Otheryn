#include <gtest/gtest.h>

#define private public
#include "creatures/players/player.hpp"
#include "creatures/players/vocations/vocation.hpp"
#undef private

namespace {
	std::shared_ptr<Player> makeTestPlayer() {
		return std::make_shared<Player>();
	}

	std::shared_ptr<Vocation> makeTestVocation() {
		return std::make_shared<Vocation>(1);
	}
}

TEST(CharacterProgressionTest, ExperienceThresholdsAreMonotonic) {
	EXPECT_EQ(Player::getExpForLevel(1), 0U);
	EXPECT_LT(Player::getExpForLevel(1), Player::getExpForLevel(2));
	EXPECT_LT(Player::getExpForLevel(10), Player::getExpForLevel(11));
	EXPECT_LT(Player::getExpForLevel(100), Player::getExpForLevel(101));
}

TEST(CharacterProgressionTest, ZeroStaminaBlocksExperienceGainBeforeMutation) {
	const auto player = makeTestPlayer();
	player->staminaMinutes = 0;
	player->experience = Player::getExpForLevel(10);
	player->level = 10;

	const auto before = player->experience;
	player->gainExperience(1000, nullptr);

	EXPECT_EQ(player->experience, before);
	EXPECT_EQ(player->level, 10U);
}

TEST(CharacterProgressionTest, OfflineTrainingTimeClampsAndFloors) {
	const auto player = makeTestPlayer();

	player->addOfflineTrainingTime(13 * 60 * 60 * 1000);
	EXPECT_EQ(player->getOfflineTrainingTime(), 12 * 60 * 60 * 1000);

	player->removeOfflineTrainingTime(13 * 60 * 60 * 1000);
	EXPECT_EQ(player->getOfflineTrainingTime(), 0);

	player->setOfflineTrainingSkill(SKILL_SWORD);
	EXPECT_EQ(player->getOfflineTrainingSkill(), SKILL_SWORD);
}

TEST(CharacterProgressionTest, OfflineTrainingAdvancesRegularSkillAtRequirementBoundary) {
	const auto player = makeTestPlayer();
	player->vocation = makeTestVocation();
	player->skills[SKILL_SWORD].level = 10;
	player->skills[SKILL_SWORD].tries = 0;

	const auto required = player->vocation->getReqSkillTries(SKILL_SWORD, 11);
	ASSERT_GT(required, 0U);

	EXPECT_TRUE(player->addOfflineTrainingTries(SKILL_SWORD, required));
	EXPECT_EQ(player->skills[SKILL_SWORD].level, 11U);
	EXPECT_EQ(player->skills[SKILL_SWORD].tries, 0U);
}

TEST(CharacterProgressionTest, OfflineTrainingAdvancesMagicLevelAtRequirementBoundary) {
	const auto player = makeTestPlayer();
	player->vocation = makeTestVocation();
	player->magLevel = 0;
	player->manaSpent = 0;

	const auto required = player->vocation->getReqMana(1);
	ASSERT_GT(required, 0U);

	EXPECT_TRUE(player->addOfflineTrainingTries(SKILL_MAGLEVEL, required));
	EXPECT_EQ(player->magLevel, 1U);
	EXPECT_EQ(player->manaSpent, 0U);
}
