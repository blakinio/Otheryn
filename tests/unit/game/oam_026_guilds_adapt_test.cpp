#include <gtest/gtest.h>

#include <type_traits>

#include "creatures/players/grouping/guild.hpp"
#include "io/ioguild.hpp"

TEST(Oam026GuildsAdaptTest, PreservesGuildIdentityRanksAndPersistentProjectionState) {
	auto guild = std::make_shared<Guild>(42, "Oteryn Guild");

	EXPECT_EQ(guild->getId(), 42u);
	EXPECT_EQ(guild->getName(), "Oteryn Guild");
	EXPECT_TRUE(guild->getMembersOnline().empty());
	EXPECT_EQ(guild->getMemberCountOnline(), 0u);
	EXPECT_EQ(guild->getMemberCount(), 0u);
	EXPECT_EQ(guild->getBankBalance(), 0u);
	EXPECT_TRUE(guild->isOnline());

	guild->addRank(7, "Leader", 3);
	guild->addRank(8, "Member", 1);
	guild->setMemberCount(12);
	guild->setBankBalance(123456);

	ASSERT_NE(guild->getRankById(7), nullptr);
	EXPECT_EQ(guild->getRankById(7)->name, "Leader");
	ASSERT_NE(guild->getRankByName("Member"), nullptr);
	EXPECT_EQ(guild->getRankByName("Member")->id, 8u);
	ASSERT_NE(guild->getRankByLevel(3), nullptr);
	EXPECT_EQ(guild->getRankByLevel(3)->id, 7u);
	EXPECT_EQ(guild->getMemberCount(), 12u);
	EXPECT_EQ(guild->getBankBalance(), 123456u);
}

TEST(Oam026GuildsAdaptTest, PreservesOam004GuildSaveFailurePropagationApi) {
	using ExpectedSaveGuildSignature = bool (*)(const std::shared_ptr<Guild> &);

	EXPECT_TRUE((std::is_same_v<decltype(&IOGuild::saveGuild), ExpectedSaveGuildSignature>));
}
