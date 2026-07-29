#include <gtest/gtest.h>

#include "database/database_outage_state.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <atomic>
	#include <chrono>
	#include <thread>
	#include <vector>
#endif

using namespace std::chrono_literals;

TEST(DatabaseOutageStateMachineTest, RequiresFinitePositiveDurations) {
	EXPECT_THROW((DatabaseOutageStateMachine { { 0ms, 10ms } }), std::invalid_argument);
	EXPECT_THROW((DatabaseOutageStateMachine { { 10ms, 0ms } }), std::invalid_argument);
	EXPECT_THROW((DatabaseOutageStateMachine { { -1ms, 10ms } }), std::invalid_argument);
	EXPECT_THROW((DatabaseOutageStateMachine { { 10ms, -1ms } }), std::invalid_argument);
}

TEST(DatabaseOutageStateMachineTest, StartsHealthyWithNoFailureInterval) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	const auto snapshot = state.snapshot();

	EXPECT_EQ(snapshot.state, DatabaseOutageState::Healthy);
	EXPECT_EQ(snapshot.lastTransitionReason, DatabaseOutageEventReason::Initial);
	EXPECT_EQ(snapshot.transitionCount, 0U);
	EXPECT_FALSE(snapshot.firstFailureTime.has_value());
	EXPECT_FALSE(snapshot.degradedDeadline.has_value());
	EXPECT_FALSE(snapshot.drainDeadline.has_value());
	EXPECT_FALSE(snapshot.lastFailureReason.has_value());
	EXPECT_FALSE(snapshot.lastFailureOutcome.has_value());
	EXPECT_FALSE(snapshot.recoveryEvidenceAccepted);
	EXPECT_EQ(snapshot.lastEventSequence, 0U);
	EXPECT_FALSE(snapshot.lastEventTime.has_value());
}

TEST(DatabaseOutageStateMachineTest, FirstKnownFailureEntersDegradedWithOneImmutableInterval) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	const auto result = state.runtimeFailure(
		1,
		DatabaseOutageFailureReason::QueryFailed,
		DatabaseOutageCommitOutcome::KnownNotCommitted,
		100ms
	);

	EXPECT_EQ(result.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(result.reason, DatabaseOutageEventReason::FirstRuntimeFailure);
	EXPECT_TRUE(result.stateChanged());
	EXPECT_EQ(result.before.state, DatabaseOutageState::Healthy);
	EXPECT_EQ(result.after.state, DatabaseOutageState::Degraded);
	EXPECT_EQ(result.after.firstFailureTime, 100ms);
	EXPECT_EQ(result.after.degradedDeadline, 200ms);
	EXPECT_FALSE(result.after.drainDeadline.has_value());
	EXPECT_EQ(result.after.lastFailureReason, DatabaseOutageFailureReason::QueryFailed);
	EXPECT_EQ(result.after.lastFailureOutcome, DatabaseOutageCommitOutcome::KnownNotCommitted);
	EXPECT_EQ(result.after.transitionCount, 1U);
}

TEST(DatabaseOutageStateMachineTest, UnknownOutcomeEntersDrainingDirectlyWithoutReplayState) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	const auto result = state.runtimeFailure(
		1,
		DatabaseOutageFailureReason::TransactionCommitFailed,
		DatabaseOutageCommitOutcome::Unknown,
		100ms
	);

	EXPECT_EQ(result.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(result.reason, DatabaseOutageEventReason::UnknownCommitOutcome);
	EXPECT_EQ(result.after.state, DatabaseOutageState::Draining);
	EXPECT_EQ(result.after.firstFailureTime, 100ms);
	EXPECT_FALSE(result.after.degradedDeadline.has_value());
	EXPECT_EQ(result.after.drainDeadline, 150ms);
	EXPECT_EQ(result.after.lastFailureOutcome, DatabaseOutageCommitOutcome::Unknown);
	EXPECT_EQ(result.after.transitionCount, 1U);
}

