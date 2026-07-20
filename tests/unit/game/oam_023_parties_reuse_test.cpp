#include <gtest/gtest.h>

#include "creatures/players/grouping/party.hpp"

TEST(Oam023PartiesReuseTest, PreservesSharedExperienceStatusValues) {
	EXPECT_EQ(static_cast<uint8_t>(SHAREDEXP_OK), 0);
	EXPECT_EQ(static_cast<uint8_t>(SHAREDEXP_TOOFARAWAY), 1);
	EXPECT_EQ(static_cast<uint8_t>(SHAREDEXP_LEVELDIFFTOOLARGE), 2);
	EXPECT_EQ(static_cast<uint8_t>(SHAREDEXP_MEMBERINACTIVE), 3);
	EXPECT_EQ(static_cast<uint8_t>(SHAREDEXP_EMPTYPARTY), 4);
}

TEST(Oam023PartiesReuseTest, StartsEmptyAndSelfOwned) {
	auto party = std::make_shared<Party>();

	EXPECT_EQ(party->getParty().get(), party.get());
	EXPECT_EQ(party->getLeader(), nullptr);
	EXPECT_TRUE(party->getPlayers().empty());
	EXPECT_TRUE(party->getMembers().empty());
	EXPECT_TRUE(party->getInvitees().empty());
	EXPECT_EQ(party->getMemberCount(), 0u);
	EXPECT_EQ(party->getInvitationCount(), 0u);
	EXPECT_TRUE(party->empty());
	EXPECT_FALSE(party->isSharedExperienceActive());
	EXPECT_FALSE(party->isSharedExperienceEnabled());
}

TEST(Oam023PartiesReuseTest, FailsClosedWithoutLeader) {
	auto party = std::make_shared<Party>();

	EXPECT_FALSE(party->invitePlayer(nullptr));
	EXPECT_FALSE(party->removeInvite(nullptr));
	EXPECT_FALSE(party->leaveParty(nullptr));
	EXPECT_FALSE(party->passPartyLeadership(nullptr));
	EXPECT_FALSE(party->setSharedExperience(nullptr, true, true));
	EXPECT_EQ(party->getMemberSharedExperienceStatus(nullptr), SHAREDEXP_EMPTYPARTY);
	EXPECT_FALSE(party->canUseSharedExperience(nullptr));
	EXPECT_FALSE(party->canOpenCorpse(1));
}
