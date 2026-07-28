#include <gtest/gtest.h>

#include "database/database.hpp"
#include "game/scheduling/player_checkpoint_attempt.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdlib>
#endif

namespace it_player_checkpoint_commit_before_ack_crash {

	class PlayerCheckpointCommitBeforeAckRepositoryDBTestDeathTest : public ::testing::Test {
	protected:
		static constexpr int CrashExitCode = 86;
		static constexpr int DirtyGenerationFailureExitCode = 87;
		static constexpr int CheckpointStartFailureExitCode = 88;
		static constexpr int SqlCommitFailureExitCode = 89;
		static constexpr int UnexpectedAcknowledgementExitCode = 90;

		void SetUp() override {
			ASSERT_TRUE(Database::getInstance().executeQuery("DROP TABLE IF EXISTS `prs_002g_commit_before_ack_probe`"));
			ASSERT_TRUE(Database::getInstance().executeQuery(
				"CREATE TABLE `prs_002g_commit_before_ack_probe` ("
				"`id` INT NOT NULL PRIMARY KEY, `value` INT NOT NULL) ENGINE=InnoDB"
			));
			ASSERT_TRUE(Database::getInstance().executeQuery(
				"INSERT INTO `prs_002g_commit_before_ack_probe` (`id`, `value`) VALUES (1, 100)"
			));
		}

		void TearDown() override {
			EXPECT_TRUE(Database::getInstance().executeQuery("DROP TABLE IF EXISTS `prs_002g_commit_before_ack_probe`"));
		}

		static int32_t committedSqlValue() {
			const auto result = Database::getInstance().storeQuery(
				"SELECT `value` FROM `prs_002g_commit_before_ack_probe` WHERE `id` = 1"
			);
			EXPECT_NE(result, nullptr);
			return result ? result->getNumber<int32_t>("value") : 0;
		}
	};

	TEST_F(PlayerCheckpointCommitBeforeAckRepositoryDBTestDeathTest, CommittedSqlSurvivesCrashBeforeInMemoryAcknowledgement) {
		::testing::FLAGS_gtest_death_test_style = "threadsafe";

		ASSERT_EXIT(
			{
				PlayerPersistenceState childState;
				if (childState.markDirty() != 1U) {
					std::_Exit(DirtyGenerationFailureExitCode);
				}

				const auto generation = childState.beginCheckpoint();
				if (!generation.has_value() || *generation != 1U) {
					std::_Exit(CheckpointStartFailureExitCode);
				}

				Database &db = Database::getInstance();
				const auto attempt = executePlayerCheckpointAttempt(childState, *generation, [&db] {
					const bool committed = DBTransaction::executeWithinTransaction([&db] {
						return db.executeQuery(
							"UPDATE `prs_002g_commit_before_ack_probe` SET `value` = 200 WHERE `id` = 1"
						);
					});
					if (!committed) {
						std::_Exit(SqlCommitFailureExitCode);
					}

					std::_Exit(CrashExitCode);
					return true;
				});
				(void)attempt;
				std::_Exit(UnexpectedAcknowledgementExitCode);
			},
			::testing::ExitedWithCode(CrashExitCode),
			""
		);

		EXPECT_EQ(committedSqlValue(), 200);

		PlayerPersistenceState restartedState;
		EXPECT_FALSE(restartedState.isDirty());
		EXPECT_FALSE(restartedState.hasCheckpointInFlight());
		EXPECT_EQ(restartedState.dirtyGeneration(), 0U);
		EXPECT_EQ(restartedState.acknowledgedGeneration(), 0U);
		EXPECT_EQ(restartedState.consecutiveFailures(), 0U);
	}

} // namespace it_player_checkpoint_commit_before_ack_crash
