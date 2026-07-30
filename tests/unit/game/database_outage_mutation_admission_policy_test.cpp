#include <gtest/gtest.h>

#include "game/database_outage_mutation_admission_policy.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <array>
	#include <chrono>
	#include <type_traits>
#endif

namespace {
	constexpr DatabaseOutageSnapshot makeSnapshot(DatabaseOutageState state) noexcept {
		DatabaseOutageSnapshot snapshot;
		snapshot.state = state;
		return snapshot;
	}

	void expectSnapshotEqual(const DatabaseOutageSnapshot &actual, const DatabaseOutageSnapshot &expected) {
		EXPECT_EQ(actual.state, expected.state);
		EXPECT_EQ(actual.lastTransitionReason, expected.lastTransitionReason);
		EXPECT_EQ(actual.transitionCount, expected.transitionCount);
		EXPECT_EQ(actual.firstFailureTime, expected.firstFailureTime);
		EXPECT_EQ(actual.degradedDeadline, expected.degradedDeadline);
		EXPECT_EQ(actual.drainDeadline, expected.drainDeadline);
		EXPECT_EQ(actual.lastFailureReason, expected.lastFailureReason);
		EXPECT_EQ(actual.lastFailureOutcome, expected.lastFailureOutcome);
		EXPECT_EQ(actual.recoveryEvidenceAccepted, expected.recoveryEvidenceAccepted);
		EXPECT_EQ(actual.lastEventSequence, expected.lastEventSequence);
		EXPECT_EQ(actual.lastEventTime, expected.lastEventTime);
	}

	constexpr auto compileTimeDecision = DatabaseOutageMutationAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		DatabaseOutageMutationOperation::CriticalDurable,
		GAME_STATE_NORMAL
	);
	static_assert(compileTimeDecision.allowed());
	static_assert(compileTimeDecision.reason == DatabaseOutageMutationReason::Allowed);
	static_assert(noexcept(DatabaseOutageMutationAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		DatabaseOutageMutationOperation::CriticalDurable,
		GAME_STATE_NORMAL
	)));
	static_assert(std::is_trivially_copyable_v<DatabaseOutageMutationDecision>);
} // namespace

TEST(DatabaseOutageMutationAdmissionPolicyTest, AppliesTheFullOutageTableForEverySupportedOperation) {
	struct TestCase final {
		DatabaseOutageState outageState;
		DatabaseOutageMutationOperation operation;
		DatabaseOutageMutationDisposition disposition;
		DatabaseOutageMutationReason reason;
	};

	using enum DatabaseOutageMutationDisposition;
	using enum DatabaseOutageMutationOperation;
	using enum DatabaseOutageMutationReason;
	using enum DatabaseOutageState;

	constexpr std::array cases {
		TestCase { Healthy, CriticalDurable, Allow, Allowed },
		TestCase { Healthy, OrdinaryDurable, Allow, Allowed },
		TestCase { Healthy, EphemeralNonDurable, Allow, Allowed },
		TestCase { Degraded, CriticalDurable, Reject, OutageDegradedDurableMutation },
		TestCase { Degraded, OrdinaryDurable, Reject, OutageDegradedDurableMutation },
		TestCase { Degraded, EphemeralNonDurable, Allow, Allowed },
		TestCase { Draining, CriticalDurable, Reject, OutageDraining },
		TestCase { Draining, OrdinaryDurable, Reject, OutageDraining },
		TestCase { Draining, EphemeralNonDurable, Reject, OutageDraining },
		TestCase { Maintenance, CriticalDurable, Reject, OutageMaintenance },
		TestCase { Maintenance, OrdinaryDurable, Reject, OutageMaintenance },
		TestCase { Maintenance, EphemeralNonDurable, Reject, OutageMaintenance },
	};

	for (const auto &testCase : cases) {
		SCOPED_TRACE(
			testing::Message()
			<< "outage=" << static_cast<int>(testCase.outageState)
			<< " operation=" << static_cast<int>(testCase.operation)
		);
		const auto decision = DatabaseOutageMutationAdmissionPolicy::evaluate(
			makeSnapshot(testCase.outageState),
			testCase.operation,
			GAME_STATE_NORMAL
		);

		EXPECT_EQ(decision.disposition, testCase.disposition);
		EXPECT_EQ(decision.reason, testCase.reason);
		EXPECT_EQ(decision.operation, testCase.operation);
		EXPECT_EQ(decision.outageState, testCase.outageState);
		EXPECT_EQ(decision.lifecycleState, GAME_STATE_NORMAL);
		EXPECT_EQ(decision.allowed(), testCase.disposition == Allow);
	}
}

