#include <gtest/gtest.h>

#include "game/scheduling/player_checkpoint_attempt.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <atomic>
	#include <future>
	#include <stdexcept>
	#include <thread>
	#include <vector>
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

TEST(PlayerCheckpointQueueAdmissionTest, QueueFullReleasesCheckpointWithoutConsumingFailureBudget) {
	PlayerCheckpointQueueAdmission admission(1);
	ASSERT_EQ(admission.capacity(), 1U);
	ASSERT_TRUE(admission.tryAcquire());
	ASSERT_EQ(admission.outstanding(), 1U);

	PlayerPersistenceState state;
	(void)state.markDirty();
	const auto generation = state.beginCheckpoint();
	ASSERT_EQ(generation, 1U);

	const auto rejected = tryAdmitPlayerCheckpoint(admission, state, *generation);

	EXPECT_EQ(rejected.outcome, PlayerCheckpointQueueAdmissionOutcome::queueFull);
	EXPECT_TRUE(rejected.checkpointReleased);
	EXPECT_EQ(admission.outstanding(), 1U);
	EXPECT_TRUE(state.isDirty());
	EXPECT_FALSE(state.hasCheckpointInFlight());
	EXPECT_EQ(state.consecutiveFailures(), 0U);

	ASSERT_TRUE(admission.release());
	const auto retryGeneration = state.beginCheckpoint();
	ASSERT_EQ(retryGeneration, 1U);
	const auto admitted = tryAdmitPlayerCheckpoint(admission, state, *retryGeneration);
	ASSERT_EQ(admitted.outcome, PlayerCheckpointQueueAdmissionOutcome::admitted);
	EXPECT_FALSE(admitted.checkpointReleased);

	{
		PlayerCheckpointQueueSlot slot(admission);
		const auto retry = executePlayerCheckpointAttempt(state, *retryGeneration, [] { return true; });
		EXPECT_EQ(retry.outcome, PlayerCheckpointAttemptOutcome::saved);
		EXPECT_TRUE(retry.acknowledgementAccepted);
		EXPECT_FALSE(retry.followUpRequired);
	}

	EXPECT_EQ(admission.outstanding(), 0U);
	EXPECT_FALSE(state.isDirty());
}

TEST(PlayerCheckpointQueueAdmissionTest, ConcurrentAdmissionNeverExceedsCapacity) {
	constexpr uint32_t capacity = 3;
	constexpr uint32_t workerCount = 32;
	PlayerCheckpointQueueAdmission admission(capacity);
	std::atomic<uint32_t> admitted = 0;
	std::vector<std::thread> workers;
	workers.reserve(workerCount);

	for (uint32_t index = 0; index < workerCount; ++index) {
		workers.emplace_back([&] {
			if (admission.tryAcquire()) {
				admitted.fetch_add(1, std::memory_order_relaxed);
			}
		});
	}
	for (auto &worker : workers) {
		worker.join();
	}

	EXPECT_EQ(admitted.load(std::memory_order_relaxed), capacity);
	EXPECT_EQ(admission.outstanding(), capacity);
	EXPECT_FALSE(admission.tryAcquire());
	for (uint32_t index = 0; index < capacity; ++index) {
		EXPECT_TRUE(admission.release());
	}
	EXPECT_FALSE(admission.release());
	EXPECT_EQ(admission.outstanding(), 0U);
}

TEST(PlayerCheckpointQueueAdmissionTest, ReleasingCurrentSlotBeforeFollowUpAllowsCapacityOneProgress) {
	PlayerCheckpointQueueAdmission admission(1);
	PlayerPersistenceState state;
	(void)state.markDirty();
	const auto firstGeneration = state.beginCheckpoint();
	ASSERT_EQ(firstGeneration, 1U);
	ASSERT_EQ(
		tryAdmitPlayerCheckpoint(admission, state, *firstGeneration).outcome,
		PlayerCheckpointQueueAdmissionOutcome::admitted
	);
	PlayerCheckpointQueueSlot firstSlot(admission);

	EXPECT_EQ(state.markDirty(), 2U);
	const auto firstAttempt = executePlayerCheckpointAttempt(state, *firstGeneration, [] { return true; });
	ASSERT_TRUE(firstAttempt.acknowledgementAccepted);
	ASSERT_TRUE(firstAttempt.followUpRequired);
	ASSERT_TRUE(firstSlot.release());
	EXPECT_EQ(admission.outstanding(), 0U);

	const auto followUpGeneration = state.beginCheckpoint();
	ASSERT_EQ(followUpGeneration, 2U);
	ASSERT_EQ(
		tryAdmitPlayerCheckpoint(admission, state, *followUpGeneration).outcome,
		PlayerCheckpointQueueAdmissionOutcome::admitted
	);
	{
		PlayerCheckpointQueueSlot followUpSlot(admission);
		const auto followUpAttempt = executePlayerCheckpointAttempt(state, *followUpGeneration, [] { return true; });
		EXPECT_TRUE(followUpAttempt.acknowledgementAccepted);
		EXPECT_FALSE(followUpAttempt.followUpRequired);
	}

	EXPECT_EQ(admission.outstanding(), 0U);
	EXPECT_FALSE(state.isDirty());
}

