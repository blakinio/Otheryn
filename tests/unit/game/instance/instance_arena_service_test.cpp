#include "game/instance/instance_arena_service.hpp"

#include <gtest/gtest.h>

namespace {
	InstanceMapRegion makeRegion() {
		return {
			.slot = toSlotId(0),
			.minX = 100,
			.minY = 100,
			.minZ = 7,
			.maxX = 111,
			.maxY = 106,
			.maxZ = 7,
			.name = "target-test-region",
		};
	}
}

TEST(InstanceArenaServiceTest, CleanTargetDoesNotImportLegacyMapCoordinates) {
	EXPECT_TRUE(InstanceArenaService::configuredRegions().empty());

	InstanceManager manager(InstanceArenaService::configuredRegions());
	InstanceArenaService service(manager);
	const auto result = service.createArena();
	EXPECT_FALSE(result.ok);
	EXPECT_EQ(InstanceId::Invalid, result.id);
	EXPECT_FALSE(result.error.empty());
}

TEST(InstanceArenaServiceTest, OperatesAgainstExplicitlyConfiguredTargetRegion) {
	InstanceManager manager({ makeRegion() });
	InstanceArenaService service(manager);
	const auto result = service.createArena();
	ASSERT_TRUE(result.ok);
	EXPECT_EQ(InstanceState::Active, *service.getState(result.id));
	ASSERT_TRUE(service.getRegion(result.id).has_value());
	EXPECT_EQ("target-test-region", service.getRegion(result.id)->name);
	EXPECT_EQ(1u, service.activeArenaCount());
	EXPECT_TRUE(service.closeArena(result.id));
	EXPECT_EQ(InstanceState::Destroyed, *service.getState(result.id));
}
