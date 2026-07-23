/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/instance/instance_id.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <mutex>
	#include <optional>
	#include <stdexcept>
	#include <string>
	#include <utility>
	#include <vector>
#endif

constexpr uint8_t INSTANCE_MAP_MAX_Z = 15;

// Inclusive, axis-aligned bounds for one physically separated instance slot.
// The pool only describes and reserves existing map space; it never copies map
// data or owns tiles.
struct InstanceMapRegion {
	InstanceSlotId slot = InstanceSlotId::Invalid;
	uint16_t minX = 0;
	uint16_t minY = 0;
	uint8_t minZ = 0;
	uint16_t maxX = 0;
	uint16_t maxY = 0;
	uint8_t maxZ = 0;
	std::string name;

	[[nodiscard]] bool isValid() const noexcept;
	[[nodiscard]] bool contains(uint16_t x, uint16_t y, uint8_t z) const noexcept;
	[[nodiscard]] bool overlaps(const InstanceMapRegion &other) const noexcept;
};

class InstanceRegionPool {
public:
	struct ReserveResult {
		bool ok = false;
		InstanceSlotId slot = InstanceSlotId::Invalid;
		std::optional<InstanceMapRegion> region;
		std::string error;
	};

	// Throws std::invalid_argument if a region is invalid, a slot id is
	// duplicated, or two configured regions overlap in all three dimensions.
	explicit InstanceRegionPool(std::vector<InstanceMapRegion> regions);

	InstanceRegionPool(const InstanceRegionPool &) = delete;
	InstanceRegionPool &operator=(const InstanceRegionPool &) = delete;

	// Reserves the first free region in configuration order.
	[[nodiscard]] ReserveResult reserve();

	// Reserves one specific configured slot. Returns false when the slot is
	// unknown or already reserved.
	bool reserve(InstanceSlotId slot);

	// Releases a reserved slot. Returns false for unknown or already-free slots.
	bool release(InstanceSlotId slot);

	[[nodiscard]] std::optional<InstanceMapRegion> getRegion(InstanceSlotId slot) const;
	[[nodiscard]] bool isReserved(InstanceSlotId slot) const;
	[[nodiscard]] std::size_t availableCount() const;
	[[nodiscard]] std::size_t totalCount() const;

private:
	struct Entry {
		InstanceMapRegion region;
		bool reserved = false;
	};

	[[nodiscard]] Entry* findEntryLocked(InstanceSlotId slot);
	[[nodiscard]] const Entry* findEntryLocked(InstanceSlotId slot) const;

	mutable std::mutex mutex;
	std::vector<Entry> entries;
};

// The implementation is inline so the CMake and legacy Visual Studio project
// paths cannot diverge by forgetting to compile a separate translation unit.
#include "game/instance/instance_region_pool.inl"
