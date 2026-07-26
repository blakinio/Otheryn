#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

#include "creatures/players/player.hpp"
#include "lib/di/container.hpp"
#include "lib/logging/in_memory_logger.hpp"

namespace {
	constexpr uint32_t huntingTaskShopPointsStorage = 1000006;

	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM051_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}
} // namespace

class Oam051bTaskShopAdaptTest : public ::testing::Test {
protected:
	static void SetUpTestSuite() {
		previousTestContainer = DI::getTestContainer();
		InMemoryLogger::install(injector);
		DI::setTestContainer(&injector);
	}

	static void TearDownTestSuite() {
		DI::setTestContainer(previousTestContainer);
	}

	static std::shared_ptr<Player> makePlayer(uint32_t level = 50) {
		auto player = std::make_shared<Player>();
		player->setLevel(level);
		return player;
	}

	inline static di::extension::injector<> injector {};
	inline static di::extension::injector<>* previousTestContainer = nullptr;
};

TEST_F(Oam051bTaskShopAdaptTest, StorageBackedPurchasesContributeToWheelPoints) {
	auto player = makePlayer();
	EXPECT_EQ(0, player->wheel().getExtraPoints());

	player->addStorageValue(huntingTaskShopPointsStorage, 7);
	EXPECT_EQ(7, player->wheel().getExtraPoints());
	EXPECT_EQ(7, player->wheel().getWheelPoints());

	player->addStorageValue(huntingTaskShopPointsStorage, 99);
	EXPECT_EQ(50, player->wheel().getExtraPoints());
}

TEST_F(Oam051bTaskShopAdaptTest, StorageReservationIsNamedAndSchemaFree) {
	const auto source = readSource("data/XML/storages.xml");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("<storage name=\"wheel.hunting_task_shop_points\" key=\"6\" />"), std::string::npos);
	EXPECT_EQ(source.find("CREATE TABLE"), std::string::npos);
}

TEST_F(Oam051bTaskShopAdaptTest, ShopPublishesExactBonusPromotionContract) {
	const auto source = readSource("data/modules/scripts/taskboard/taskboard.lua");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("BonusPromotion = 0x04"), std::string::npos);
	EXPECT_NE(source.find("BonusPromotion = 0"), std::string::npos);
	EXPECT_NE(source.find("BonusPromotionPoints = 1000006"), std::string::npos);
	EXPECT_NE(source.find("MaxBonusPromotionPoints = 50"), std::string::npos);
	EXPECT_NE(source.find("100 * (1 + nextPoint * (nextPoint - 1) / 2)"), std::string::npos);
	EXPECT_NE(source.find("msg:addByte(1) -- offer count"), std::string::npos);
	EXPECT_NE(source.find("msg:addByte(OfferType.BonusPromotion)"), std::string::npos);
	EXPECT_NE(source.find("msg:addU16(purchasedPoints + 1)"), std::string::npos);
	EXPECT_NE(source.find("msg:addU32(nextCost)"), std::string::npos);
	EXPECT_NE(source.find("msg:addByte(status)"), std::string::npos);
}

TEST_F(Oam051bTaskShopAdaptTest, PurchaseMutationRollsBackAndRejectsReplayBoundaries) {
	const auto source = readSource("data/modules/scripts/taskboard/taskboard.lua");
	ASSERT_FALSE(source.empty());

	const auto functionStart = source.find("local function purchaseBonusPromotion");
	ASSERT_NE(functionStart, std::string::npos);
	const auto functionEnd = source.find("local function sendShopWindow", functionStart);
	ASSERT_NE(functionEnd, std::string::npos);
	const auto function = source.substr(functionStart, functionEnd - functionStart);

	EXPECT_NE(function.find("offerId ~= OfferId.BonusPromotion"), std::string::npos);
	EXPECT_NE(function.find("purchasedPoints >= MaxBonusPromotionPoints"), std::string::npos);
	EXPECT_NE(function.find("player:getTaskHuntingPoints() < cost"), std::string::npos);
	EXPECT_NE(function.find("player:setStorageValue(Storage.BonusPromotionPoints, purchasedPoints + 1)"), std::string::npos);
	EXPECT_NE(function.find("player:removeTaskHuntingPoints(cost)"), std::string::npos);
	EXPECT_NE(function.find("player:setStorageValue(Storage.BonusPromotionPoints, purchasedPoints)"), std::string::npos);
	EXPECT_EQ(function.find(":kv()"), std::string::npos);
	EXPECT_EQ(function.find("wheel-of-destiny"), std::string::npos);
}

TEST_F(Oam051bTaskShopAdaptTest, ShopBuyParserIsExactAndFailClosed) {
	const auto source = readSource("data/modules/scripts/taskboard/taskboard.lua");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("local offerId = readU16(msg)"), std::string::npos);
	EXPECT_NE(source.find("if not offerId then"), std::string::npos);
	EXPECT_NE(source.find("local trailingBytes = msg:getUnreadBytes()"), std::string::npos);
	EXPECT_NE(source.find("if trailingBytes > 0 then"), std::string::npos);
	EXPECT_NE(source.find("purchaseBonusPromotion(player, offerId)"), std::string::npos);
}

TEST_F(Oam051bTaskShopAdaptTest, ExistingEmptyBountyAndWeeklyShimsRemainBounded) {
	const auto source = readSource("data/modules/scripts/taskboard/taskboard.lua");
	ASSERT_FALSE(source.empty());

	EXPECT_NE(source.find("msg:addByte(0) -- bounty task count"), std::string::npos);
	EXPECT_NE(source.find("msg:addByte(0) -- weekly kill task count"), std::string::npos);
	EXPECT_NE(source.find("msg:addByte(0) -- weekly item task count"), std::string::npos);
}

TEST_F(Oam051bTaskShopAdaptTest, PlayerStoragesLoadBeforeWheelAllocationValidation) {
	const auto source = readSource("src/io/functions/iologindata_load_player.cpp");
	ASSERT_FALSE(source.empty());

	const auto storages = source.find("loadPlayerStorageMap");
	const auto slots = source.find("player->wheel().loadDBPlayerSlotPointsOnLogin();");
	ASSERT_NE(storages, std::string::npos);
	ASSERT_NE(slots, std::string::npos);
	EXPECT_LT(storages, slots);
}
