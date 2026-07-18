/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#include <gtest/gtest.h>

#include "items/weapons/weapons.hpp"

TEST(WeaponReuseTest, PreservesMaximumDamageHelpers) {
	EXPECT_EQ(Weapons::getMaxMeleeDamage(100, 50), 275);
	EXPECT_EQ(Weapons::getMaxWeaponDamage(100, 100, 50, 1.0F, true), 445);
	EXPECT_EQ(Weapons::getMaxWeaponDamage(100, 100, 50, 1.0F, false), 470);
	EXPECT_EQ(Weapons::getMaxWeaponDamage(100, 100, 0, 1.0F, true), 0);
}

TEST(WeaponReuseTest, PreservesDeterministicWandMaximumDamage) {
	WeaponWand wand;
	wand.setMinChange(20);
	wand.setMaxChange(80);

	EXPECT_EQ(wand.getWeaponDamage(nullptr, nullptr, nullptr, true), -80);
	EXPECT_EQ(wand.getElementDamageValue(), 0);
}