TEST(DatabaseOutageStateMachineTest, RepeatedDegradedFailurePreservesFirstFailureAndDeadline) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	ASSERT_EQ(
		state.runtimeFailure(1, DatabaseOutageFailureReason::ConnectionLost, DatabaseOutageCommitOutcome::KnownNotCommitted, 100ms).after.state,
		DatabaseOutageState::Degraded
	);

	const auto result = state.runtimeFailure(
		2,
		DatabaseOutageFailureReason::ServerGone,
		DatabaseOutageCommitOutcome::KnownNotCommitted,
		120ms
	);

	EXPECT_EQ(result.reason, DatabaseOutageEventReason::RepeatedRuntimeFailure);
	EXPECT_EQ(result.after.state, DatabaseOutageState::Draining);
	EXPECT_EQ(result.after.firstFailureTime, 100ms);
	EXPECT_EQ(result.after.degradedDeadline, 200ms);
	EXPECT_EQ(result.after.drainDeadline, 170ms);
	EXPECT_EQ(result.after.transitionCount, 2U);
}

TEST(DatabaseOutageStateMachineTest, DegradedDeadlineCannotFireEarlyAndThenEntersDraining) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	ASSERT_EQ(
		state.runtimeFailure(1, DatabaseOutageFailureReason::QueryFailed, DatabaseOutageCommitOutcome::KnownNotCommitted, 100ms).after.state,
		DatabaseOutageState::Degraded
	);

	const auto early = state.degradedDeadlineExpired(2, 199ms);
	EXPECT_EQ(early.disposition, DatabaseOutageEventDisposition::RejectedPrecondition);
	EXPECT_FALSE(early.stateChanged());
	EXPECT_EQ(early.after.state, DatabaseOutageState::Degraded);
	EXPECT_EQ(early.after.transitionCount, 1U);

	const auto expired = state.degradedDeadlineExpired(3, 200ms);
	EXPECT_EQ(expired.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(expired.reason, DatabaseOutageEventReason::DegradedDeadlineExpired);
	EXPECT_EQ(expired.after.state, DatabaseOutageState::Draining);
	EXPECT_EQ(expired.after.firstFailureTime, 100ms);
	EXPECT_EQ(expired.after.degradedDeadline, 200ms);
	EXPECT_EQ(expired.after.drainDeadline, 250ms);
	EXPECT_EQ(expired.after.transitionCount, 2U);
}