TEST(DatabaseOutageMutationAdmissionPolicyTest, AppliesTheLifecycleTableBeforeOutageAdmission) {
	struct TestCase final {
		GameState_t lifecycleState;
		DatabaseOutageMutationOperation operation;
		DatabaseOutageMutationDisposition disposition;
		DatabaseOutageMutationReason reason;
	};

	using enum DatabaseOutageMutationDisposition;
	using enum DatabaseOutageMutationOperation;
	using enum DatabaseOutageMutationReason;

	constexpr std::array cases {
		TestCase { GAME_STATE_STARTUP, CriticalDurable, Reject, LifecycleStartup },
		TestCase { GAME_STATE_STARTUP, OrdinaryDurable, Reject, LifecycleStartup },
		TestCase { GAME_STATE_STARTUP, EphemeralNonDurable, Reject, LifecycleStartup },
		TestCase { GAME_STATE_INIT, CriticalDurable, Allow, Allowed },
		TestCase { GAME_STATE_INIT, OrdinaryDurable, Allow, Allowed },
		TestCase { GAME_STATE_INIT, EphemeralNonDurable, Allow, Allowed },
		TestCase { GAME_STATE_NORMAL, CriticalDurable, Allow, Allowed },
		TestCase { GAME_STATE_NORMAL, OrdinaryDurable, Allow, Allowed },
		TestCase { GAME_STATE_NORMAL, EphemeralNonDurable, Allow, Allowed },
		TestCase { GAME_STATE_CLOSING, CriticalDurable, Reject, LifecycleClosing },
		TestCase { GAME_STATE_CLOSING, OrdinaryDurable, Reject, LifecycleClosing },
		TestCase { GAME_STATE_CLOSING, EphemeralNonDurable, Reject, LifecycleClosing },
		TestCase { GAME_STATE_CLOSED, CriticalDurable, Reject, LifecycleClosed },
		TestCase { GAME_STATE_CLOSED, OrdinaryDurable, Reject, LifecycleClosed },
		TestCase { GAME_STATE_CLOSED, EphemeralNonDurable, Reject, LifecycleClosed },
		TestCase { GAME_STATE_SHUTDOWN, CriticalDurable, Reject, LifecycleShutdown },
		TestCase { GAME_STATE_SHUTDOWN, OrdinaryDurable, Reject, LifecycleShutdown },
		TestCase { GAME_STATE_SHUTDOWN, EphemeralNonDurable, Reject, LifecycleShutdown },
		TestCase { GAME_STATE_MAINTAIN, CriticalDurable, Reject, LifecycleMaintenance },
		TestCase { GAME_STATE_MAINTAIN, OrdinaryDurable, Reject, LifecycleMaintenance },
		TestCase { GAME_STATE_MAINTAIN, EphemeralNonDurable, Reject, LifecycleMaintenance },
	};

	for (const auto &testCase : cases) {
		SCOPED_TRACE(
			testing::Message()
			<< "lifecycle=" << static_cast<int>(testCase.lifecycleState)
			<< " operation=" << static_cast<int>(testCase.operation)
		);
		const auto decision = DatabaseOutageMutationAdmissionPolicy::evaluate(
			makeSnapshot(DatabaseOutageState::Healthy),
			testCase.operation,
			testCase.lifecycleState
		);

		EXPECT_EQ(decision.disposition, testCase.disposition);
		EXPECT_EQ(decision.reason, testCase.reason);
		EXPECT_EQ(decision.lifecycleState, testCase.lifecycleState);
	}
}

