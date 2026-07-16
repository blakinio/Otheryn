#include "database/database.hpp"

namespace it_world_persistence {

	class WorldPersistenceTransactionTest : public ::testing::Test {
	protected:
		static constexpr std::string_view probeTable = "oam_004c_house_rollback_probe";

		void SetUp() override {
			ASSERT_TRUE(Database::getInstance().executeQuery(fmt::format("DROP TABLE IF EXISTS `{}`", probeTable)));
			ASSERT_TRUE(Database::getInstance().executeQuery(fmt::format(
				"CREATE TABLE `{}` (`id` INT NOT NULL PRIMARY KEY, `value` INT NOT NULL) ENGINE=InnoDB",
				probeTable
			)));
			ASSERT_TRUE(Database::getInstance().executeQuery(fmt::format("INSERT INTO `{}` (`id`, `value`) VALUES (1, 100)", probeTable)));
		}

		void TearDown() override {
			EXPECT_TRUE(Database::getInstance().executeQuery(fmt::format("DROP TABLE IF EXISTS `{}`", probeTable)));
		}
	};

	TEST_F(WorldPersistenceTransactionTest, HouseReplacementFalseCallbackRollsBackTransaction) {
		const bool transactionResult = DBTransaction::executeWithinTransaction([] {
			if (!Database::getInstance().executeQuery(fmt::format("UPDATE `{}` SET `value` = 200 WHERE `id` = 1", probeTable))) {
				return false;
			}

			// IOMapSerialize::saveHouseItems() reports a failed replacement batch by
			// returning false from the same transaction callback contract. OAM-004A
			// requires that result to roll back, not commit, earlier statements.
			return false;
		});

		EXPECT_FALSE(transactionResult);
		const auto result = Database::getInstance().storeQuery(fmt::format("SELECT `value` FROM `{}` WHERE `id` = 1", probeTable));
		ASSERT_NE(result, nullptr);
		EXPECT_EQ(result->getNumber<int32_t>("value"), 100);
	}

} // namespace it_world_persistence