TEST(DatabaseOutageStateMachineTest, DrainCompletionAndDeadlineUseDistinctMaintenanceReasons) {
	DatabaseOutageStateMachine completedState({ 100ms, 50ms });
	ASSERT_EQ(
		completedState.runtimeFailure(1, DatabaseOutageFailureReason::TransactionCommitFailed, DatabaseOutageCommitOutcome::Unknown, 100ms).after.state,
		DatabaseOutageState::Draining
	);
	const auto completed = completedState.drainCompleted(2, 120ms);
	EXPECT_EQ(completed.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(completed.reason, DatabaseOutageEventReason::DrainCompleted);
	EXPECT_EQ(completed.after.state, DatabaseOutageState::Maintenance);
	EXPECT_EQ(completed.after.lastTransitionReason, DatabaseOutageEventReason::DrainCompleted);

	DatabaseOutageStateMachine timedOutState({ 100ms, 50ms });
	ASSERT_EQ(
		timedOutState.runtimeFailure(1, DatabaseOutageFailureReason::TransactionCommitFailed, DatabaseOutageCommitOutcome::Unknown, 100ms).after.state,
		DatabaseOutageState::Draining
	);
	const auto early = timedOutState.drainDeadlineExpired(2, 149ms);
	EXPECT_EQ(early.disposition, DatabaseOutageEventDisposition::RejectedPrecondition);
	EXPECT_EQ(early.after.state, DatabaseOutageState::Draining);

	const auto timedOut = timedOutState.drainDeadlineExpired(3, 150ms);
	EXPECT_EQ(timedOut.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(timedOut.reason, DatabaseOutageEventReason::DrainDeadlineExpired);
	EXPECT_EQ(timedOut.after.state, DatabaseOutageState::Maintenance);
	EXPECT_EQ(timedOut.after.lastTransitionReason, DatabaseOutageEventReason::DrainDeadlineExpired);
}

TEST(DatabaseOutageStateMachineTest, RecoveryEvidenceDoesNotAutoResumeAndResumeClearsAfterEmission) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	ASSERT_EQ(
		state.runtimeFailure(1, DatabaseOutageFailureReason::QueryFailed, DatabaseOutageCommitOutcome::KnownNotCommitted, 100ms).after.state,
		DatabaseOutageState::Degraded
	);

	const auto rejected = state.operatorResume(2, 110ms);
	EXPECT_EQ(rejected.disposition, DatabaseOutageEventDisposition::RejectedPrecondition);
	EXPECT_EQ(rejected.after.state, DatabaseOutageState::Degraded);

	const auto evidence = state.recoveryEvidenceAccepted(3, 120ms);
	EXPECT_EQ(evidence.disposition, DatabaseOutageEventDisposition::AcceptedNoStateChange);
	EXPECT_FALSE(evidence.stateChanged());
	EXPECT_EQ(evidence.after.state, DatabaseOutageState::Degraded);
	EXPECT_TRUE(evidence.after.recoveryEvidenceAccepted);
	EXPECT_EQ(evidence.after.transitionCount, 1U);

	const auto resumed = state.operatorResume(4, 130ms);
	EXPECT_EQ(resumed.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(resumed.after.state, DatabaseOutageState::Healthy);
	EXPECT_EQ(resumed.after.lastTransitionReason, DatabaseOutageEventReason::OperatorResume);
	EXPECT_EQ(resumed.after.firstFailureTime, 100ms);
	EXPECT_EQ(resumed.after.degradedDeadline, 200ms);
	EXPECT_TRUE(resumed.after.recoveryEvidenceAccepted);
	EXPECT_EQ(resumed.after.transitionCount, 2U);

	const auto current = state.snapshot();
	EXPECT_EQ(current.state, DatabaseOutageState::Healthy);
	EXPECT_EQ(current.lastTransitionReason, DatabaseOutageEventReason::OperatorResume);
	EXPECT_EQ(current.transitionCount, 2U);
	EXPECT_FALSE(current.firstFailureTime.has_value());
	EXPECT_FALSE(current.degradedDeadline.has_value());
	EXPECT_FALSE(current.drainDeadline.has_value());
	EXPECT_FALSE(current.lastFailureReason.has_value());
	EXPECT_FALSE(current.lastFailureOutcome.has_value());
	EXPECT_FALSE(current.recoveryEvidenceAccepted);
}

TEST(DatabaseOutageStateMachineTest, MaintenanceRequiresFreshRecoveryEvidenceAfterAnotherFailure) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	const auto maintenance = state.operatorEnterMaintenance(1, 100ms);
	ASSERT_EQ(maintenance.after.state, DatabaseOutageState::Maintenance);
	EXPECT_EQ(maintenance.after.lastTransitionReason, DatabaseOutageEventReason::OperatorMaintenance);

	EXPECT_EQ(state.recoveryEvidenceAccepted(2, 110ms).disposition, DatabaseOutageEventDisposition::AcceptedNoStateChange);
	EXPECT_TRUE(state.snapshot().recoveryEvidenceAccepted);

	const auto failure = state.runtimeFailure(
		3,
		DatabaseOutageFailureReason::RecoveryProbeFailed,
		DatabaseOutageCommitOutcome::KnownNotCommitted,
		120ms
	);
	EXPECT_EQ(failure.disposition, DatabaseOutageEventDisposition::AcceptedNoStateChange);
	EXPECT_EQ(failure.reason, DatabaseOutageEventReason::RuntimeFailureWhileUnavailable);
	EXPECT_EQ(failure.after.state, DatabaseOutageState::Maintenance);
	EXPECT_FALSE(failure.after.recoveryEvidenceAccepted);
	EXPECT_EQ(state.operatorResume(4, 130ms).disposition, DatabaseOutageEventDisposition::RejectedPrecondition);

	EXPECT_EQ(state.recoveryEvidenceAccepted(5, 140ms).disposition, DatabaseOutageEventDisposition::AcceptedNoStateChange);
	EXPECT_EQ(state.operatorResume(6, 150ms).after.state, DatabaseOutageState::Healthy);
}

TEST(DatabaseOutageStateMachineTest, DrainingRejectsRecoveryAndResumeWithoutReversingState) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	ASSERT_EQ(
		state.runtimeFailure(1, DatabaseOutageFailureReason::TransactionCommitFailed, DatabaseOutageCommitOutcome::Unknown, 100ms).after.state,
		DatabaseOutageState::Draining
	);

	const auto evidence = state.recoveryEvidenceAccepted(2, 110ms);
	EXPECT_EQ(evidence.disposition, DatabaseOutageEventDisposition::RejectedState);
	EXPECT_EQ(evidence.after.state, DatabaseOutageState::Draining);

	const auto resume = state.operatorResume(3, 120ms);
	EXPECT_EQ(resume.disposition, DatabaseOutageEventDisposition::RejectedState);
	EXPECT_EQ(resume.after.state, DatabaseOutageState::Draining);
	EXPECT_EQ(resume.after.transitionCount, 1U);
}

