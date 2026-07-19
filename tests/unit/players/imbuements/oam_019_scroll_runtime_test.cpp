#include "pch.hpp"

#include <gtest/gtest.h>

#include "creatures/players/imbuements/imbuements.hpp"
#include "creatures/players/player.hpp"
#include "items/containers/inbox/inbox.hpp"
#include "items/item.hpp"
#include "../../../shared/imbuements/imbuements_test_fixture.hpp"

namespace {

	class Oam019ImbuementScrollRuntimeTest : public test::imbuements::ImbuementsTestBase {
	protected:
		static constexpr uint16_t kValidBootsId = 65010;
		static constexpr uint16_t kInvalidTargetId = 65011;
		static constexpr uint16_t kIntricateScrollId = 51746;
		static constexpr uint16_t kPowerfulScrollId = 51466;

		static void SetUpTestSuite() {
			ImbuementsTestBase::SetUpTestSuite();
			auto &items = Item::items.getItems();
			originalItemsSize = items.size();
			saveItem(items, kValidBootsId, originalValidBoots);
			saveItem(items, kInvalidTargetId, originalInvalidTarget);
			saveItem(items, kIntricateScrollId, originalIntricateScroll);
			saveItem(items, kPowerfulScrollId, originalPowerfulScroll);

			const auto requiredSize = static_cast<size_t>(std::max({ kValidBootsId, kInvalidTargetId, kIntricateScrollId, kPowerfulScrollId })) + 1;
			if (items.size() < requiredSize) {
				items.resize(requiredSize);
			}

			configureTarget(items[kValidBootsId], kValidBootsId, true);
			configureTarget(items[kInvalidTargetId], kInvalidTargetId, false);
			configureScroll(items[kIntricateScrollId], kIntricateScrollId);
			configureScroll(items[kPowerfulScrollId], kPowerfulScrollId);
		}

		static void TearDownTestSuite() {
			auto &items = Item::items.getItems();
			restoreItem(items, kValidBootsId, originalValidBoots);
			restoreItem(items, kInvalidTargetId, originalInvalidTarget);
			restoreItem(items, kIntricateScrollId, originalIntricateScroll);
			restoreItem(items, kPowerfulScrollId, originalPowerfulScroll);
			if (items.size() > originalItemsSize) {
				items.resize(originalItemsSize);
			}
			ImbuementsTestBase::TearDownTestSuite();
		}

		static std::shared_ptr<Player> makePlayer() {
			return std::make_shared<Player>(std::shared_ptr<ProtocolGame> {});
		}

		static void saveItem(std::vector<ItemType> &items, uint16_t id, std::optional<ItemType> &saved) {
			if (id < items.size()) {
				saved.emplace(std::move(items[id]));
			}
		}

		static void restoreItem(std::vector<ItemType> &items, uint16_t id, std::optional<ItemType> &saved) {
			if (saved && id < items.size()) {
				items[id] = std::move(*saved);
			}
		}

		static void configureTarget(ItemType &itemType, uint16_t id, bool supportsVibrancy) {
			itemType = ItemType {};
			itemType.id = id;
			itemType.name = supportsVibrancy ? "test imbuable boots" : "test invalid target";
			itemType.pickupable = true;
			itemType.movable = true;
			itemType.slotPosition = SLOTP_FEET;
			itemType.imbuementSlot = 2;
			if (supportsVibrancy) {
				itemType.imbuementTypes[IMBUEMENT_PARALYSIS_DEFLECTION] = 3;
			}
		}

		static void configureScroll(ItemType &itemType, uint16_t id) {
			itemType = ItemType {};
			itemType.id = id;
			itemType.name = "test Vibrancy scroll";
			itemType.pickupable = true;
			itemType.movable = true;
		}

		inline static size_t originalItemsSize = 0;
		inline static std::optional<ItemType> originalValidBoots;
		inline static std::optional<ItemType> originalInvalidTarget;
		inline static std::optional<ItemType> originalIntricateScroll;
		inline static std::optional<ItemType> originalPowerfulScroll;
	};

