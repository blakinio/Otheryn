from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected exactly one match, found {count}: {old[:120]!r}")
    file_path.write_text(text.replace(old, new, 1), encoding="utf-8")


def regex_replace_once(path: str, pattern: str, repl: str) -> None:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, repl, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"{path}: expected exactly one regex match, found {count}: {pattern}")
    file_path.write_text(updated, encoding="utf-8")


def create_exact(path: str, content: str) -> None:
    file_path = ROOT / path
    if file_path.exists():
        raise RuntimeError(f"{path}: refusing to overwrite existing file")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")


STORAGE_POLICY = r'''/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include <cstdint>

namespace ImbuementStoragePolicy {
	template <typename StorageReader>
	[[nodiscard]] bool shouldHide(bool storageFilteringEnabled, uint32_t storageId, uint16_t baseId, StorageReader &&readStorage) {
		if (!storageFilteringEnabled || storageId == 0 || baseId < 1 || baseId > 3) {
			return false;
		}

		return readStorage(storageId) == -1;
	}
} // namespace ImbuementStoragePolicy
'''

ACCESS_POLICY = r'''/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#pragma once

#include "creatures/players/imbuements/imbuement_storage_policy.hpp"

namespace ImbuementAccessPolicy {
	template <typename StorageReader>
	[[nodiscard]] bool canApplyDirectly(
		bool storageFilteringEnabled,
		bool playerPremium,
		bool imbuementPremium,
		uint32_t storageId,
		uint16_t baseId,
		StorageReader &&readStorage
	) {
		if (imbuementPremium && !playerPremium) {
			return false;
		}

		return !ImbuementStoragePolicy::shouldHide(
			storageFilteringEnabled,
			storageId,
			baseId,
			readStorage
		);
	}
} // namespace ImbuementAccessPolicy
'''

TEST_FILE = r'''#include "pch.hpp"

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

		const auto intricateVibrancy = findImbuement("Vibrancy", 2);
		const auto powerfulVibrancy = findImbuement("Vibrancy", 3);
		const auto powerfulFeatherweight = findImbuement("Featherweight", 3);
		ASSERT_TRUE(intricateVibrancy);
		ASSERT_TRUE(powerfulVibrancy);
		ASSERT_TRUE(powerfulFeatherweight);
		EXPECT_EQ(46365, powerfulVibrancy.attribute("storage").as_int());
		EXPECT_EQ(45929, powerfulFeatherweight.attribute("storage").as_int());

		auto scrollValue = [](const pugi::xml_node &node) {
			for (const auto child : node.children("attribute")) {
				if (std::string(child.attribute("key").as_string()) == "scroll") {
					return child.attribute("value").as_int();
				}
			}
			return 0;
		};
		EXPECT_EQ(51746, scrollValue(intricateVibrancy));
		EXPECT_EQ(51466, scrollValue(powerfulVibrancy));
	}

} // namespace
'''


