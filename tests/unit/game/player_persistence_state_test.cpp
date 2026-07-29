#include <gtest/gtest.h>

#include "game/scheduling/player_persistence_state.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <atomic>
	#include <thread>
	#include <vector>
#endif

TEST(PlayerPersistenceStateTest, StartsCleanAndCannotBeginCheckpoint) {
	PlayerPersistenceState state;

	EXPECT_FALSE(state.isDirty());
	EXPECT_FALSE(state.hasCheckpointInFlight());
	EXPECT_EQ(state.dirtyGeneration(), 0U);
	EXPECT_EQ(state.acknowledgedGeneration(), 0U);
	EXPECT_EQ(state.consecutiveFailures(), 0U);
	EXPECT_FALSE(state.dirtySinceTimestampSeconds().has_value());
	EXPECT_FALSE(state.beginCheckpoint().has_value());
}

TEST(PlayerPersistenceStateTest, CapturesOneDirtyGenerationAndCoalescesRequests) {
	PlayerPersistenceState state;

	EXPECT_EQ(state.markDirty(), 1U);
	const auto checkpoint = state.beginCheckpoint();
	ASSERT_TRUE(checkpoint.has_value());
	EXPECT_EQ(*checkpoint, 1U);
	EXPECT_TRUE(state.hasCheckpointInFlight());
	EXPECT_FALSE(state.beginCheckpoint().has_value());
}

TEST(PlayerPersistenceStateTest, MutationDuringSaveRemainsDirtyAfterOlderGenerationSucceeds) {
	PlayerPersistenceState state;

	(void)state.markDirty();
	const auto first = state.beginCheckpoint();
	ASSERT_EQ(first, 1U);

	EXPECT_EQ(state.markDirty(), 2U);
	EXPECT_TRUE(state.acknowledgeSuccess(*first));
	EXPECT_EQ(state.acknowledgedGeneration(), 1U);
	EXPECT_EQ(state.dirtyGeneration(), 2U);
	EXPECT_TRUE(state.isDirty());
	EXPECT_FALSE(state.hasCheckpointInFlight());

	const auto second = state.beginCheckpoint();
	ASSERT_EQ(second, 2U);
	EXPECT_TRUE(state.acknowledgeSuccess(*second));
	EXPECT_FALSE(state.isDirty());
	EXPECT_EQ(state.acknowledgedGeneration(), 2U);
}

TEST(PlayerPersistenceStateTest, FailedSavePreservesDirtyGenerationAndConsumesRetryBudget) {
	PlayerPersistenceState state;

	(void)state.markDirty();
	const auto first = state.beginCheckpoint(2);
	ASSERT_EQ(first, 1U);
	EXPECT_TRUE(state.acknowledgeFailure(*first));
	EXPECT_TRUE(state.isDirty());
	EXPECT_EQ(state.consecutiveFailures(), 1U);

	const auto second = state.beginCheckpoint(2);
	ASSERT_EQ(second, 1U);
	EXPECT_TRUE(state.acknowledgeFailure(*second));
	EXPECT_TRUE(state.isDirty());
	EXPECT_EQ(state.consecutiveFailures(), 2U);
	EXPECT_FALSE(state.canBeginCheckpoint(2));
	EXPECT_FALSE(state.beginCheckpoint(2).has_value());
}

TEST(PlayerPersistenceStateTest, AbandonedCheckpointPreservesDirtyStateWithoutConsumingFailureBudget) {
	PlayerPersistenceState state;

	(void)state.markDirty();
	const auto generation = state.beginCheckpoint();
	ASSERT_EQ(generation, 1U);

	EXPECT_TRUE(state.abandonCheckpoint(*generation));
	EXPECT_TRUE(state.isDirty());
	EXPECT_FALSE(state.hasCheckpointInFlight());
	EXPECT_EQ(state.acknowledgedGeneration(), 0U);
	EXPECT_EQ(state.consecutiveFailures(), 0U);

	const auto retry = state.beginCheckpoint();
	ASSERT_EQ(retry, 1U);
	EXPECT_TRUE(state.acknowledgeSuccess(*retry));
	EXPECT_FALSE(state.isDirty());
}

TEST(PlayerPersistenceStateTest, RejectsStaleAbandonmentAndPreservesExactCheckpointOwner) {
	PlayerPersistenceState state;

	(void)state.markDirty();
	const auto first = state.beginCheckpoint();
	ASSERT_EQ(first, 1U);
	EXPECT_EQ(state.markDirty(), 2U);

	EXPECT_FALSE(state.abandonCheckpoint(2));
	EXPECT_EQ(state.inFlightGeneration(), first);
	EXPECT_TRUE(state.abandonCheckpoint(*first));
	EXPECT_TRUE(state.isDirty());
	EXPECT_EQ(state.consecutiveFailures(), 0U);

	const auto second = state.beginCheckpoint();
	ASSERT_EQ(second, 2U);
}

TEST(PlayerPersistenceStateTest, SuccessfulExplicitAttemptResetsFailureBudget) {
	PlayerPersistenceState state;

	(void)state.markDirty();
	const auto failed = state.beginCheckpoint(1);
	ASSERT_EQ(failed, 1U);
	ASSERT_TRUE(state.acknowledgeFailure(*failed));
	EXPECT_FALSE(state.beginCheckpoint(1).has_value());

	const auto explicitAttempt = state.beginCheckpoint(2);
	ASSERT_EQ(explicitAttempt, 1U);
	EXPECT_TRUE(state.acknowledgeSuccess(*explicitAttempt));
	EXPECT_EQ(state.consecutiveFailures(), 0U);
	EXPECT_FALSE(state.isDirty());
}

