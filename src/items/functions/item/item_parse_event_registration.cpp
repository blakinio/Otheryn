/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "items/functions/item/item_parse.hpp"
#include "items/functions/item/item_parse_policy.hpp"

void ItemParse::createAndRegisterScript(ItemType &itemType, pugi::xml_node attributeNode, MoveEvent_t eventType) {
	createAndRegisterScript(itemType, attributeNode, eventType, WEAPON_NONE);
	if (ItemParsePolicy::shouldRegisterAddItemField(eventType == MOVE_EVENT_STEP_IN, itemType.isMagicField())) {
		createAndRegisterScript(itemType, attributeNode, MOVE_EVENT_ADD_ITEM_ITEMTILE, WEAPON_NONE);
	}
}