TEST(DatabaseOutageStateMachineTest, RejectsDuplicateSequenceAndRegressingTimeWithoutConsumingThem) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	ASSERT_EQ(
		state.runtimeFailure(5, DatabaseOutageFailureReason::QueryFailed, DatabaseOutageCommitOutcome::KnownNotCommitted, 100ms).after.state,
		DatabaseOutageState::Degraded
	);

	const auto duplicate = state.runtimeFailure(
		5,
		DatabaseOutageFailureReason::ServerGone,
		DatabaseOutageCommitOutcome::KnownNotCommitted,
		101ms
	);
	EXPECT_EQ(duplicate.disposition, DatabaseOutageEventDisposition::RejectedStaleOrDuplicate);
	EXPECT_EQ(duplicate.reason, DatabaseOutageEventReason::StaleOrDuplicateEvent);
	EXPECT_EQ(duplicate.after.lastEventSequence, 5U);
	EXPECT_EQ(duplicate.after.lastEventTime, 100ms);
	EXPECT_EQ(duplicate.after.state, DatabaseOutageState::Degraded);

	const auto regressingTime = state.runtimeFailure(
		6,
		DatabaseOutageFailureReason::ServerGone,
		DatabaseOutageCommitOutcome::KnownNotCommitted,
		99ms
	);
	EXPECT_EQ(regressingTime.disposition, DatabaseOutageEventDisposition::RejectedStaleOrDuplicate);
	EXPECT_EQ(regressingTime.after.lastEventSequence, 5U);
	EXPECT_EQ(regressingTime.after.lastEventTime, 100ms);

	const auto accepted = state.runtimeFailure(
		6,
		DatabaseOutageFailureReason::ServerGone,
		DatabaseOutageCommitOutcome::KnownNotCommitted,
		100ms
	);
	EXPECT_EQ(accepted.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(accepted.after.state, DatabaseOutageState::Draining);
	EXPECT_EQ(accepted.after.transitionCount, 2U);
}

TEST(DatabaseOutageStateMachineTest, ConcurrentDuplicateFailuresProduceOneSerializedTransition) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	constexpr uint32_t threadCount = 16;
	std::atomic<uint32_t> applied = 0;
	std::atomic<uint32_t> stale = 0;
	std::vector<std::thread> workers;
	workers.reserve(threadCount);

	for (uint32_t threadIndex = 0; threadIndex < threadCount; ++threadIndex) {
		workers.emplace_back([&state, &applied, &stale] {
			const auto result = state.runtimeFailure(
				1,
				DatabaseOutageFailureReason::ConnectionLost,
				DatabaseOutageCommitOutcome::KnownNotCommitted,
				100ms
			);
			if (result.disposition == DatabaseOutageEventDisposition::Applied) {
				applied.fetch_add(1, std::memory_order_relaxed);
			} else if (result.disposition == DatabaseOutageEventDisposition::RejectedStaleOrDuplicate) {
				stale.fetch_add(1, std::memory_order_relaxed);
			}
		});
	}
	for (auto &worker : workers) {
		worker.join();
	}

	EXPECT_EQ(applied.load(std::memory_order_relaxed), 1U);
	EXPECT_EQ(stale.load(std::memory_order_relaxed), threadCount - 1);
	const auto snapshot = state.snapshot();
	EXPECT_EQ(snapshot.state, DatabaseOutageState::Degraded);
	EXPECT_EQ(snapshot.transitionCount, 1U);
	EXPECT_EQ(snapshot.lastEventSequence, 1U);
	EXPECT_EQ(snapshot.firstFailureTime, 100ms);
	EXPECT_EQ(snapshot.degradedDeadline, 200ms);
}
