#include <gtest/gtest.h>

#include "database/database.hpp"
#include "game/scheduling/player_checkpoint_attempt.hpp"

namespace it_player_checkpoint_sql_failure {

	class PlayerCheckpointSqlFailureRepositoryDBTest : public ::testing::Test {
	protected:
		void SetUp() override {
			ASSERT_TRUE(Database::getInstance().executeQuery("DROP TABLE IF EXISTS `prs_002e_player_checkpoint_sql_failure_probe`"));
			ASSERT_TRUE(Database::getInstance().executeQuery(
				"CREATE TABLE `prs_002e_player_checkpoint_sql_failure_probe` ("
				"`id` INT NOT NULL PRIMARY KEY, `value` INT NOT NULL) ENGINE=InnoDB"
			));
			ASSERT_TRUE(Database::getInstance().executeQuery(
				"INSERT INTO `prs_002e_player_checkpoint_sql_failure_probe` (`id`, `value`) VALUES (1, 100)"
			));
		}

		void TearDown() override {
			EXPECT_TRUE(Database::getInstance().executeQuery("DROP TABLE IF EXISTS `prs_002e_player_checkpoint_sql_failure_probe`"));
		}

		static int32_t persistedValue() {
			const auto result = Database::getInstance().storeQuery(
				"SELECT `value` FROM `prs_002e_player_checkpoint_sql_failure_probe` WHERE `id` = 1"
			);
			EXPECT_NE(result, nullptr);
			return result ? result->getNumber<int32_t>("value") : 0;
		}

		static bool executeControlledSqlFailure() {
			return DBTransaction::executeWithinTransaction([] {
				if (!Database::getInstance().executeQuery(
						"UPDATE `prs_002e_player_checkpoint_sql_failure_probe` SET `value` = 200 WHERE `id` = 1"
					)) {
					return false;
				}

				// Deliberately fail a real MariaDB statement after an earlier InnoDB write.
				// DBTransaction must roll the update back when this returns false.
				return Database::getInstance().executeQuery(
					"UPDATE `prs_002e_player_checkpoint_sql_failure_probe` SET `missing_column` = 1 WHERE `id` = 1"
				);
			});
		}
	};

	TEST_F(PlayerCheckpointSqlFailureRepositoryDBTest, SqlFailureRollsBackAndPreservesDirtyCheckpoint) {
		PlayerPersistenceState state;
		EXPECT_EQ(state.markDirty(), 1U);
		const auto generation = state.beginCheckpoint();
		ASSERT_EQ(generation, 1U);

		uint32_t attempts = 0;
		const auto result = executePlayerCheckpointAttempt(state, *generation, [&attempts] {
			++attempts;
			return executeControlledSqlFailure();
		});

		EXPECT_EQ(attempts, 1U);
		EXPECT_EQ(result.outcome, PlayerCheckpointAttemptOutcome::saveFailed);
		EXPECT_TRUE(result.acknowledgementAccepted);
		EXPECT_FALSE(result.followUpRequired);
		EXPECT_FALSE(result.exception);
		EXPECT_EQ(persistedValue(), 100);
		EXPECT_TRUE(state.isDirty());
		EXPECT_FALSE(state.hasCheckpointInFlight());
		EXPECT_EQ(state.acknowledgedGeneration(), 0U);
		EXPECT_EQ(state.consecutiveFailures(), 1U);
	}

	TEST_F(PlayerCheckpointSqlFailureRepositoryDBTest, LaterExplicitGenerationCommitsAndClearsDirtyState) {
		PlayerPersistenceState state;
		EXPECT_EQ(state.markDirty(), 1U);
		const auto failedGeneration = state.beginCheckpoint();
		ASSERT_EQ(failedGeneration, 1U);
		ASSERT_EQ(
			executePlayerCheckpointAttempt(state, *failedGeneration, [] { return executeControlledSqlFailure(); }).outcome,
			PlayerCheckpointAttemptOutcome::saveFailed
		);
		ASSERT_EQ(persistedValue(), 100);

		EXPECT_EQ(state.markDirty(), 2U);
		const auto retryGeneration = state.beginCheckpoint();
		ASSERT_EQ(retryGeneration, 2U);
		const auto retry = executePlayerCheckpointAttempt(state, *retryGeneration, [] {
			return DBTransaction::executeWithinTransaction([] {
				return Database::getInstance().executeQuery(
					"UPDATE `prs_002e_player_checkpoint_sql_failure_probe` SET `value` = 300 WHERE `id` = 1"
				);
			});
		});

		EXPECT_EQ(retry.outcome, PlayerCheckpointAttemptOutcome::saved);
		EXPECT_TRUE(retry.acknowledgementAccepted);
		EXPECT_FALSE(retry.followUpRequired);
		EXPECT_EQ(persistedValue(), 300);
		EXPECT_FALSE(state.isDirty());
		EXPECT_FALSE(state.hasCheckpointInFlight());
		EXPECT_EQ(state.acknowledgedGeneration(), 2U);
		EXPECT_EQ(state.consecutiveFailures(), 0U);
	}

} // namespace it_player_checkpoint_sql_failure
