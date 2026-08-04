#include <gtest/gtest.h>

#include "database/database.hpp"
#include "database/player_writer_fence_repository.hpp"
#include "database/player_writer_fenced_save_transaction.hpp"
#include "game/scheduling/player_checkpoint_attempt.hpp"

#include <fmt/format.h>

#include <atomic>
#include <string>

namespace it_player_writer_fenced_save {

	class PlayerWriterFencedSaveTest : public ::testing::Test {
	protected:
		void SetUp() override {
			static std::atomic_uint64_t sequence = 0;
			playerName = fmt::format("PRS004D Subject {}", ++sequence);
			ASSERT_TRUE(g_database().executeQuery(fmt::format(
				"INSERT INTO `players` (`name`, `account_id`, `conditions`) VALUES ({}, 1, '')",
				g_database().escapeString(playerName)
			)));
			playerId = static_cast<uint32_t>(g_database().getLastInsertId());
			ASSERT_NE(0, playerId);
		}

		void TearDown() override {
			if (playerId != 0) {
				EXPECT_TRUE(g_database().executeQuery(fmt::format("DELETE FROM `players` WHERE `id` = {}", playerId)));
			}
		}

		static PlayerWriterFenceToken token(uint8_t seed) {
			PlayerWriterFenceToken value {};
			for (size_t index = 0; index < value.size(); ++index) {
				value[index] = static_cast<uint8_t>(seed + index);
			}
			return value;
		}

		PlayerWriterFenceContext acquireContext() {
			const auto loaded = repository.load(playerId);
			EXPECT_EQ(PlayerWriterFenceResult::Applied, loaded.result);
			EXPECT_FALSE(PlayerWriterFenceRepository::isValidToken(loaded.context.writerToken));
			PlayerWriterFenceContext desired {
				.playerId = playerId,
				.ownershipGeneration = loaded.context.ownershipGeneration + 1,
				.writerToken = token(7),
				.stateRevision = loaded.context.stateRevision,
			};
			EXPECT_EQ(PlayerWriterFenceResult::Applied, repository.acquire(desired));
			return desired;
		}

		uint32_t level() const {
			const auto result = g_database().storeQuery(fmt::format("SELECT `level` FROM `players` WHERE `id` = {}", playerId));
			EXPECT_NE(nullptr, result);
			return result ? result->getNumber<uint32_t>("level") : 0;
		}

		uint64_t revision() const {
			const auto result = g_database().storeQuery(fmt::format(
				"SELECT `state_revision` FROM `player_writer_fence` WHERE `player_id` = {}",
				playerId
			));
			EXPECT_NE(nullptr, result);
			return result ? result->getNumber<uint64_t>("state_revision") : 0;
		}

		PlayerWriterFenceRepository repository;
		uint32_t playerId = 0;
		std::string playerName;
	};

	TEST_F(PlayerWriterFencedSaveTest, ProtectedMutationAndExactNextRevisionCommitTogether) {
		auto context = acquireContext();
		const auto result = PlayerWriterFencedSaveTransaction::execute(context, [&] {
			return g_database().executeQuery(fmt::format(
				"UPDATE `players` SET `level` = 77 WHERE `id` = {}",
				playerId
			));
		});

		EXPECT_EQ(PlayerWriterFenceResult::Applied, result);
		EXPECT_EQ(1, context.stateRevision);
		EXPECT_EQ(77, level());
		EXPECT_EQ(1, revision());
	}

	TEST_F(PlayerWriterFencedSaveTest, MissingContextFailsBeforeMutation) {
		PlayerWriterFenceContext missing;
		uint32_t attempts = 0;
		const auto result = PlayerWriterFencedSaveTransaction::execute(missing, [&] {
			++attempts;
			return g_database().executeQuery(fmt::format(
				"UPDATE `players` SET `level` = 88 WHERE `id` = {}",
				playerId
			));
		});

		EXPECT_EQ(PlayerWriterFenceResult::MalformedContext, result);
		EXPECT_EQ(0, attempts);
		EXPECT_EQ(1, level());
		EXPECT_EQ(0, revision());
	}

	TEST_F(PlayerWriterFencedSaveTest, CallbackFailureRollsBackMutationAndRevision) {
		auto context = acquireContext();
		const auto result = PlayerWriterFencedSaveTransaction::execute(context, [&] {
			EXPECT_TRUE(g_database().executeQuery(fmt::format(
				"UPDATE `players` SET `level` = 66 WHERE `id` = {}",
				playerId
			)));
			return false;
		});

		EXPECT_EQ(PlayerWriterFenceResult::DatabaseFailure, result);
		EXPECT_EQ(0, context.stateRevision);
		EXPECT_EQ(1, level());
		EXPECT_EQ(0, revision());
	}

	TEST_F(PlayerWriterFencedSaveTest, StaleRevisionRollsBackAndPreservesDirtyStateWithoutRetry) {
		auto staleContext = acquireContext();
		ASSERT_EQ(PlayerWriterFenceResult::Applied, repository.advanceRevision(staleContext, 1));
		ASSERT_EQ(1, revision());

		PlayerPersistenceState state;
		EXPECT_EQ(1, state.markDirty());
		const auto generation = state.beginCheckpoint();
		ASSERT_EQ(1, generation);

		uint32_t attempts = 0;
		const auto attempt = executePlayerCheckpointAttempt(state, *generation, [&] {
			++attempts;
			return PlayerWriterFencedSaveTransaction::execute(staleContext, [&] {
				return g_database().executeQuery(fmt::format(
					"UPDATE `players` SET `level` = 99 WHERE `id` = {}",
					playerId
				));
			}) == PlayerWriterFenceResult::Applied;
		});

		EXPECT_EQ(1, attempts);
		EXPECT_EQ(PlayerCheckpointAttemptOutcome::saveFailed, attempt.outcome);
		EXPECT_TRUE(attempt.acknowledgementAccepted);
		EXPECT_FALSE(attempt.followUpRequired);
		EXPECT_TRUE(state.isDirty());
		EXPECT_EQ(0, state.acknowledgedGeneration());
		EXPECT_EQ(1, state.consecutiveFailures());
		EXPECT_EQ(1, level());
		EXPECT_EQ(1, revision());
	}

} // namespace it_player_writer_fenced_save
