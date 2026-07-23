#include "game/instance/instance_scoped_event.hpp"

#include <gtest/gtest.h>

namespace {
	InstanceMapRegion makeRegion() {
		return {
			.slot = toSlotId(0),
			.minX = 100,
			.minY = 100,
			.minZ = 7,
			.maxX = 109,
			.maxY = 109,
			.maxZ = 7,
			.name = "region",
		};
	}
}

TEST(InstanceScopedEventTest, RunsOnlyWhileInstanceIsActive) {
	InstanceManager manager({ makeRegion() });
	const auto instance = manager.createInstance({ .name = "test" });
	ASSERT_TRUE(instance.ok);
	InstanceScopedEvent event(manager, instance.id);
	int calls = 0;

	EXPECT_FALSE(event.isLive());
	EXPECT_FALSE(event.runIfLive([&] { ++calls; }));
	ASSERT_TRUE(manager.activate(instance.id));
	EXPECT_TRUE(event.isLive());
	EXPECT_TRUE(event.runIfLive([&] { ++calls; }));
	EXPECT_EQ(1, calls);

	ASSERT_TRUE(manager.close(instance.id));
	EXPECT_FALSE(event.isLive());
	EXPECT_FALSE(event.runIfLive([&] { ++calls; }));
	EXPECT_EQ(1, calls);
}

TEST(InstanceScopedEventTest, ClosingIsAlreadyFailClosedInsideCleanup) {
	InstanceManager manager({ makeRegion() });
	const auto instance = manager.createInstance({ .name = "test" });
	ASSERT_TRUE(manager.activate(instance.id));
	InstanceScopedEvent event(manager, instance.id);
	bool liveDuringCleanup = true;

	manager.setCleanupCallback(instance.id, [&](InstanceId, const InstanceMapRegion &) {
		liveDuringCleanup = event.isLive();
	});
	ASSERT_TRUE(manager.close(instance.id));
	EXPECT_FALSE(liveDuringCleanup);
}
