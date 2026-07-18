/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "creatures/players/player.hpp"
#include "creatures/players/components/weapon_proficiency.hpp"

#include "lib/logging/in_memory_logger.hpp"

class WeaponProficiencyTest : public ::testing::Test {
protected:
	static void SetUpTestSuite() {
		InMemoryLogger::install(injector);
		DI::setTestContainer(&injector);
	}

	static WeaponProficiencyData createInitialState(uint32_t experience, uint32_t maxExperience) {
		return WeaponProficiency::createInitialState(experience, maxExperience);
	}

	static void setMasteredState(WeaponProficiency &component, uint16_t weaponId, bool mastered) {
		WeaponProficiencyData state;
		state.mastered = mastered;
		component.proficiency.insert_or_assign(weaponId, std::move(state));
	}

	static std::vector<uint16_t> getMasteryAchievementIds(size_t masteredWeaponCount) {
		return WeaponProficiency::getMasteryAchievementIds(masteredWeaponCount);
	}

private:
	inline static di::extension::injector<> injector {};
};

TEST_F(WeaponProficiencyTest, InitialStateBelowMaximumIsNotMastered) {
	const auto state = createInitialState(99, 100);

	EXPECT_EQ(99u, state.experience);
	EXPECT_FALSE(state.mastered);
}

TEST_F(WeaponProficiencyTest, InitialStateAtMaximumIsMastered) {
	const auto state = createInitialState(100, 100);

	EXPECT_EQ(100u, state.experience);
	EXPECT_TRUE(state.mastered);
}

TEST_F(WeaponProficiencyTest, InitialStateAboveMaximumIsCappedAndMastered) {
	const auto state = createInitialState(150, 100);

	EXPECT_EQ(100u, state.experience);
	EXPECT_TRUE(state.mastered);
}

TEST_F(WeaponProficiencyTest, ZeroMaximumNeverProducesMastery) {
	const auto state = createInitialState(100, 0);

	EXPECT_EQ(0u, state.experience);
	EXPECT_FALSE(state.mastered);
}

TEST_F(WeaponProficiencyTest, MasteredWeaponCountIncludesOnlyMasteredEntries) {
	auto player = std::make_shared<Player>();
	auto &component = player->weaponProficiency();

	setMasteredState(component, 300, true);
	setMasteredState(component, 100, false);
	setMasteredState(component, 200, true);

	const auto &constComponent = component;
	EXPECT_EQ(std::size_t { 2 }, constComponent.getMasteredWeaponCount());
}

TEST_F(WeaponProficiencyTest, EmptyStateHasNoMasteredWeapons) {
	auto player = std::make_shared<Player>();
	const auto &component = player->weaponProficiency();

	EXPECT_EQ(std::size_t { 0 }, component.getMasteredWeaponCount());
}

TEST_F(WeaponProficiencyTest, MasteryAchievementThresholdsAreExact) {
	EXPECT_TRUE(getMasteryAchievementIds(0).empty());
	EXPECT_EQ((std::vector<uint16_t> { 564 }), getMasteryAchievementIds(1));
	EXPECT_EQ((std::vector<uint16_t> { 564 }), getMasteryAchievementIds(9));
	EXPECT_EQ((std::vector<uint16_t> { 564, 565 }), getMasteryAchievementIds(10));
	EXPECT_EQ((std::vector<uint16_t> { 564, 565 }), getMasteryAchievementIds(49));
	EXPECT_EQ((std::vector<uint16_t> { 564, 565, 566 }), getMasteryAchievementIds(50));
	EXPECT_EQ((std::vector<uint16_t> { 564, 565, 566 }), getMasteryAchievementIds(500));
}
