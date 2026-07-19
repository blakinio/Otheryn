/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
#endif

namespace ForgeEffectPolicy {
	[[nodiscard]] constexpr bool isAvatarActive(uint64_t forgeAvatarUntil, uint64_t spellAvatarUntil, uint64_t now) {
		return forgeAvatarUntil > now || spellAvatarUntil > now;
	}

	[[nodiscard]] constexpr bool isMomentumCooldownEligible(bool isSpellCooldown, bool isSpellGroupCooldown, uint16_t spellOrGroupId, uint16_t supportGroupId) {
		return isSpellCooldown || (isSpellGroupCooldown && spellOrGroupId > supportGroupId);
	}
} // namespace ForgeEffectPolicy
