#include "game/instance/instance_creature_binder.hpp"

#include <gtest/gtest.h>

namespace {
	struct FakeCreature {
		uint32_t id;
		[[nodiscard]] uint32_t getID() const {
			return id;
		}
	};

	InstanceMapRegion region(uint32_t slot, uint16_t x) {
		return {
			.slot = toSlotId(slot),
			.minX = x,
			.minY = 100,
			.minZ = 7,
			.maxX = static_cast<uint16_t>(x + 9),
			.maxY = 109,
			.maxZ = 7,
			.name = "region",
		};
	}
}

TEST(InstanceCreatureBinderTest, BindsAndUnbindsThroughStableRuntimeIds) {
	InstanceManager manager({ region(0, 100) });
	const auto instance = manager.createInstance({ .name = "test" });
	ASSERT_TRUE(instance.ok);
	InstanceCreatureBinder binder(manager);
	const FakeCreature creature { 42 };

	EXPECT_TRUE(binder.bind(instance.id, creature));
	ASSERT_TRUE(binder.ownerOf(creature).has_value());
	EXPECT_EQ(instance.id, *binder.ownerOf(creature));
	EXPECT_TRUE(binder.unbind(creature));
	EXPECT_FALSE(binder.ownerOf(creature).has_value());
}

TEST(InstanceCreatureBinderTest, InheritanceAndRelationsUseAuthoritativeOwner) {
	InstanceManager manager({ region(0, 100), region(1, 200) });
	const auto first = manager.createInstance({ .name = "first" });
	const auto second = manager.createInstance({ .name = "second" });
	InstanceCreatureBinder binder(manager);
	ASSERT_TRUE(binder.bind(first.id, 10));
	ASSERT_TRUE(binder.bind(second.id, 20));

	EXPECT_TRUE(binder.inherit(10, 11));
	EXPECT_EQ(InstanceCreatureRelation::SameInstance, binder.relation(10, 11));
	EXPECT_TRUE(binder.canInteract(10, 11));
	EXPECT_FALSE(binder.inherit(10, 20));
	EXPECT_EQ(InstanceCreatureRelation::Isolated, binder.relation(10, 20));
	EXPECT_FALSE(binder.canInteract(10, 20));
}

TEST(InstanceCreatureBinderTest, FailedMasterMutationRollsBackNewlyInheritedOwner) {
	InstanceManager manager({ region(0, 100) });
	const auto instance = manager.createInstance({ .name = "test" });
	InstanceCreatureBinder binder(manager);
	ASSERT_TRUE(binder.bind(instance.id, 10));

	EXPECT_FALSE(binder.inheritAndApply(10, 11, [] { return false; }));
	EXPECT_FALSE(binder.ownerOf(11).has_value());

	EXPECT_TRUE(binder.inheritAndApply(10, 11, [] { return true; }));
	ASSERT_TRUE(binder.ownerOf(11).has_value());
	EXPECT_EQ(instance.id, *binder.ownerOf(11));
}
