#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readHouseSource() {
		std::ifstream input(std::string(OAM027_SOURCE_DIR) + "/src/map/house/house.cpp");
		EXPECT_TRUE(input.is_open());
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

TEST(Oam027HousesAdaptTest, GuardsReviewedHouseTransferSafetyContract) {
	const auto source = readHouseSource();
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("const auto itemsSnapshot = *items;"), std::string::npos);
	EXPECT_NE(source.find("item->getParent().get() != tile.get()"), std::string::npos);
	EXPECT_NE(source.find("std::unordered_set<const Item*> processedItems;"), std::string::npos);
	EXPECT_NE(source.find("!processedItems.insert(item.get()).second"), std::string::npos);
	EXPECT_NE(source.find("const auto originalItemId = item->getID();"), std::string::npos);
	EXPECT_NE(source.find("if (!newItem || newItem->isRemoved() || !newItem->getParent())"), std::string::npos);
	EXPECT_NE(source.find("const auto itemsSnapshot = container->getItemList();"), std::string::npos);
	EXPECT_NE(source.find("item->getParent().get() != container.get()"), std::string::npos);
}
