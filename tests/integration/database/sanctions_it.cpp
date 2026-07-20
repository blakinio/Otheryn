#include "creatures/players/management/ban.hpp"
#include "database/database.hpp"

#include <fmt/format.h>

#include <ctime>
#include <string>
#include <string_view>

namespace it_sanctions {

	class SanctionsRepositoryDBTest : public ::testing::Test {
	protected:
		static constexpr uint32_t accountId = 240024;
		static constexpr uint32_t moderatorId = 240024;
		static constexpr std::string_view deleteTrigger = "oam_024_block_account_ban_delete";

		void SetUp() override {
			cleanup();
			ASSERT_TRUE(g_database().executeQuery("INSERT INTO `accounts` (`id`, `name`, `password`, `email`) VALUES (240024, 'oam024-account', 'test', 'oam024@example.invalid')"));
			ASSERT_TRUE(g_database().executeQuery("INSERT INTO `players` (`id`, `name`, `account_id`, `conditions`) VALUES (240024, 'Oam024Moderator', 240024, '')"));
		}

		void TearDown() override {
			cleanup();
		}

		void insertAccountBan(int64_t expiresAt, std::string_view reason = "OAM-024 test ban") const {
			const auto bannedAt = expiresAt == 0 ? static_cast<int64_t>(std::time(nullptr)) : expiresAt - 60;
			ASSERT_TRUE(g_database().executeQuery(fmt::format(
				"INSERT INTO `account_bans` (`account_id`, `reason`, `banned_at`, `expires_at`, `banned_by`) VALUES ({}, {}, {}, {}, {})",
				accountId,
				g_database().escapeString(std::string(reason)),
				bannedAt,
				expiresAt,
				moderatorId
			)));
		}

		uint64_t countRows(std::string_view table) const {
			const auto result = g_database().storeQuery(fmt::format("SELECT COUNT(*) AS `count` FROM `{}` WHERE `account_id` = {}", table, accountId));
			EXPECT_NE(result, nullptr);
			return result ? result->getNumber<uint64_t>("count") : 0;
		}

		void cleanup() const {
			EXPECT_TRUE(g_database().executeQuery(fmt::format("DROP TRIGGER IF EXISTS `{}`", deleteTrigger)));
			EXPECT_TRUE(g_database().executeQuery(fmt::format("DELETE FROM `account_ban_history` WHERE `account_id` = {}", accountId)));
			EXPECT_TRUE(g_database().executeQuery(fmt::format("DELETE FROM `account_bans` WHERE `account_id` = {}", accountId)));
			EXPECT_TRUE(g_database().executeQuery(fmt::format("DELETE FROM `players` WHERE `id` = {}", moderatorId)));
			EXPECT_TRUE(g_database().executeQuery(fmt::format("DELETE FROM `accounts` WHERE `id` = {}", accountId)));
		}
	};

	TEST_F(SanctionsRepositoryDBTest, ActiveAccountBanRemainsEnforced) {
		const auto expiresAt = static_cast<int64_t>(std::time(nullptr)) + 3600;
		insertAccountBan(expiresAt, "active sanction");

		BanInfo banInfo;
		EXPECT_TRUE(IOBan::isAccountBanned(accountId, banInfo));
		EXPECT_EQ(expiresAt, banInfo.expiresAt);
		EXPECT_EQ("active sanction", banInfo.reason);
		EXPECT_EQ("Oam024Moderator", banInfo.bannedBy);
		EXPECT_EQ(1, countRows("account_bans"));
		EXPECT_EQ(0, countRows("account_ban_history"));
	}

	TEST_F(SanctionsRepositoryDBTest, ExpiredAccountBanMovesToHistoryExactlyOnce) {
		const auto expiresAt = static_cast<int64_t>(std::time(nullptr)) - 60;
		insertAccountBan(expiresAt, "expired sanction");

		BanInfo banInfo;
		EXPECT_FALSE(IOBan::isAccountBanned(accountId, banInfo));
		EXPECT_EQ(0, countRows("account_bans"));
		EXPECT_EQ(1, countRows("account_ban_history"));

		BanInfo repeatedLookup;
		EXPECT_FALSE(IOBan::isAccountBanned(accountId, repeatedLookup));
		EXPECT_EQ(0, countRows("account_bans"));
		EXPECT_EQ(1, countRows("account_ban_history"));
	}

	TEST_F(SanctionsRepositoryDBTest, FailedExpiredBanDeleteRollsBackHistoryInsert) {
		const auto expiresAt = static_cast<int64_t>(std::time(nullptr)) - 60;
		insertAccountBan(expiresAt, "rollback sanction");
		ASSERT_TRUE(g_database().executeQuery(fmt::format(
			"CREATE TRIGGER `{}` BEFORE DELETE ON `account_bans` FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'OAM-024 forced delete failure'",
			deleteTrigger
		)));

		BanInfo banInfo;
		EXPECT_FALSE(IOBan::isAccountBanned(accountId, banInfo));
		EXPECT_EQ(1, countRows("account_bans"));
		EXPECT_EQ(0, countRows("account_ban_history"));

		ASSERT_TRUE(g_database().executeQuery(fmt::format("DROP TRIGGER IF EXISTS `{}`", deleteTrigger)));
		BanInfo retryLookup;
		EXPECT_FALSE(IOBan::isAccountBanned(accountId, retryLookup));
		EXPECT_EQ(0, countRows("account_bans"));
		EXPECT_EQ(1, countRows("account_ban_history"));
	}

} // namespace it_sanctions
