#!/usr/bin/env python3
from pathlib import Path

path = Path("src/map/house/house.cpp")
text = path.read_text(encoding="utf-8")

replacements = [
    (
        "\tif (const TileItemVector* items = tile->getItemList()) {\n\t\tfor (const auto &item : *items) {\n",
        "\tif (const TileItemVector* items = tile->getItemList()) {\n\t\tconst auto itemsSnapshot = *items;\n\t\tfor (const auto &item : itemsSnapshot) {\n\t\t\tif (!item || item->getParent().get() != tile.get()) {\n\t\t\t\tcontinue;\n\t\t\t}\n\n",
    ),
    (
        "\tstd::unordered_set<std::shared_ptr<Player>> playersToSave = { player };\n\tfor (const auto &item : moveItemList) {\n",
        "\tstd::unordered_set<std::shared_ptr<Player>> playersToSave = { player };\n\tstd::unordered_set<const Item*> processedItems;\n\tfor (const auto &item : moveItemList) {\n\t\tif (!item || !processedItems.insert(item.get()).second) {\n\t\t\tcontinue;\n\t\t}\n\n",
    ),
    (
        "\tconst auto &newItem = g_game().wrapItem(item, houseTile->getHouse());\n\tif (newItem->isRemoved() && !newItem->getParent()) {\n\t\tg_logger().warn(\"[{}] item removed during wrapping - check ground type - player name: {} item id: {} position: {}\", __FUNCTION__, player->getName(), item->getID(), houseTile->getPosition().toString());\n",
        "\tconst auto originalItemId = item->getID();\n\tconst auto &newItem = g_game().wrapItem(item, houseTile->getHouse());\n\tif (!newItem || newItem->isRemoved() || !newItem->getParent()) {\n\t\tg_logger().warn(\"[{}] item removed during wrapping - check ground type - player name: {} item id: {} position: {}\", __FUNCTION__, player->getName(), originalItemId, houseTile->getPosition().toString());\n",
    ),
    (
        "\tfor (const auto &item : container->getItemList()) {\n\t\tif (!item) {\n",
        "\tconst auto itemsSnapshot = container->getItemList();\n\tfor (const auto &item : itemsSnapshot) {\n\t\tif (!item || item->getParent().get() != container.get()) {\n",
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one precondition match, found {count}: {old!r}")
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("materialized OAM-027 house transfer safety patch")
