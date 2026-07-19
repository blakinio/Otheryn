/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#pragma once

#include "creatures/players/imbuements/imbuement_storage_policy.hpp"

namespace ImbuementAccessPolicy {
	template <typename StorageReader>
	[[nodiscard]] bool canApplyDirectly(
		bool storageFilteringEnabled,
		bool playerPremium,
		bool imbuementPremium,
		uint32_t storageId,
		uint16_t baseId,
		StorageReader &&readStorage
	) {
		if (imbuementPremium && !playerPremium) {
			return false;
		}

		return !ImbuementStoragePolicy::shouldHide(
			storageFilteringEnabled,
			storageId,
			baseId,
			readStorage
		);
	}
} // namespace ImbuementAccessPolicy