TEST(DatabaseOutageMutationAdmissionPolicyTest, RejectsUnknownOperationLifecycleAndOutageValuesFailClosed) {
	using enum DatabaseOutageMutationReason;

	const auto unknownOperation = DatabaseOutageMutationAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		static_cast<DatabaseOutageMutationOperation>(0xFF),
		GAME_STATE_NORMAL
	);
	EXPECT_FALSE(unknownOperation.allowed());
	EXPECT_EQ(unknownOperation.reason, UnknownOperation);

	const auto unknownLifecycle = DatabaseOutageMutationAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		DatabaseOutageMutationOperation::EphemeralNonDurable,
		static_cast<GameState_t>(0xFF)
	);
	EXPECT_FALSE(unknownLifecycle.allowed());
	EXPECT_EQ(unknownLifecycle.reason, UnknownLifecycleState);

	auto unknownOutageSnapshot = makeSnapshot(DatabaseOutageState::Healthy);
	unknownOutageSnapshot.state = static_cast<DatabaseOutageState>(0xFF);
	const auto unknownOutage = DatabaseOutageMutationAdmissionPolicy::evaluate(
		unknownOutageSnapshot,
		DatabaseOutageMutationOperation::EphemeralNonDurable,
		GAME_STATE_NORMAL
	);
	EXPECT_FALSE(unknownOutage.allowed());
	EXPECT_EQ(unknownOutage.reason, UnknownOutageState);
}

TEST(DatabaseOutageMutationAdmissionPolicyTest, UsesOnlySuppliedImmutableInputsAndIsDeterministic) {
	using namespace std::chrono_literals;

	DatabaseOutageSnapshot snapshot = makeSnapshot(DatabaseOutageState::Degraded);
	snapshot.lastTransitionReason = DatabaseOutageEventReason::FirstRuntimeFailure;
	snapshot.transitionCount = 7;
	snapshot.firstFailureTime = 100ms;
	snapshot.degradedDeadline = 200ms;
	snapshot.lastFailureReason = DatabaseOutageFailureReason::QueryFailed;
	snapshot.lastFailureOutcome = DatabaseOutageCommitOutcome::KnownNotCommitted;
	snapshot.lastEventSequence = 11;
	snapshot.lastEventTime = 120ms;
	const auto original = snapshot;

	const auto first = DatabaseOutageMutationAdmissionPolicy::evaluate(
		snapshot,
		DatabaseOutageMutationOperation::OrdinaryDurable,
		GAME_STATE_NORMAL
	);
	const auto second = DatabaseOutageMutationAdmissionPolicy::evaluate(
		snapshot,
		DatabaseOutageMutationOperation::OrdinaryDurable,
		GAME_STATE_NORMAL
	);

	EXPECT_EQ(first, second);
	EXPECT_FALSE(first.allowed());
	EXPECT_EQ(first.reason, DatabaseOutageMutationReason::OutageDegradedDurableMutation);
	expectSnapshotEqual(snapshot, original);

	const auto ephemeral = DatabaseOutageMutationAdmissionPolicy::evaluate(
		snapshot,
		DatabaseOutageMutationOperation::EphemeralNonDurable,
		GAME_STATE_NORMAL
	);
	EXPECT_TRUE(ephemeral.allowed());
	EXPECT_EQ(ephemeral.reason, DatabaseOutageMutationReason::Allowed);
	EXPECT_NE(first, ephemeral);
	expectSnapshotEqual(snapshot, original);
}
