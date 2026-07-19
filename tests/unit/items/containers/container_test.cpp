/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019-2023 OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include <gtest/gtest.h>

#include "items/containers/container.hpp"

namespace {
	class ScopedItemTypeRegistry {
	public:
		ScopedItemTypeRegistry() :
			originalSize(Item::items.getItems().size()) {
			if (originalSize == 0) {
				Item::items.getItems().resize(1);
			}
		}

		~ScopedItemTypeRegistry() {
			Item::items.getItems().resize(originalSize);
		}

	private:
		size_t originalSize;
	};
} // namespace

TEST(ContainerReuseTest, PreservesDirectCapacityAndItemLifecycle) {
	const ScopedItemTypeRegistry itemTypeRegistry;
	const auto container = Container::create(0, 2, true, false);
	ASSERT_NE(container, nullptr);
	EXPECT_TRUE(container->empty());
	EXPECT_EQ(container->capacity(), 2);
	EXPECT_EQ(container->getFreeSlots(), 2);

	const auto first = std::make_shared<Item>(0);
	const auto second = std::make_shared<Item>(0);

	container->addItem(first);
	EXPECT_EQ(container->size(), 1);
	EXPECT_EQ(container->getItemByIndex(0), first);
	EXPECT_EQ(container->getThingIndex(first), 0);
	EXPECT_EQ(container->getFreeSlots(), 1);
	EXPECT_TRUE(container->isHoldingItem(first));

	container->addItem(second);
	EXPECT_EQ(container->size(), 2);
	EXPECT_EQ(container->getFreeSlots(), 0);
	EXPECT_EQ(container->getItemByIndex(1), second);

	container->removeItem(first);
	EXPECT_EQ(container->size(), 1);
	EXPECT_EQ(container->getThingIndex(first), -1);
	EXPECT_EQ(container->getFreeSlots(), 1);
}

TEST(ContainerReuseTest, PreservesBoundedNestedTraversal) {
	const ScopedItemTypeRegistry itemTypeRegistry;
	const auto root = Container::create(0, 4, true, false);
	const auto nested = Container::create(0, 4, true, false);
	const auto leaf = std::make_shared<Item>(0);

	nested->addItem(leaf);
	root->addItem(nested);

	ContainerIterator iterator(root, 2);
	ASSERT_TRUE(iterator.hasNext());
	EXPECT_EQ(*iterator, nested);
	iterator.advance();
	ASSERT_TRUE(iterator.hasNext());
	EXPECT_EQ(*iterator, leaf);
	iterator.advance();
	EXPECT_FALSE(iterator.hasNext());
	EXPECT_FALSE(iterator.hasReachedMaxDepth());

	ContainerIterator shallowIterator(root, 1);
	ASSERT_TRUE(shallowIterator.hasNext());
	EXPECT_EQ(*shallowIterator, nested);
	shallowIterator.advance();
	EXPECT_TRUE(shallowIterator.hasReachedMaxDepth());
	EXPECT_FALSE(shallowIterator.hasNext());
}
