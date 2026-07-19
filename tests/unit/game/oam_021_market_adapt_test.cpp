#include <gtest/gtest.h>

#include "io/market_validation.hpp"

TEST(Oam021MarketAdaptTest, OfferCounterMatchesWireIdentityContract) {
	EXPECT_EQ(MarketValidation::offerCounter(0), static_cast<uint16_t>(0xCDEF));
	EXPECT_EQ(MarketValidation::offerCounter(0x00ABCDEFU), 0);
	EXPECT_EQ(MarketValidation::offerCounter(0x00010000U), MarketValidation::offerCounter(0));
}

TEST(Oam021MarketAdaptTest, OfferCreatedAtFailsClosedOnInvalidTimestampWindow) {
	EXPECT_EQ(MarketValidation::offerCreatedAt(3600, 3600), std::optional<uint32_t>(0));
	EXPECT_EQ(MarketValidation::offerCreatedAt(7200, 3600), std::optional<uint32_t>(3600));
	EXPECT_EQ(MarketValidation::offerCreatedAt(3599, 3600), std::nullopt);
	EXPECT_EQ(MarketValidation::offerCreatedAt(7200, -1), std::nullopt);
}

TEST(Oam021MarketAdaptTest, TierParsingRejectsMalformedAndOutOfRangeDatabaseValues) {
	EXPECT_EQ(MarketValidation::parseTier("0", 10), std::optional<uint8_t>(0));
	EXPECT_EQ(MarketValidation::parseTier("10", 10), std::optional<uint8_t>(10));
	EXPECT_EQ(MarketValidation::parseTier("11", 10), std::nullopt);
	EXPECT_EQ(MarketValidation::parseTier("256", 300), std::nullopt);
	EXPECT_EQ(MarketValidation::parseTier("300", 10), std::nullopt);
	EXPECT_EQ(MarketValidation::parseTier("10x", 10), std::nullopt);
	EXPECT_EQ(MarketValidation::parseTier("-1", 10), std::nullopt);
	EXPECT_EQ(MarketValidation::parseTier("", 10), std::nullopt);
	EXPECT_EQ(MarketValidation::parseTier("1", -1), std::nullopt);
}