	TEST_F(Oam019ImbuementScrollRuntimeTest, ResolvesIntricateAndPowerfulVibrancyScrolls) {
		const std::array expected {
			std::pair { kIntricateScrollId, uint16_t { 2 } },
			std::pair { kPowerfulScrollId, uint16_t { 3 } },
		};
		for (const auto &[scrollId, baseId] : expected) {
			const auto* imbuement = g_imbuements().getImbuementByScrollID(scrollId);
			ASSERT_NE(nullptr, imbuement);
			EXPECT_EQ("Vibrancy", imbuement->getName());
			EXPECT_EQ(baseId, imbuement->getBaseID());
			EXPECT_EQ(IMBUEMENT_PARALYSIS_DEFLECTION, imbuement->getCategory());
		}
	}

	TEST_F(Oam019ImbuementScrollRuntimeTest, AppliesEachVibrancyScrollAndConsumesExactlyOne) {
		const std::array expected {
			std::pair { kIntricateScrollId, uint16_t { 2 } },
			std::pair { kPowerfulScrollId, uint16_t { 3 } },
		};
		for (const auto &[scrollId, baseId] : expected) {
			auto player = makePlayer();
			auto inbox = player->getInbox();
			ASSERT_NE(nullptr, inbox);
			auto target = Item::CreateItem(kValidBootsId, 1);
			auto usedScroll = Item::CreateItem(scrollId, 1);
			auto spareScroll = Item::CreateItem(scrollId, 1);
			ASSERT_NE(nullptr, target);
			ASSERT_NE(nullptr, usedScroll);
			ASSERT_NE(nullptr, spareScroll);
			inbox->addThing(target);
			inbox->addThing(usedScroll);
			inbox->addThing(spareScroll);

			player->applyScrollImbuement(target, usedScroll);

			EXPECT_TRUE(usedScroll->isRemoved());
			EXPECT_FALSE(spareScroll->isRemoved());
			EXPECT_EQ(2U, inbox->size());
			ImbuementInfo info;
			ASSERT_TRUE(target->getImbuementInfo(0, &info));
			ASSERT_NE(nullptr, info.imbuement);
			EXPECT_EQ("Vibrancy", info.imbuement->getName());
			EXPECT_EQ(baseId, info.imbuement->getBaseID());
			EXPECT_EQ(72000U, info.duration);
			g_imbuementDecay().stopImbuementDecay(target);
		}
	}

	TEST_F(Oam019ImbuementScrollRuntimeTest, RejectsInvalidTargetWithoutConsumingScrollOrMutatingItem) {
		auto player = makePlayer();
		auto inbox = player->getInbox();
		ASSERT_NE(nullptr, inbox);
		auto target = Item::CreateItem(kInvalidTargetId, 1);
		auto scroll = Item::CreateItem(kIntricateScrollId, 1);
		ASSERT_NE(nullptr, target);
		ASSERT_NE(nullptr, scroll);
		inbox->addThing(target);
		inbox->addThing(scroll);

		player->applyScrollImbuement(target, scroll);

		EXPECT_FALSE(scroll->isRemoved());
		EXPECT_EQ(2U, inbox->size());
		ImbuementInfo info;
		EXPECT_FALSE(target->getImbuementInfo(0, &info));
	}

	TEST_F(Oam019ImbuementScrollRuntimeTest, RejectsOccupiedVibrancyCategoryWithoutConsumingScroll) {
		auto player = makePlayer();
		auto inbox = player->getInbox();
		ASSERT_NE(nullptr, inbox);
		auto target = Item::CreateItem(kValidBootsId, 1);
		auto scroll = Item::CreateItem(kPowerfulScrollId, 1);
		ASSERT_NE(nullptr, target);
		ASSERT_NE(nullptr, scroll);
		const auto* intricate = g_imbuements().getImbuementByScrollID(kIntricateScrollId);
		ASSERT_NE(nullptr, intricate);
		target->setImbuement(0, intricate->getID(), 72000);
		inbox->addThing(target);
		inbox->addThing(scroll);

		player->applyScrollImbuement(target, scroll);

		EXPECT_FALSE(scroll->isRemoved());
		EXPECT_EQ(2U, inbox->size());
		ImbuementInfo occupied;
		ASSERT_TRUE(target->getImbuementInfo(0, &occupied));
		EXPECT_EQ(intricate, occupied.imbuement);
		ImbuementInfo freeSlot;
		EXPECT_FALSE(target->getImbuementInfo(1, &freeSlot));
	}

} // namespace
