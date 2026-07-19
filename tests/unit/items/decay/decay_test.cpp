/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include <gtest/gtest.h>

#include "items/cylinder.hpp"
#include "items/decay/decay.hpp"
#include "items/item.hpp"

namespace {
	class ScopedDecayItemType {
	public:
		ScopedDecayItemType() :
			originalSize(Item::items.getItems().size()) {
			auto &items = Item::items.getItems();
			if (items.empty()) {
				items.resize(1);
			} else {
				originalId = items[0].id;
				originalDecayTime = items[0].decayTime;
				originalDecayTo = items[0].decayTo;
			}

			auto &itemType = items[0];
			itemType.id = 0;
			itemType.decayTime = 3600;
			itemType.decayTo = 0;
		}

		~ScopedDecayItemType() {
			auto &items = Item::items.getItems();
			if (originalSize == 0) {
				items.resize(0);
				return;
			}

			auto &itemType = items[0];
			itemType.id = originalId;
			itemType.decayTime = originalDecayTime;
			itemType.decayTo = originalDecayTo;
		}

		ItemType &type() {
			return Item::items.getItems()[0];
		}

	private:
		size_t originalSize;
		uint16_t originalId = 0;
		uint32_t originalDecayTime = 0;
		int32_t originalDecayTo = -1;
	};
} // namespace

TEST(ItemDecayReuseTest, PreservesStartStopAndRestartLifecycle) {
	const ScopedDecayItemType itemTypeRegistry;
	const auto parent = std::make_shared<VirtualCylinder>();
	const auto item = std::make_shared<Item>(0);
	item->setParent(parent);

	ASSERT_TRUE(item->canDecay());
	const auto initialDuration = item->getDuration();
	ASSERT_EQ(initialDuration, 3600000);

	auto &decay = g_decay();
	decay.startDecay(item);

	EXPECT_EQ(item->getDecaying(), DECAYING_TRUE);
	EXPECT_TRUE(item->hasAttribute(ItemAttribute_t::DURATION_TIMESTAMP));
	EXPECT_GT(item->getAttribute<int64_t>(ItemAttribute_t::DURATION_TIMESTAMP), 0);
	EXPECT_GT(item->getDuration(), 0);
	EXPECT_LE(item->getDuration(), initialDuration);

	decay.stopDecay(item);

	EXPECT_EQ(item->getDecaying(), DECAYING_FALSE);
	EXPECT_FALSE(item->hasAttribute(ItemAttribute_t::DECAYSTATE));
	const auto stoppedDuration = item->getDuration();
	EXPECT_GT(stoppedDuration, 0);
	EXPECT_LE(stoppedDuration, initialDuration);

	decay.startDecay(item);
	EXPECT_EQ(item->getDecaying(), DECAYING_TRUE);
	EXPECT_TRUE(item->hasAttribute(ItemAttribute_t::DURATION_TIMESTAMP));

	decay.stopDecay(item);
	EXPECT_EQ(item->getDecaying(), DECAYING_FALSE);
}

TEST(ItemDecayReuseTest, RejectsNonDecayableAndClearsStoppingState) {
	ScopedDecayItemType itemTypeRegistry;
	const auto parent = std::make_shared<VirtualCylinder>();
	const auto item = std::make_shared<Item>(0);
	item->setParent(parent);

	itemTypeRegistry.type().decayTo = -1;
	ASSERT_FALSE(item->canDecay());

	auto &decay = g_decay();
	decay.startDecay(item);

	EXPECT_EQ(item->getDecaying(), DECAYING_FALSE);
	EXPECT_FALSE(item->hasAttribute(ItemAttribute_t::DECAYSTATE));
	EXPECT_FALSE(item->hasAttribute(ItemAttribute_t::DURATION_TIMESTAMP));

	itemTypeRegistry.type().decayTo = 0;
	item->setDecaying(DECAYING_STOPPING);
	ASSERT_TRUE(item->hasAttribute(ItemAttribute_t::DECAYSTATE));

	decay.startDecay(item);

	EXPECT_EQ(item->getDecaying(), DECAYING_FALSE);
	EXPECT_FALSE(item->hasAttribute(ItemAttribute_t::DECAYSTATE));
	EXPECT_FALSE(item->hasAttribute(ItemAttribute_t::DURATION_TIMESTAMP));
}
