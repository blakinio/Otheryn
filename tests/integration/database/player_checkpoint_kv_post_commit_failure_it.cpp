#include <gtest/gtest.h>

#include "database/database.hpp"
#include "game/scheduling/player_checkpoint_attempt.hpp"
#include "kv/kv_sql.hpp"
#include "lib/di/container.hpp"

namespace it_player_checkpoint_kv_post_commit_failure {

	class PlayerCheckpointKvPostCommitFailureRepositoryDBTest : public ::testing::Test {
	protected:
		static constexpr auto ProbeKey = "prs.002f.pending-wheel-kv";

		void SetUp() override {
			ASSERT_TRUE(ensureKvStoreAvailable());
			ASSERT_TRUE(Database::getInstance().executeQuery("DROP TABLE IF EXISTS `prs_002f_player_sql_commit_probe`"));
			ASSERT_TRUE(Database::getInstance().executeQuery(
				"CREATE TABLE `prs_002f_player_sql_commit_probe` ("
				"`id` INT NOT NULL PRIMARY KEY, `value` INT NOT NULL) ENGINE=InnoDB"
			));
			ASSERT_TRUE(Database::getInstance().executeQuery(
				"INSERT INTO `prs_002f_player_sql_commit_probe` (`id`, `value`) VALUES (1, 100)"
			));
			ASSERT_TRUE(Database::getInstance().executeQuery(
				"DELETE FROM `kv_store` WHERE `key_name` = 'prs.002f.pending-wheel-kv'"
			));
		}

		void TearDown() override {
			EXPECT_TRUE(ensureKvStoreAvailable());
			EXPECT_TRUE(Database::getInstance().executeQuery(
				"DELETE FROM `kv_store` WHERE `key_name` = 'prs.002f.pending-wheel-kv'"
			));
			EXPECT_TRUE(Database::getInstance().executeQuery("DROP TABLE IF EXISTS `prs_002f_player_sql_commit_probe`"));
		}

		static bool primaryKvTableExists() {
			return Database::getInstance().storeQuery(
					   "SELECT 1 AS `present` FROM `information_schema`.`tables` "
					   "WHERE `table_schema` = DATABASE() AND `table_name` = 'kv_store' LIMIT 1"
				   )
				!= nullptr;
		}

		static bool hiddenKvTableExists() {
			return Database::getInstance().storeQuery(
					   "SELECT 1 AS `present` FROM `information_schema`.`tables` "
					   "WHERE `table_schema` = DATABASE() AND `table_name` = 'prs_002f_kv_store_unavailable' LIMIT 1"
				   )
				!= nullptr;
		}

		static bool ensureKvStoreAvailable() {
			const bool primaryExists = primaryKvTableExists();
			const bool hiddenExists = hiddenKvTableExists();
			if (primaryExists && hiddenExists) {
				return Database::getInstance().executeQuery("DROP TABLE `prs_002f_kv_store_unavailable`");
			}
			if (primaryExists) {
				return true;
			}
			if (!hiddenExists) {
				return false;
			}
			return Database::getInstance().executeQuery(
				"RENAME TABLE `prs_002f_kv_store_unavailable` TO `kv_store`"
			);
		}

		static bool hideKvStore() {
			return Database::getInstance().executeQuery(
				"RENAME TABLE `kv_store` TO `prs_002f_kv_store_unavailable`"
			);
		}

		static int32_t committedSqlValue() {
			const auto result = Database::getInstance().storeQuery(
				"SELECT `value` FROM `prs_002f_player_sql_commit_probe` WHERE `id` = 1"
			);
			EXPECT_NE(result, nullptr);
			return result ? result->getNumber<int32_t>("value") : 0;
		}

		static bool committedKvKeyExists() {
			return Database::getInstance().storeQuery(
					   "SELECT 1 AS `present` FROM `kv_store` "
					   "WHERE `key_name` = 'prs.002f.pending-wheel-kv' LIMIT 1"
				   )
				!= nullptr;
		}
	};

	TEST_F(PlayerCheckpointKvPostCommitFailureRepositoryDBTest, KvFailureAfterSqlCommitStaysDirtyUntilExplicitRetry) {
		Database &db = Database::getInstance();
		KVSQL kv(db, inject<Logger>());
		PlayerPersistenceState state;
		EXPECT_EQ(state.markDirty(), 1U);
		const auto generation = state.beginCheckpoint();
		ASSERT_EQ(generation, 1U);
		ASSERT_TRUE(hideKvStore());

		const auto failed = executePlayerCheckpointAttempt(state, *generation, [&] {
			const bool sqlCommitted = DBTransaction::executeWithinTransaction([&db] {
				return db.executeQuery(
					"UPDATE `prs_002f_player_sql_commit_probe` SET `value` = 200 WHERE `id` = 1"
				);
			});
			if (!sqlCommitted) {
				return false;
			}

			kv.set(ProbeKey, 77);
			return kv.saveAll();
		});

		ASSERT_TRUE(ensureKvStoreAvailable());
		EXPECT_EQ(failed.outcome, PlayerCheckpointAttemptOutcome::saveFailed);
		EXPECT_TRUE(failed.acknowledgementAccepted);
		EXPECT_FALSE(failed.followUpRequired);
		EXPECT_FALSE(failed.exception);
		EXPECT_EQ(committedSqlValue(), 200);
		EXPECT_FALSE(committedKvKeyExists());
		EXPECT_TRUE(state.isDirty());
		EXPECT_FALSE(state.hasCheckpointInFlight());
		EXPECT_EQ(state.acknowledgedGeneration(), 0U);
		EXPECT_EQ(state.consecutiveFailures(), 1U);

		EXPECT_EQ(state.markDirty(), 2U);
		const auto retryGeneration = state.beginCheckpoint();
		ASSERT_EQ(retryGeneration, 2U);
		const auto retry = executePlayerCheckpointAttempt(state, *retryGeneration, [&kv] {
			return kv.saveAll();
		});

		EXPECT_EQ(retry.outcome, PlayerCheckpointAttemptOutcome::saved);
		EXPECT_TRUE(retry.acknowledgementAccepted);
		EXPECT_FALSE(retry.followUpRequired);
		EXPECT_EQ(committedSqlValue(), 200);
		EXPECT_TRUE(committedKvKeyExists());
		EXPECT_FALSE(state.isDirty());
		EXPECT_FALSE(state.hasCheckpointInFlight());
		EXPECT_EQ(state.acknowledgedGeneration(), 2U);
		EXPECT_EQ(state.consecutiveFailures(), 0U);

		KVSQL persistedKv(db, inject<Logger>());
		const auto persistedValue = persistedKv.get(ProbeKey, true);
		ASSERT_TRUE(persistedValue.has_value());
		EXPECT_EQ(persistedValue->getNumber(), 77.0);
	}

} // namespace it_player_checkpoint_kv_post_commit_failure