TEST(PlayerCheckpointQueueAdmissionTest, ReleaseObserverRunsExactlyOnceForEarlyAndScopedRelease) {
	PlayerCheckpointQueueAdmission admission(1);
	uint32_t observations = 0;

	ASSERT_TRUE(admission.tryAcquire());
	{
		PlayerCheckpointQueueSlot slot(admission, [&observations] {
			++observations;
		});
		EXPECT_TRUE(slot.release());
		EXPECT_FALSE(slot.release());
	}
	EXPECT_EQ(observations, 1U);
	EXPECT_EQ(admission.outstanding(), 0U);

	ASSERT_TRUE(admission.tryAcquire());
	{
		PlayerCheckpointQueueSlot slot(admission, [&observations] {
			++observations;
		});
	}
	EXPECT_EQ(observations, 2U);
	EXPECT_EQ(admission.outstanding(), 0U);
}

TEST(PlayerCheckpointTelemetryTest, GaugeSummaryReportsBoundedQueueAndOldestDirtyOwner) {
	auto newer = std::make_shared<PlayerPersistenceState>();
	auto older = std::make_shared<PlayerPersistenceState>();
	auto clean = std::make_shared<PlayerPersistenceState>();
	(void)newer->markDirty(200);
	(void)older->markDirty(100);

	const auto initial = summarizePlayerCheckpointGauges(7, 2, { newer, older, clean });
	EXPECT_EQ(initial.queueCapacity, 7U);
	EXPECT_EQ(initial.queueOutstanding, 2U);
	EXPECT_EQ(initial.dirtyOwners, 2U);
	EXPECT_EQ(initial.oldestDirtyTimestampSeconds, 100);

	const auto olderGeneration = older->beginCheckpoint();
	ASSERT_EQ(olderGeneration, 1U);
	ASSERT_TRUE(older->acknowledgeSuccess(*olderGeneration));
	const auto afterSuccess = summarizePlayerCheckpointGauges(7, 1, { newer, older, clean });
	EXPECT_EQ(afterSuccess.dirtyOwners, 1U);
	EXPECT_EQ(afterSuccess.oldestDirtyTimestampSeconds, 200);
}

TEST(PlayerCheckpointTelemetryTest, UnmeasuredDirtyOwnerDoesNotInventATimestamp) {
	auto state = std::make_shared<PlayerPersistenceState>();
	(void)state->markDirty();

	const auto snapshot = summarizePlayerCheckpointGauges(1, 0, { state });
	EXPECT_EQ(snapshot.dirtyOwners, 1U);
	EXPECT_EQ(snapshot.oldestDirtyTimestampSeconds, 0);
}

TEST(PlayerCheckpointTelemetryTest, DistinguishesFailuresExceptionsRejectionsAndSubmissionFailures) {
	PlayerCheckpointTelemetry telemetry;
	telemetry.recordRequest();
	telemetry.recordAttempt();
	telemetry.recordSuccess();
	telemetry.recordFailure();
	telemetry.recordThrownAttempt();
	telemetry.recordQueueRejection();
	telemetry.recordSubmissionFailure();

	const auto snapshot = telemetry.snapshot();
	EXPECT_EQ(snapshot.requests, 1U);
	EXPECT_EQ(snapshot.attempts, 1U);
	EXPECT_EQ(snapshot.successes, 1U);
	EXPECT_EQ(snapshot.failures, 2U);
	EXPECT_EQ(snapshot.thrownAttempts, 1U);
	EXPECT_EQ(snapshot.queueRejections, 1U);
	EXPECT_EQ(snapshot.submissionFailures, 1U);
}

TEST(PlayerCheckpointTelemetryTest, ConcurrentCountersDoNotLoseEvents) {
	PlayerCheckpointTelemetry telemetry;
	constexpr uint32_t threadCount = 16;
	constexpr uint32_t eventsPerThread = 500;
	std::vector<std::thread> workers;
	workers.reserve(threadCount);

	for (uint32_t index = 0; index < threadCount; ++index) {
		workers.emplace_back([&telemetry] {
			for (uint32_t event = 0; event < eventsPerThread; ++event) {
				telemetry.recordRequest();
				telemetry.recordAttempt();
				telemetry.recordSuccess();
			}
		});
	}
	for (auto &worker : workers) {
		worker.join();
	}

	const auto snapshot = telemetry.snapshot();
	const auto expected = static_cast<uint64_t>(threadCount) * eventsPerThread;
	EXPECT_EQ(snapshot.requests, expected);
	EXPECT_EQ(snapshot.attempts, expected);
	EXPECT_EQ(snapshot.successes, expected);
	EXPECT_EQ(snapshot.failures, 0U);
}
