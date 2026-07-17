#include <gtest/gtest.h>

#define private public
#include "creatures/players/vocations/vocation.hpp"
#undef private

TEST(VocationsTest, LookupIsCaseInsensitiveAndUnknownFallsBackToNone) {
	Vocations vocations;

	auto sorcerer = std::make_shared<Vocation>(1);
	sorcerer->name = "Sorcerer";
	vocations.vocationsMap.emplace(1, sorcerer);

	EXPECT_EQ(vocations.getVocationId("Sorcerer"), 1);
	EXPECT_EQ(vocations.getVocationId("sOrCeReR"), 1);
	EXPECT_EQ(vocations.getVocationId("missing"), VOCATION_NONE);
}

TEST(VocationsTest, PromotionLookupReturnsDistinctVocationWithMatchingBase) {
	Vocations vocations;

	auto base = std::make_shared<Vocation>(1);
	base->name = "Sorcerer";
	base->fromVocation = 1;
	vocations.vocationsMap.emplace(1, base);

	auto promoted = std::make_shared<Vocation>(5);
	promoted->name = "Master Sorcerer";
	promoted->fromVocation = 1;
	vocations.vocationsMap.emplace(5, promoted);

	EXPECT_EQ(vocations.getPromotedVocation(1), 5);
	EXPECT_EQ(vocations.getPromotedVocation(5), VOCATION_NONE);
}
