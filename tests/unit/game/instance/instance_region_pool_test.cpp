#include "game/instance/instance_region_pool.hpp"

#include <gtest/gtest.h>

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <mutex>
	#include <thread>
	#include <vector>
#endif

namespace {
	InstanceMapRegion makeRegion(uint32_t slot, uint16_t minX, uint16_t minY, uint8_t minZ = 7, uint16_t size = 10, uint8_t maxZ = 7) {
		return {
			.slot = toSlotId(slot),
			.minX = minX,
			.minY = minY,
			.minZ = minZ,
			.maxX = static_cast<uint16_t>(minX + size - 1),
			.maxY = static_cast<uint16_t>(minY + size - 1),
			.maxZ = maxZ,
			.name = "region-" + std::to_string(slot),
		};
	}
}

TEST(InstanceRegionPoolTest, ValidatesBoundsAndOverlap) {
	const auto first = makeRegion(0, 100, 100, 7, 10, 8);
	const auto adjacent = makeRegion(1, 110, 100, 7, 10, 8);
	const auto otherFloor = makeRegion(2, 100, 100, 9, 10, 9);
	const auto overlapping = makeRegion(3, 109, 109, 8, 10, 8);

	EXPECT_TRUE(first.isValid());
	EXPECT_TRUE(first.contains(100, 100, 7));
	EXPECT_FALSE(first.contains(110, 109, 8));
	EXPECT_FALSE(first.overlaps(adjacent));
	EXPECT_FALSE(first.overlaps(otherFloor));
	EXPECT_TRUE(first.overlaps(overlapping));

	auto invalid = first;
	invalid.slot = InstanceSlotId::Invalid;
	EXPECT_THROW(InstanceRegionPool({ invalid }), std::invalid_argument);
	EXPECT_THROW(InstanceRegionPool({ makeRegion(0, 100, 100), makeRegion(0, 200, 200) }), std::invalid_argument);
	EXPECT_THROW(InstanceRegionPool({ makeRegion(0, 100, 100), makeRegion(1, 109, 109) }), std::invalid_argument);
}

TEST(InstanceRegionPoolTest, ReservesReleasesAndReusesDeterministically) {
	InstanceRegionPool pool({ makeRegion(4, 100, 100), makeRegion(9, 200, 200) });
	EXPECT_EQ(2u, pool.totalCount());
	EXPECT_EQ(2u, pool.availableCount());

	const auto first = pool.reserve();
	ASSERT_TRUE(first.ok);
	EXPECT_EQ(toSlotId(4), first.slot);
	EXPECT_TRUE(pool.reserve(toSlotId(9)));
	EXPECT_FALSE(pool.reserve().ok);
	EXPECT_TRUE(pool.release(toSlotId(4)));
	EXPECT_FALSE(pool.release(toSlotId(4)));

	const auto reused = pool.reserve();
	ASSERT_TRUE(reused.ok);
	EXPECT_EQ(toSlotId(4), reused.slot);
}

TEST(InstanceRegionPoolTest, ConcurrentReservationsNeverDuplicateSlots) {
	std::vector<InstanceMapRegion> regions;
	for (uint32_t slot = 0; slot < 8; ++slot) {
		regions.push_back(makeRegion(slot, static_cast<uint16_t>(100 + slot * 20), 100));
	}
	InstanceRegionPool pool(std::move(regions));

	std::mutex resultMutex;
	std::vector<InstanceSlotId> reserved;
	std::vector<std::thread> workers;
	for (std::size_t index = 0; index < 24; ++index) {
		workers.emplace_back([&] {
			const auto result = pool.reserve();
			if (result.ok) {
				std::scoped_lock lock(resultMutex);
				reserved.push_back(result.slot);
			}
		});
	}
	for (auto &worker : workers) {
		worker.join();
	}

	ASSERT_EQ(8u, reserved.size());
	std::ranges::sort(reserved, {}, [](InstanceSlotId slot) { return toIndex(slot); });
	EXPECT_EQ(std::ranges::unique(reserved).begin(), reserved.end());
}
