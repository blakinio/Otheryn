#include <gtest/gtest.h>

#include "game/scheduling/player_persistence_state.hpp"

TEST(PlayerPersistenceStateTest, StartsCleanAndCannotBeginCheckpoint) {
	PlayerPersistenceState state;

	EXPECT_FALSE(state.isDirty());
	EXPECT_FALSE(state.hasCheckpointInFlight());
	EXPECT_EQ(state.dirtyGeneration(), 0U);
	EXPECT_EQ(state.acknowledgedGeneration(), 0U);
	EXPECT_EQ(state.consecutiveFailures(), 0U);
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

	state.markDirty();
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

	state.markDirty();
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

TEST(PlayerPersistenceStateTest, SuccessfulExplicitAttemptResetsFailureBudget) {
	PlayerPersistenceState state;

	state.markDirty();
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

	state.markDirty();
	const auto first = state.beginCheckpoint();
	ASSERT_EQ(first, 1U);
	state.markDirty();

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

	state.markDirty();
	const auto first = state.beginCheckpoint(1);
	ASSERT_EQ(first, 1U);
	ASSERT_TRUE(state.acknowledgeFailure(*first));

	EXPECT_EQ(state.markDirty(), 2U);
	EXPECT_EQ(state.consecutiveFailures(), 1U);
	EXPECT_FALSE(state.canBeginCheckpoint(1));
	EXPECT_TRUE(state.canBeginCheckpoint(2));
}