def materialize() -> None:
    create_exact("src/creatures/players/imbuements/imbuement_storage_policy.hpp", STORAGE_POLICY)
    create_exact("src/creatures/players/imbuements/imbuement_access_policy.hpp", ACCESS_POLICY)

    replace_once(
        "src/creatures/players/imbuements/imbuements.cpp",
        '#include "creatures/players/imbuements/imbuements.hpp"\n',
        '#include "creatures/players/imbuements/imbuements.hpp"\n#include "creatures/players/imbuements/imbuement_storage_policy.hpp"\n',
    )
    replace_once(
        "src/creatures/players/imbuements/imbuements.cpp",
        '''\t\tif (g_configManager().getBoolean(TOGGLE_IMBUEMENT_SHRINE_STORAGE)\n\t\t    && imbuement->getStorage() != 0\n\t\t    && player->getStorageValue(imbuement->getStorage() == -1)\n\t\t    && imbuement->getBaseID() >= 1 && imbuement->getBaseID() <= 3) {\n\t\t\tcontinue;\n\t\t}\n''',
        '''\t\tif (ImbuementStoragePolicy::shouldHide(\n\t\t\t\tg_configManager().getBoolean(TOGGLE_IMBUEMENT_SHRINE_STORAGE),\n\t\t\t\timbuement->getStorage(),\n\t\t\t\timbuement->getBaseID(),\n\t\t\t\t[&player](uint32_t storageId) {\n\t\t\t\t\treturn player->getStorageValue(storageId);\n\t\t\t\t}\n\t\t\t)) {\n\t\t\tcontinue;\n\t\t}\n''',
    )

    replace_once(
        "src/creatures/players/player.cpp",
        '#include "creatures/players/imbuements/imbuements.hpp"\n#include "creatures/players/storages/storages.hpp"\n',
        '#include "creatures/players/imbuements/imbuements.hpp"\n#include "creatures/players/imbuements/imbuement_access_policy.hpp"\n#include "creatures/players/storages/storages.hpp"\n',
    )
    replace_once(
        "src/creatures/players/player.cpp",
        '''\t\treturn false;\n\t}\n}\n\nMuteCountMap Player::muteCountMap;\n''',
        '''\t\treturn false;\n\t}\n\n\t[[nodiscard]] bool canApplyImbuementDirectly(const std::shared_ptr<Player> &player, const Imbuement* imbuement) {\n\t\tif (!player || !imbuement) {\n\t\t\treturn false;\n\t\t}\n\n\t\tconst bool allowed = ImbuementAccessPolicy::canApplyDirectly(\n\t\t\tg_configManager().getBoolean(TOGGLE_IMBUEMENT_SHRINE_STORAGE),\n\t\t\tplayer->isPremium(),\n\t\t\timbuement->isPremium(),\n\t\t\timbuement->getStorage(),\n\t\t\timbuement->getBaseID(),\n\t\t\t[&player](uint32_t storageId) {\n\t\t\t\treturn player->getStorageValue(storageId);\n\t\t\t}\n\t\t);\n\t\tif (allowed) {\n\t\t\treturn true;\n\t\t}\n\n\t\tif (imbuement->isPremium() && !player->isPremium()) {\n\t\t\tplayer->sendImbuementResult("You need a premium account to use this imbuement.");\n\t\t} else {\n\t\t\tplayer->sendImbuementResult("You have not unlocked this imbuement.");\n\t\t}\n\t\treturn false;\n\t}\n}\n\nMuteCountMap Player::muteCountMap;\n''',
    )
    replace_once(
        "src/creatures/players/player.cpp",
        '''void Player::createScrollImbuement(const Imbuement* imbuement) {\n\tif (!imbuement) {\n\t\treturn;\n\t}\n\n\tconst BaseImbuement* baseImbuement = g_imbuements().getBaseByID(imbuement->getBaseID());\n''',
        '''void Player::createScrollImbuement(const Imbuement* imbuement) {\n\tif (!imbuement) {\n\t\treturn;\n\t}\n\n\tif (!canApplyImbuementDirectly(getPlayer(), imbuement)) {\n\t\treturn;\n\t}\n\n\tconst BaseImbuement* baseImbuement = g_imbuements().getBaseByID(imbuement->getBaseID());\n''',
    )
    replace_once(
        "src/creatures/players/player.cpp",
        '''\tconst auto &thisPlayer = getPlayer();\n\tif (!item->canAddImbuement(slot, thisPlayer, imbuement)) {\n''',
        '''\tconst auto &thisPlayer = getPlayer();\n\tif (!canApplyImbuementDirectly(thisPlayer, imbuement)) {\n\t\treturn;\n\t}\n\n\tif (!item->canAddImbuement(slot, thisPlayer, imbuement)) {\n''',
    )

    xml_path = ROOT / "data/XML/imbuements.xml"
    xml = xml_path.read_text(encoding="utf-8")

    exact_replacements = {
        '<base id="1" name="Basic" price="5000" protectionPrice="10000" percent="90" removecost="15000" duration="72000" />': '<base id="1" name="Basic" price="7500" protectionPrice="0" percent="100" removecost="15000" duration="72000" />',
        '<base id="2" name="Intricate" price="30000" protectionPrice="30000" percent="70" removecost="15000" duration="72000" />': '<base id="2" name="Intricate" price="60000" protectionPrice="0" percent="100" removecost="15000" duration="72000" />',
        '<base id="3" name="Powerful" price="200000" protectionPrice="50000" percent="50" removecost="15000" duration="72000" />': '<base id="3" name="Powerful" price="250000" protectionPrice="0" percent="100" removecost="15000" duration="72000" />',
        '<attribute key="description" value="Raises crit hit damage by 15% and crit hit chance by 10%." />': '<attribute key="description" value="Raises critical hit damage by 5% and critical hit chance by 5%." />',
        '<attribute key="effect" type="skill" value="critical" bonus="1500" chance="1000" />': '<attribute key="effect" type="skill" value="critical" bonus="500" chance="500" />',
        '<attribute key="description" value="Raises crit hit damage by 25% and crit hit chance by 10%." />': '<attribute key="description" value="Raises critical hit damage by 15% and critical hit chance by 5%." />',
        '<attribute key="effect" type="skill" value="critical" bonus="2500" chance="1000" />': '<attribute key="effect" type="skill" value="critical" bonus="1500" chance="500" />',
        '<attribute key="description" value="Raises crit hit damage by 50% and crit hit chance by 10%." />': '<attribute key="description" value="Raises critical hit damage by 40% and critical hit chance by 5%." />',
        '<attribute key="effect" type="skill" value="critical" bonus="5000" chance="1000" />': '<attribute key="effect" type="skill" value="critical" bonus="4000" chance="500" />',
        '<attribute key="item" value="9690" count="20" />': '<attribute key="item" value="10281" count="25" />',
    }
    for old, new in exact_replacements.items():
        count = xml.count(old)
        if count != 1:
            raise RuntimeError(f"data/XML/imbuements.xml: expected one exact replacement, found {count}: {old}")
        xml = xml.replace(old, new, 1)

    storage_groups = {
        45489: (50488, ["Reap", "Vampirism", "Lich Shroud"]),
        45490: (50490, ["Electrify", "Cloud Fabric", "Swiftness"]),
        45491: (50492, ["Venom", "Snake Skin", "Chop", "Slash", "Bash", "Punch"]),
        45492: (50494, ["Scorch", "Void", "Dragon Hide"]),
        45493: (50496, ["Frost", "Quara Scale", "Blockade"]),
        45494: (50498, ["Demon Presence", "Precision"]),
        45495: (50501, ["Strike", "Epiphany"]),
    }
    for new_storage, (old_storage, names) in storage_groups.items():
        for name in names:
            pattern = rf'(<imbuement name="{re.escape(name)}" base="3"[^>]* storage="){old_storage}("[^>]*>)'
            xml, count = re.subn(pattern, rf'\g<1>{new_storage}\2', xml, count=1)
            if count != 1:
                raise RuntimeError(f"storage replacement failed for {name}: expected {old_storage}")

    for name, storage in (("Vibrancy", 46365), ("Featherweight", 45929)):
        pattern = rf'(<imbuement name="{name}" base="3"[^>]* storage=")0("[^>]*>)'
        xml, count = re.subn(pattern, rf'\g<1>{storage}\2', xml, count=1)
        if count != 1:
            raise RuntimeError(f"unlock storage replacement failed for {name}")

    def add_scroll(xml_text: str, base: int, scroll_id: int) -> str:
        pattern = rf'(<imbuement name="Vibrancy" base="{base}"[\s\S]*?)(\n\t</imbuement>)'
        match = re.search(pattern, xml_text)
        if not match:
            raise RuntimeError(f"Vibrancy base {base} block not found")
        block = match.group(1)
        if 'key="scroll"' in block:
            raise RuntimeError(f"Vibrancy base {base} already has a scroll mapping")
        replacement = block + f'\n\t\t<attribute key="scroll" value="{scroll_id}" />' + match.group(2)
        return xml_text[:match.start()] + replacement + xml_text[match.end():]

    xml = add_scroll(xml, 2, 51746)
    xml = add_scroll(xml, 3, 51466)
    xml_path.write_text(xml, encoding="utf-8")

    create_exact("tests/unit/players/imbuements/oam_019_imbuements_adapt_test.cpp", TEST_FILE)
    replace_once(
        "tests/unit/players/imbuements/CMakeLists.txt",
        "    PRIVATE imbuements_test.cpp\n",
        "    PRIVATE imbuements_test.cpp oam_019_imbuements_adapt_test.cpp imbuement_storage_policy_test.cpp\n",
    )

    storage_test = r'''#include "pch.hpp"

#include <gtest/gtest.h>

#include "creatures/players/imbuements/imbuement_storage_policy.hpp"

TEST(ImbuementStoragePolicyTest, ReadsTheConfiguredStorageId) {
	uint32_t requestedStorage = 0;
	const bool hidden = ImbuementStoragePolicy::shouldHide(true, 30059, 3, [&requestedStorage](uint32_t storageId) {
		requestedStorage = storageId;
		return -1;
	});

	EXPECT_TRUE(hidden);
	EXPECT_EQ(30059, requestedStorage);
}
'''
    create_exact("tests/unit/players/imbuements/imbuement_storage_policy_test.cpp", storage_test)


if __name__ == "__main__":
    materialize()
