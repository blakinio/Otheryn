#include <gtest/gtest.h>

#include "game/scheduling/player_checkpoint_attempt.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <future>
	#include <stdexcept>
#endif

TEST(PlayerCheckpointAttemptTest, FailedAttemptPreservesDirtyStateAndRequestsNoFollowUp) {
	PlayerPersistenceState state;
	(void)state.markDirty();
	const auto generation = state.beginCheckpoint();
	ASSERT_EQ(generation, 1U);

	uint32_t attempts = 0;
	const auto result = executePlayerCheckpointAttempt(state, *generation, [&attempts] {
		++attempts;
		return false;
	});

	EXPECT_EQ(attempts, 1U);
	EXPECT_EQ(result.outcome, PlayerCheckpointAttemptOutcome::saveFailed);
	EXPECT_TRUE(result.acknowledgementAccepted);
	EXPECT_FALSE(result.followUpRequired);
	EXPECT_FALSE(result.exception);
	EXPECT_TRUE(state.isDirty());
	EXPECT_FALSE(state.hasCheckpointInFlight());
	EXPECT_EQ(state.acknowledgedGeneration(), 0U);
	EXPECT_EQ(state.consecutiveFailures(), 1U);
}

TEST(PlayerCheckpointAttemptTest, LaterExplicitGenerationRetriesTheStillDirtyState) {
	PlayerPersistenceState state;
	(void)state.markDirty();
	const auto firstGeneration = state.beginCheckpoint();
	ASSERT_EQ(firstGeneration, 1U);
	ASSERT_EQ(
		executePlayerCheckpointAttempt(state, *firstGeneration, [] { return false; }).outcome,
		PlayerCheckpointAttemptOutcome::saveFailed
	);

	EXPECT_EQ(state.markDirty(), 2U);
	const auto retryGeneration = state.beginCheckpoint();
	ASSERT_EQ(retryGeneration, 2U);
	const auto retry = executePlayerCheckpointAttempt(state, *retryGeneration, [] { return true; });

	EXPECT_EQ(retry.outcome, PlayerCheckpointAttemptOutcome::saved);
	EXPECT_TRUE(retry.acknowledgementAccepted);
	EXPECT_FALSE(retry.followUpRequired);
	EXPECT_FALSE(state.isDirty());
	EXPECT_EQ(state.acknowledgedGeneration(), 2U);
	EXPECT_EQ(state.consecutiveFailures(), 0U);
}

TEST(PlayerCheckpointAttemptTest, ThrownAttemptPreservesDirtyStateAndCapturesFailure) {
	PlayerPersistenceState state;
	(void)state.markDirty();
	const auto generation = state.beginCheckpoint();
	ASSERT_EQ(generation, 1U);

	const auto result = executePlayerCheckpointAttempt(state, *generation, []() -> bool {
		throw std::runtime_error("controlled checkpoint failure");
	});

	EXPECT_EQ(result.outcome, PlayerCheckpointAttemptOutcome::saveThrew);
	EXPECT_TRUE(result.acknowledgementAccepted);
	EXPECT_FALSE(result.followUpRequired);
	EXPECT_TRUE(result.exception);
	EXPECT_TRUE(state.isDirty());
	EXPECT_FALSE(state.hasCheckpointInFlight());
	EXPECT_EQ(state.consecutiveFailures(), 1U);
}

TEST(PlayerCheckpointAttemptTest, NewerMutationRequestsFollowUpOnlyAfterSuccess) {
	PlayerPersistenceState state;
	(void)state.markDirty();
	const auto generation = state.beginCheckpoint();
	ASSERT_EQ(generation, 1U);
	EXPECT_EQ(state.markDirty(), 2U);

	const auto result = executePlayerCheckpointAttempt(state, *generation, [] { return true; });

	EXPECT_EQ(result.outcome, PlayerCheckpointAttemptOutcome::saved);
	EXPECT_TRUE(result.acknowledgementAccepted);
	EXPECT_TRUE(result.followUpRequired);
	EXPECT_TRUE(state.isDirty());
	EXPECT_EQ(state.acknowledgedGeneration(), 1U);
	EXPECT_EQ(state.dirtyGeneration(), 2U);
}

TEST(PlayerCheckpointAttemptTest, FailingPlayerDoesNotBlockIndependentSuccess) {
	PlayerPersistenceState failingState;
	PlayerPersistenceState succeedingState;
	(void)failingState.markDirty();
	(void)succeedingState.markDirty();
	const auto failingGeneration = failingState.beginCheckpoint();
	const auto succeedingGeneration = succeedingState.beginCheckpoint();
	ASSERT_EQ(failingGeneration, 1U);
	ASSERT_EQ(succeedingGeneration, 1U);

	std::promise<void> failingAttemptStarted;
	auto failingAttemptStartedFuture = failingAttemptStarted.get_future();
	std::promise<void> releaseFailingAttempt;
	auto releaseFailingAttemptFuture = releaseFailingAttempt.get_future().share();
	PlayerCheckpointAttemptResult failingResult {
		PlayerCheckpointAttemptOutcome::saveFailed,
		false,
		false,
		{},
	};

	auto failingWorker = std::async(std::launch::async, [&] {
		failingResult = executePlayerCheckpointAttempt(failingState, *failingGeneration, [&] {
			failingAttemptStarted.set_value();
			releaseFailingAttemptFuture.wait();
			return false;
		});
	});
	failingAttemptStartedFuture.wait();

	const auto succeedingResult = executePlayerCheckpointAttempt(succeedingState, *succeedingGeneration, [] { return true; });
	releaseFailingAttempt.set_value();
	failingWorker.get();

	EXPECT_EQ(succeedingResult.outcome, PlayerCheckpointAttemptOutcome::saved);
	EXPECT_TRUE(succeedingResult.acknowledgementAccepted);
	EXPECT_FALSE(succeedingState.isDirty());
	EXPECT_EQ(failingResult.outcome, PlayerCheckpointAttemptOutcome::saveFailed);
	EXPECT_TRUE(failingResult.acknowledgementAccepted);
	EXPECT_TRUE(failingState.isDirty());
}
