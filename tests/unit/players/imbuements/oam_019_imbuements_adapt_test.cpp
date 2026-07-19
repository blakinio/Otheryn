#include "pch.hpp"

#include <filesystem>
#include <string>
#include <unordered_map>

#include <gtest/gtest.h>
#include <pugixml.hpp>

#include "creatures/players/imbuements/imbuement_access_policy.hpp"
#include "creatures/players/imbuements/imbuement_storage_policy.hpp"
#include "../../../shared/imbuements/imbuements_test_fixture.hpp"

namespace {

	class Oam019ImbuementsAdaptTest : public test::imbuements::ImbuementsTestBase {
	};

	TEST_F(Oam019ImbuementsAdaptTest, StoragePolicyReadsConfiguredStorageAndFailsClosed) {
		uint32_t requestedStorage = 0;
		EXPECT_TRUE(ImbuementStoragePolicy::shouldHide(true, 30059, 3, [&requestedStorage](uint32_t storageId) {
			requestedStorage = storageId;
			return -1;
		}));
		EXPECT_EQ(30059, requestedStorage);

		EXPECT_FALSE(ImbuementStoragePolicy::shouldHide(true, 30059, 3, [](uint32_t) {
			return 1;
		}));
	}

	TEST_F(Oam019ImbuementsAdaptTest, DirectAccessPolicyEnforcesPremiumAndStorage) {
		EXPECT_FALSE(ImbuementAccessPolicy::canApplyDirectly(false, false, true, 0, 2, [](uint32_t) {
			return 1;
		}));
		EXPECT_FALSE(ImbuementAccessPolicy::canApplyDirectly(true, true, true, 45495, 3, [](uint32_t) {
			return -1;
		}));
		EXPECT_TRUE(ImbuementAccessPolicy::canApplyDirectly(true, true, true, 45495, 3, [](uint32_t) {
			return 1;
		}));
		EXPECT_TRUE(ImbuementAccessPolicy::canApplyDirectly(false, true, true, 45495, 3, [](uint32_t) {
			return -1;
		}));
	}

	TEST_F(Oam019ImbuementsAdaptTest, ProductionRegistryContainsAcceptedDonorContract) {
		pugi::xml_document doc;
		ASSERT_TRUE(doc.load_file("data/XML/imbuements.xml"));
		const auto root = doc.child("imbuements");
		ASSERT_TRUE(root);

		std::unordered_map<int, pugi::xml_node> bases;
		for (const auto node : root.children("base")) {
			bases.emplace(node.attribute("id").as_int(), node);
		}
		ASSERT_EQ(3U, bases.size());
		EXPECT_EQ(7500, bases.at(1).attribute("price").as_int());
		EXPECT_EQ(60000, bases.at(2).attribute("price").as_int());
		EXPECT_EQ(250000, bases.at(3).attribute("price").as_int());
		for (int id = 1; id <= 3; ++id) {
			EXPECT_EQ(100, bases.at(id).attribute("percent").as_int());
			EXPECT_EQ(0, bases.at(id).attribute("protectionPrice").as_int());
		}

		const std::unordered_map<std::string, int> expectedStorage {
			{ "Reap", 45489 }, { "Vampirism", 45489 }, { "Lich Shroud", 45489 },
			{ "Electrify", 45490 }, { "Cloud Fabric", 45490 }, { "Swiftness", 45490 },
			{ "Venom", 45491 }, { "Snake Skin", 45491 }, { "Chop", 45491 }, { "Slash", 45491 }, { "Bash", 45491 }, { "Punch", 45491 },
			{ "Scorch", 45492 }, { "Void", 45492 }, { "Dragon Hide", 45492 },
			{ "Frost", 45493 }, { "Quara Scale", 45493 }, { "Blockade", 45493 },
			{ "Demon Presence", 45494 }, { "Precision", 45494 },
			{ "Strike", 45495 }, { "Epiphany", 45495 },
		};

		std::unordered_map<std::string, int> observedPowerfulStorage;
		for (const auto node : root.children("imbuement")) {
			if (node.attribute("base").as_int() == 3) {
				const std::string name = node.attribute("name").as_string();
				if (expectedStorage.contains(name)) {
					observedPowerfulStorage[name] = node.attribute("storage").as_int();
				}
			}
		}
		EXPECT_EQ(expectedStorage, observedPowerfulStorage);

		auto findImbuement = [&root](const char* name, int base) {
			for (const auto node : root.children("imbuement")) {
				if (std::string(node.attribute("name").as_string()) == name && node.attribute("base").as_int() == base) {
					return node;
				}
			}
			return pugi::xml_node {};
		};

		auto findAttribute = [](const pugi::xml_node &node, const char* key) {
			for (const auto child : node.children("attribute")) {
				if (std::string(child.attribute("key").as_string()) == key) {
					return child;
				}
			}
			return pugi::xml_node {};
		};

		const auto intricateVibrancy = findImbuement("Vibrancy", 2);
		const auto powerfulVibrancy = findImbuement("Vibrancy", 3);
		const auto powerfulFeatherweight = findImbuement("Featherweight", 3);
		ASSERT_TRUE(intricateVibrancy);
		ASSERT_TRUE(powerfulVibrancy);
		ASSERT_TRUE(powerfulFeatherweight);
		EXPECT_EQ(46365, powerfulVibrancy.attribute("storage").as_int());
		EXPECT_EQ(45929, powerfulFeatherweight.attribute("storage").as_int());
		EXPECT_EQ(51746, findAttribute(intricateVibrancy, "scroll").attribute("value").as_int());
		EXPECT_EQ(51466, findAttribute(powerfulVibrancy, "scroll").attribute("value").as_int());

		const std::array expectedStrike {
			std::tuple { 1, 500, 500 },
			std::tuple { 2, 1500, 500 },
			std::tuple { 3, 4000, 500 },
		};
		for (const auto &[base, bonus, chance] : expectedStrike) {
			const auto strike = findImbuement("Strike", base);
			ASSERT_TRUE(strike);
			const auto effect = findAttribute(strike, "effect");
			ASSERT_TRUE(effect);
			EXPECT_STREQ("critical", effect.attribute("value").as_string());
			EXPECT_EQ(bonus, effect.attribute("bonus").as_int());
			EXPECT_EQ(chance, effect.attribute("chance").as_int());
		}

		const auto basicPunch = findImbuement("Punch", 1);
		ASSERT_TRUE(basicPunch);
		const auto punchItem = findAttribute(basicPunch, "item");
		ASSERT_TRUE(punchItem);
		EXPECT_EQ(10281, punchItem.attribute("value").as_int());
		EXPECT_EQ(25, punchItem.attribute("count").as_int());
	}

} // namespace
