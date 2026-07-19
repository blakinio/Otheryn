/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include <gtest/gtest.h>

#include "config/forge_config_defaults.hpp"
#include "game/functions/forge_effect_policy.hpp"
#include "game/functions/forge_fusion_policy.hpp"
#include "game/functions/forge_transaction.hpp"
#include "game/functions/forge_transfer_policy.hpp"

TEST(Oam020ExaltationForgeAdaptTest, PinsValidatedDefaultsAndServerAuthorityPolicies) {
	EXPECT_EQ(325, ForgeConfigDefaults::maxDust);
	EXPECT_EQ(4, ForgeConfigDefaults::fiendishCreaturesLimit);

	EXPECT_TRUE(ForgeFusionPolicy::isValid(100, 100, 4, 4, false, false));
	EXPECT_FALSE(ForgeFusionPolicy::isValid(100, 101, 4, 4, false, false));
	EXPECT_TRUE(ForgeFusionPolicy::isValid(100, 101, 4, 4, true, true));
	EXPECT_FALSE(ForgeFusionPolicy::isValid(100, 101, 3, 3, true, true));

	EXPECT_TRUE(ForgeTransferPolicy::isValidTransfer(4, 4, 1, true));
	EXPECT_FALSE(ForgeTransferPolicy::isValidTransfer(3, 3, 1, true));
	EXPECT_TRUE(ForgeTransferPolicy::isValidTransfer(2, 2, 2, false));
	EXPECT_EQ(2, ForgeTransferPolicy::resourceTier(2));
	EXPECT_EQ(1, ForgeTransferPolicy::resultTier(2, false));
}

TEST(Oam020ExaltationForgeAdaptTest, PreservesEffectGatesAndRollsBackFailedTransactions) {
	constexpr uint64_t now = 1000;
	EXPECT_TRUE(ForgeEffectPolicy::isAvatarActive(1001, 0, now));
	EXPECT_TRUE(ForgeEffectPolicy::isAvatarActive(0, 1001, now));
	EXPECT_TRUE(ForgeEffectPolicy::isMomentumCooldownEligible(true, false, 0, 3));
	EXPECT_FALSE(ForgeEffectPolicy::isMomentumCooldownEligible(false, true, 3, 3));

	int state = 0;
	ForgeTransaction transaction;
	transaction.stage(
		[&state] {
			state = 1;
			return true;
		},
		[&state] {
			state = 0;
		}
	);
	transaction.stage(
		[] {
			return false;
		},
		[] { }
	);

	EXPECT_FALSE(transaction.commit());
	EXPECT_FALSE(transaction.isCommitted());
	EXPECT_EQ(0, state);
}