TEST(PlayerPersistenceStateTest, RejectsStaleAndDuplicateAcknowledgements) {
	PlayerPersistenceState state;

	(void)state.markDirty();
	const auto first = state.beginCheckpoint();
	ASSERT_EQ(first, 1U);
	(void)state.markDirty();

	EXPECT_FALSE(state.acknowledgeSuccess(2));
	EXPECT_FALSE(state.acknowledgeFailure(2));
	EXPECT_EQ(state.inFlightGeneration(), first);

	EXPECT_TRUE(state.acknowledgeSuccess(*first));
	EXPECT_FALSE(state.acknowledgeSuccess(*first));
	EXPECT_FALSE(state.acknowledgeFailure(*first));
	EXPECT_TRUE(state.isDirty());
}

TEST(PlayerPersistenceStateTest, NewMutationDoesNotSilentlyResetFailureBudget) {
	PlayerPersistenceState state;

	(void)state.markDirty();
	const auto first = state.beginCheckpoint(1);
	ASSERT_EQ(first, 1U);
	ASSERT_TRUE(state.acknowledgeFailure(*first));

	EXPECT_EQ(state.markDirty(), 2U);
	EXPECT_EQ(state.consecutiveFailures(), 1U);
	EXPECT_FALSE(state.canBeginCheckpoint(1));
	EXPECT_TRUE(state.canBeginCheckpoint(2));
}

TEST(PlayerPersistenceStateTest, DirtyTimestampStartsOnceAndClearsOnlyWhenOwnerBecomesClean) {
	PlayerPersistenceState state;

	EXPECT_EQ(state.markDirty(100), 1U);
	EXPECT_EQ(state.dirtySinceTimestampSeconds(), 100);
	const auto first = state.beginCheckpoint();
	ASSERT_EQ(first, 1U);

	EXPECT_EQ(state.markDirty(200), 2U);
	EXPECT_EQ(state.dirtySinceTimestampSeconds(), 100);
	ASSERT_TRUE(state.acknowledgeSuccess(*first));
	EXPECT_TRUE(state.isDirty());
	EXPECT_EQ(state.dirtySinceTimestampSeconds(), 100);

	const auto second = state.beginCheckpoint();
	ASSERT_EQ(second, 2U);
	ASSERT_TRUE(state.acknowledgeSuccess(*second));
	EXPECT_FALSE(state.isDirty());
	EXPECT_FALSE(state.dirtySinceTimestampSeconds().has_value());
}

TEST(PlayerPersistenceStateTest, FailureAndAbandonmentPreserveOriginalDirtyTimestamp) {
	PlayerPersistenceState state;
	(void)state.markDirty(300);

	const auto rejected = state.beginCheckpoint();
	ASSERT_EQ(rejected, 1U);
	ASSERT_TRUE(state.abandonCheckpoint(*rejected));
	EXPECT_EQ(state.dirtySinceTimestampSeconds(), 300);
	EXPECT_EQ(state.consecutiveFailures(), 0U);

	const auto failed = state.beginCheckpoint();
	ASSERT_EQ(failed, 1U);
	ASSERT_TRUE(state.acknowledgeFailure(*failed));
	EXPECT_EQ(state.dirtySinceTimestampSeconds(), 300);
	EXPECT_EQ(state.consecutiveFailures(), 1U);
}

TEST(PlayerPersistenceStateTest, FirstTimestampedObservationBackfillsAnUnmeasuredDirtyIntervalOnce) {
	PlayerPersistenceState state;
	(void)state.markDirty();
	EXPECT_FALSE(state.dirtySinceTimestampSeconds().has_value());

	(void)state.markDirty(400);
	EXPECT_EQ(state.dirtySinceTimestampSeconds(), 400);
	(void)state.markDirty(500);
	EXPECT_EQ(state.dirtySinceTimestampSeconds(), 400);
}

TEST(PlayerPersistenceStateTest, ConcurrentDirtyMarksDoNotLoseGenerations) {
	PlayerPersistenceState state;
	constexpr uint32_t threadCount = 8;
	constexpr uint32_t marksPerThread = 250;
	std::vector<std::thread> workers;
	workers.reserve(threadCount);

	for (uint32_t threadIndex = 0; threadIndex < threadCount; ++threadIndex) {
		workers.emplace_back([&state] {
			for (uint32_t mark = 0; mark < marksPerThread; ++mark) {
				(void)state.markDirty();
			}
		});
	}
	for (auto &worker : workers) {
		worker.join();
	}

	EXPECT_EQ(state.dirtyGeneration(), threadCount * marksPerThread);
	EXPECT_TRUE(state.isDirty());
}

TEST(PlayerPersistenceStateTest, ConcurrentCheckpointBeginsProduceOneOwner) {
	PlayerPersistenceState state;
	(void)state.markDirty();
	constexpr uint32_t threadCount = 16;
	std::atomic<uint32_t> owners = 0;
	std::vector<std::thread> workers;
	workers.reserve(threadCount);

	for (uint32_t threadIndex = 0; threadIndex < threadCount; ++threadIndex) {
		workers.emplace_back([&state, &owners] {
			if (state.beginCheckpoint().has_value()) {
				owners.fetch_add(1, std::memory_order_relaxed);
			}
		});
	}
	for (auto &worker : workers) {
		worker.join();
	}

	EXPECT_EQ(owners.load(std::memory_order_relaxed), 1U);
	EXPECT_TRUE(state.hasCheckpointInFlight());
}
