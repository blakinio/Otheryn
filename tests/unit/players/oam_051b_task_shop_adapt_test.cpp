#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM051_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}

	constexpr uint32_t bonusPromotionCost(uint32_t nextPoint) {
		return 100 * (1 + nextPoint * (nextPoint - 1) / 2);
	}
} // namespace

class Oam051bTaskShopAdaptTest : public ::testing::Test { };

TEST_F(Oam051bTaskShopAdaptTest, StorageBackedPurchasesContributeToWheelPoints) {
	const auto source = readSource("src/creatures/players/components/wheel/player_wheel.cpp");
	ASSERT_FALSE(source.empty());

	const auto extraStart = source.find("uint16_t PlayerWheel::getExtraPoints() const");
	const auto wheelPointsStart = source.find("uint16_t PlayerWheel::getWheelPoints", extraStart);
	const auto wheelPointsEnd = source.find("uint8_t PlayerWheel::getMaxPointsPerSlot", wheelPointsStart);
	ASSERT_NE(extraStart, std::string::npos);
	ASSERT_NE(wheelPointsStart, std::string::npos);
	ASSERT_NE(wheelPointsEnd, std::string::npos);

	const auto extraPoints = source.substr(extraStart, wheelPointsStart - extraStart);
	const auto wheelPoints = source.substr(wheelPointsStart, wheelPointsEnd - wheelPointsStart);
	EXPECT_NE(extraPoints.find("m_player.getStorageValue(1000006)"), std::string::npos);
	EXPECT_NE(extraPoints.find("std::clamp<int32_t>"), std::string::npos);
	EXPECT_NE(extraPoints.find("0, 50"), std::string::npos);
	EXPECT_NE(extraPoints.find("totalBonus += static_cast<uint32_t>(huntingTaskShopPoints)"), std::string::npos);
	EXPECT_NE(wheelPoints.find("points += getExtraPoints();"), std::string::npos);
}

TEST_F(Oam051bTaskShopAdaptTest, CostProgressionMatchesBoundedContract) {
	EXPECT_EQ(100, bonusPromotionCost(1));
	EXPECT_EQ(200, bonusPromotionCost(2));
	EXPECT_EQ(117700, bonusPromotionCost(49));
	EXPECT_EQ(122600, bonusPromotionCost(50));
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

TEST_F(Oam051bTaskShopAdaptTest, WheelAccountingUsesSqlStorageAndNoKvMirror) {
	const auto source = readSource("src/creatures/players/components/wheel/player_wheel.cpp");
	ASSERT_FALSE(source.empty());

	const auto functionStart = source.find("uint16_t PlayerWheel::getExtraPoints() const");
	ASSERT_NE(functionStart, std::string::npos);
	const auto functionEnd = source.find("uint16_t PlayerWheel::getWheelPoints", functionStart);
	ASSERT_NE(functionEnd, std::string::npos);
	const auto function = source.substr(functionStart, functionEnd - functionStart);

	EXPECT_NE(function.find("m_player.getStorageValue(1000006)"), std::string::npos);
	EXPECT_NE(function.find("std::clamp<int32_t>"), std::string::npos);
	EXPECT_EQ(function.find("kv()"), std::string::npos);
}

TEST_F(Oam051bTaskShopAdaptTest, OfficialWheelPayloadReportsPurchasedTaskShopPoints) {
	const auto source = readSource("src/creatures/players/components/wheel/player_wheel.cpp");
	ASSERT_FALSE(source.empty());

	const auto functionStart = source.find("void PlayerWheel::sendOpenWheelWindow(NetworkMessage &msg, uint32_t ownerId)");
	ASSERT_NE(functionStart, std::string::npos);
	const auto functionEnd = source.find("void PlayerWheel::sendOpenWheelWindow(uint32_t ownerId)", functionStart);
	ASSERT_NE(functionEnd, std::string::npos);
	const auto function = source.substr(functionStart, functionEnd - functionStart);

	EXPECT_NE(function.find("The Way of the Monk quest bonus flag"), std::string::npos);
	EXPECT_NE(function.find("m_player.getStorageValue(1000006)"), std::string::npos);
	EXPECT_NE(function.find("std::clamp<int32_t>"), std::string::npos);
}

TEST_F(Oam051bTaskShopAdaptTest, SqlTransactionCommitsBalanceAndStorageBeforeSeparateKvStaging) {
	const auto source = readSource("src/io/iologindata.cpp");
	ASSERT_FALSE(source.empty());

	const auto databaseHelperStart = source.find("void saveOnlinePlayerDatabaseData");
	const auto databaseHelperEnd = source.find("void stageOnlinePlayerWheelKV", databaseHelperStart);
	ASSERT_NE(databaseHelperStart, std::string::npos);
	ASSERT_NE(databaseHelperEnd, std::string::npos);
	const auto databaseHelper = source.substr(databaseHelperStart, databaseHelperEnd - databaseHelperStart);
	EXPECT_NE(databaseHelper.find("IOLoginDataSave::savePlayerStorage(player)"), std::string::npos);

	const auto savePlayerStart = source.find("bool IOLoginData::savePlayer(const std::shared_ptr<Player> &player)");
	const auto savePlayerEnd = source.find("bool IOLoginData::savePlayerGuard", savePlayerStart);
	ASSERT_NE(savePlayerStart, std::string::npos);
	ASSERT_NE(savePlayerEnd, std::string::npos);
	const auto savePlayer = source.substr(savePlayerStart, savePlayerEnd - savePlayerStart);
	const auto transaction = savePlayer.find("DBTransaction::executeWithinTransaction");
	const auto kvStaging = savePlayer.find("stageOnlinePlayerWheelKV(player)");
	ASSERT_NE(transaction, std::string::npos);
	ASSERT_NE(kvStaging, std::string::npos);
	EXPECT_LT(transaction, kvStaging);

	const auto guardStart = savePlayerEnd;
	const auto guardEnd = source.find("void IOLoginData::saveOnlyDataForOnlinePlayer", guardStart);
	ASSERT_NE(guardEnd, std::string::npos);
	const auto guard = source.substr(guardStart, guardEnd - guardStart);
	EXPECT_NE(guard.find("IOLoginDataSave::savePlayerTaskHuntingClass(player)"), std::string::npos);
	EXPECT_NE(guard.find("saveOnlinePlayerDatabaseData(player)"), std::string::npos);
}
