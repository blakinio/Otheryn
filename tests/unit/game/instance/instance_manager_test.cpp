#include "game/instance/instance_manager.hpp"

#include <gtest/gtest.h>

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <stdexcept>
	#include <vector>
#endif

namespace {
	std::vector<InstanceMapRegion> makeRegions(std::size_t count) {
		std::vector<InstanceMapRegion> regions;
		for (std::size_t index = 0; index < count; ++index) {
			const auto minX = static_cast<uint16_t>(100 + index * 20);
			regions.push_back({
				.slot = toSlotId(static_cast<uint32_t>(index)),
				.minX = minX,
				.minY = 100,
				.minZ = 7,
				.maxX = static_cast<uint16_t>(minX + 9),
				.maxY = 109,
				.maxZ = 7,
				.name = "region-" + std::to_string(index),
			});
		}
		return regions;
	}
}

TEST(InstanceManagerTest, LifecycleReservesActivatesClosesAndReusesRegion) {
	InstanceManager manager(makeRegions(1));
	const auto first = manager.createInstance({ .name = "first" });
	ASSERT_TRUE(first.ok);
	EXPECT_EQ(InstanceState::Creating, *manager.getState(first.id));
	ASSERT_TRUE(manager.activate(first.id));
	EXPECT_EQ(InstanceState::Active, *manager.getState(first.id));
	const auto firstSlot = manager.getSlot(first.id);
	ASSERT_TRUE(firstSlot.has_value());
	EXPECT_EQ(0u, manager.availableSlotCount());

	EXPECT_TRUE(manager.close(first.id));
	EXPECT_EQ(InstanceState::Destroyed, *manager.getState(first.id));
	EXPECT_EQ(1u, manager.availableSlotCount());
	EXPECT_TRUE(manager.close(first.id));

	const auto second = manager.createInstance({ .name = "second" });
	ASSERT_TRUE(second.ok);
	EXPECT_EQ(*firstSlot, *manager.getSlot(second.id));
}

TEST(InstanceManagerTest, CleanupRunsExactlyOnceAndDirtyRegionIsQuarantined) {
	InstanceManager manager(makeRegions(1));
	const auto result = manager.createInstance({ .name = "dirty" });
	ASSERT_TRUE(result.ok);
	ASSERT_TRUE(manager.registerCreature(result.id, 101));

	int cleanupCalls = 0;
	manager.setCleanupCallback(result.id, [&](InstanceId id, const InstanceMapRegion &) {
		++cleanupCalls;
		EXPECT_EQ(result.id, id);
	});

	EXPECT_THROW(manager.close(result.id), std::logic_error);
	EXPECT_EQ(1, cleanupCalls);
	EXPECT_EQ(InstanceState::Closing, *manager.getState(result.id));
	EXPECT_EQ(0u, manager.availableSlotCount());
	EXPECT_FALSE(manager.createInstance({ .name = "blocked" }).ok);

	EXPECT_TRUE(manager.unregisterCreature(result.id, 101));
	EXPECT_TRUE(manager.close(result.id));
	EXPECT_EQ(1u, manager.availableSlotCount());
}

TEST(InstanceManagerTest, CreatureOwnershipIsStableAndFailClosedAcrossInstances) {
	InstanceManager manager(makeRegions(2));
	const auto first = manager.createInstance({ .name = "first" });
	const auto second = manager.createInstance({ .name = "second" });
	ASSERT_TRUE(first.ok);
	ASSERT_TRUE(second.ok);

	EXPECT_TRUE(manager.registerCreature(first.id, 100));
	EXPECT_TRUE(manager.registerCreature(first.id, 100));
	EXPECT_FALSE(manager.registerCreature(second.id, 100));
	EXPECT_TRUE(manager.inheritCreatureOwnership(100, 101));
	EXPECT_EQ(first.id, *manager.getCreatureOwner(101));
	EXPECT_EQ(InstanceCreatureRelation::SameInstance, manager.getCreatureRelation(100, 101));
	EXPECT_EQ(InstanceCreatureRelation::Isolated, manager.getCreatureRelation(100, 999));
	EXPECT_EQ(InstanceCreatureRelation::SameWorld, manager.getCreatureRelation(998, 999));

	EXPECT_THROW(manager.close(first.id), std::logic_error);
	EXPECT_EQ(InstanceCreatureRelation::Isolated, manager.getCreatureRelation(100, 101));
	EXPECT_FALSE(manager.inheritCreatureOwnership(100, 102));
}

TEST(InstanceManagerTest, ExpirationSweepClosesOnlyTimedOutInstances) {
	InstanceManager manager(makeRegions(3));
	const auto shortLived = manager.createInstance({ .name = "short", .timeout = std::chrono::seconds(1) });
	const auto longLived = manager.createInstance({ .name = "long", .timeout = std::chrono::hours(1) });
	const auto noTimeout = manager.createInstance({ .name = "forever" });
	ASSERT_TRUE(shortLived.ok);
	ASSERT_TRUE(longLived.ok);
	ASSERT_TRUE(noTimeout.ok);
	manager.activate(shortLived.id);
	manager.activate(longLived.id);
	manager.activate(noTimeout.id);

	const auto future = std::chrono::steady_clock::now() + std::chrono::seconds(10);
	EXPECT_EQ(1u, manager.closeExpiredInstances(future));
	EXPECT_EQ(InstanceState::Destroyed, *manager.getState(shortLived.id));
	EXPECT_EQ(InstanceState::Active, *manager.getState(longLived.id));
	EXPECT_EQ(InstanceState::Active, *manager.getState(noTimeout.id));
	EXPECT_EQ(0u, manager.closeExpiredInstances(future));
}
