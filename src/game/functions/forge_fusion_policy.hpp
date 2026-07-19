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

namespace ForgeFusionPolicy {
	[[nodiscard]] constexpr bool isValid(
		uint16_t firstItemId,
		uint16_t secondItemId,
		uint8_t firstClassification,
		uint8_t secondClassification,
		bool sameSlot,
		bool convergence
	) {
		if (firstItemId == 0 || secondItemId == 0 || firstClassification == 0 || secondClassification == 0) {
			return false;
		}

		if (!convergence) {
			return firstItemId == secondItemId && firstClassification == secondClassification;
		}

		return firstItemId != secondItemId
			&& firstClassification == 4
			&& secondClassification == 4
			&& sameSlot;
	}
} // namespace ForgeFusionPolicy
