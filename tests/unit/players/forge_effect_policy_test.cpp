/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include <gtest/gtest.h>

#include "game/functions/forge_effect_policy.hpp"

TEST(ForgeEffectPolicyTest, BlocksTranscendenceForEitherActiveAvatarSource) {
	constexpr uint64_t now = 1000;
	EXPECT_TRUE(ForgeEffectPolicy::isAvatarActive(1001, 0, now));
	EXPECT_TRUE(ForgeEffectPolicy::isAvatarActive(0, 1001, now));
	EXPECT_TRUE(ForgeEffectPolicy::isAvatarActive(1001, 1002, now));
	EXPECT_FALSE(ForgeEffectPolicy::isAvatarActive(now, now, now));
	EXPECT_FALSE(ForgeEffectPolicy::isAvatarActive(0, 0, now));
}

TEST(ForgeEffectPolicyTest, AcceptsOnlyCooldownsMomentumCanActuallyReduce) {
	constexpr uint16_t supportGroup = 3;
	EXPECT_TRUE(ForgeEffectPolicy::isMomentumCooldownEligible(true, false, 0, supportGroup));
	EXPECT_TRUE(ForgeEffectPolicy::isMomentumCooldownEligible(false, true, supportGroup + 1, supportGroup));
	EXPECT_FALSE(ForgeEffectPolicy::isMomentumCooldownEligible(false, true, supportGroup, supportGroup));
	EXPECT_FALSE(ForgeEffectPolicy::isMomentumCooldownEligible(false, true, supportGroup - 1, supportGroup));
	EXPECT_FALSE(ForgeEffectPolicy::isMomentumCooldownEligible(false, false, supportGroup + 1, supportGroup));
}
