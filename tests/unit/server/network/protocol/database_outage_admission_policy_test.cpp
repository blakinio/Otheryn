#include <gtest/gtest.h>

#include "server/network/protocol/database_outage_admission_policy.hpp"

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

	constexpr DatabaseOutageAdmissionCallerContext regularCaller {};
	constexpr DatabaseOutageAdmissionCallerContext canAlwaysLoginCaller { .canAlwaysLogin = true };
	constexpr DatabaseOutageAdmissionCallerContext diagnosticCaller { .staffDiagnostic = true };

	constexpr auto compileTimeDecision = DatabaseOutageAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		DatabaseOutageAdmissionOperation::AccountLogin,
		regularCaller,
		GAME_STATE_NORMAL
	);
	static_assert(compileTimeDecision.allowed());
	static_assert(compileTimeDecision.reason == DatabaseOutageAdmissionReason::Allowed);
	static_assert(noexcept(DatabaseOutageAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		DatabaseOutageAdmissionOperation::AccountLogin,
		regularCaller,
		GAME_STATE_NORMAL
	)));
	static_assert(std::is_trivially_copyable_v<DatabaseOutageAdmissionDecision>);
}

TEST(DatabaseOutageAdmissionPolicyTest, AppliesTheFullOutageTableForEverySupportedOperation) {
	struct TestCase final {
		DatabaseOutageState outageState;
		DatabaseOutageAdmissionOperation operation;
		DatabaseOutageAdmissionCallerContext caller;
		DatabaseOutageAdmissionDisposition disposition;
		DatabaseOutageAdmissionReason reason;
	};

	using enum DatabaseOutageAdmissionDisposition;
	using enum DatabaseOutageAdmissionOperation;
	using enum DatabaseOutageAdmissionReason;
	using enum DatabaseOutageState;

	constexpr std::array cases {
		TestCase { Healthy, AccountLogin, regularCaller, Allow, Allowed },
		TestCase { Healthy, GameLogin, regularCaller, Allow, Allowed },
		TestCase { Healthy, ChannelHandoff, regularCaller, Allow, Allowed },
		TestCase { Healthy, StaffDiagnostic, diagnosticCaller, Allow, Allowed },
		TestCase { Degraded, AccountLogin, regularCaller, Reject, OutageDegraded },
		TestCase { Degraded, GameLogin, canAlwaysLoginCaller, Reject, OutageDegraded },
		TestCase { Degraded, ChannelHandoff, canAlwaysLoginCaller, Reject, OutageDegraded },
		TestCase { Degraded, StaffDiagnostic, diagnosticCaller, Reject, OutageDegraded },
		TestCase { Draining, AccountLogin, regularCaller, Reject, OutageDraining },
		TestCase { Draining, GameLogin, canAlwaysLoginCaller, Reject, OutageDraining },
		TestCase { Draining, ChannelHandoff, canAlwaysLoginCaller, Reject, OutageDraining },
		TestCase { Draining, StaffDiagnostic, diagnosticCaller, Reject, OutageDraining },
		TestCase { Maintenance, AccountLogin, regularCaller, Reject, OutageMaintenance },
		TestCase { Maintenance, GameLogin, canAlwaysLoginCaller, Reject, OutageMaintenance },
		TestCase { Maintenance, ChannelHandoff, canAlwaysLoginCaller, Reject, OutageMaintenance },
		TestCase { Maintenance, StaffDiagnostic, diagnosticCaller, Allow, Allowed },
	};

	for (const auto &testCase : cases) {
		SCOPED_TRACE(
			testing::Message()
			<< "outage=" << static_cast<int>(testCase.outageState)
			<< " operation=" << static_cast<int>(testCase.operation)
		);
		const auto decision = DatabaseOutageAdmissionPolicy::evaluate(
			makeSnapshot(testCase.outageState),
			testCase.operation,
			testCase.caller,
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

TEST(DatabaseOutageAdmissionPolicyTest, PreservesExistingLifecycleAndNarrowCanAlwaysLoginBehavior) {
	struct TestCase final {
		GameState_t lifecycleState;
		DatabaseOutageAdmissionOperation operation;
		DatabaseOutageAdmissionCallerContext caller;
		DatabaseOutageAdmissionDisposition disposition;
		DatabaseOutageAdmissionReason reason;
	};

	using enum DatabaseOutageAdmissionDisposition;
	using enum DatabaseOutageAdmissionOperation;
	using enum DatabaseOutageAdmissionReason;

	constexpr std::array cases {
		TestCase { GAME_STATE_STARTUP, AccountLogin, regularCaller, Reject, LifecycleStartup },
		TestCase { GAME_STATE_STARTUP, StaffDiagnostic, diagnosticCaller, Reject, LifecycleStartup },
		TestCase { GAME_STATE_INIT, AccountLogin, regularCaller, Allow, Allowed },
		TestCase { GAME_STATE_INIT, GameLogin, regularCaller, Allow, Allowed },
		TestCase { GAME_STATE_NORMAL, ChannelHandoff, regularCaller, Allow, Allowed },
		TestCase { GAME_STATE_CLOSED, AccountLogin, regularCaller, Allow, Allowed },
		TestCase { GAME_STATE_CLOSED, GameLogin, regularCaller, Reject, LifecycleClosed },
		TestCase { GAME_STATE_CLOSED, GameLogin, canAlwaysLoginCaller, Allow, Allowed },
		TestCase { GAME_STATE_CLOSED, ChannelHandoff, regularCaller, Reject, LifecycleClosed },
		TestCase { GAME_STATE_CLOSED, ChannelHandoff, canAlwaysLoginCaller, Allow, Allowed },
		TestCase { GAME_STATE_SHUTDOWN, AccountLogin, regularCaller, Reject, LifecycleShutdown },
		TestCase { GAME_STATE_SHUTDOWN, StaffDiagnostic, diagnosticCaller, Reject, LifecycleShutdown },
		TestCase { GAME_STATE_CLOSING, AccountLogin, regularCaller, Allow, Allowed },
		TestCase { GAME_STATE_CLOSING, GameLogin, regularCaller, Reject, LifecycleClosing },
		TestCase { GAME_STATE_CLOSING, GameLogin, canAlwaysLoginCaller, Allow, Allowed },
		TestCase { GAME_STATE_CLOSING, ChannelHandoff, regularCaller, Reject, LifecycleClosing },
		TestCase { GAME_STATE_CLOSING, ChannelHandoff, canAlwaysLoginCaller, Allow, Allowed },
		TestCase { GAME_STATE_MAINTAIN, AccountLogin, canAlwaysLoginCaller, Reject, LifecycleMaintenance },
		TestCase { GAME_STATE_MAINTAIN, GameLogin, canAlwaysLoginCaller, Reject, LifecycleMaintenance },
		TestCase { GAME_STATE_MAINTAIN, ChannelHandoff, canAlwaysLoginCaller, Reject, LifecycleMaintenance },
		TestCase { GAME_STATE_MAINTAIN, StaffDiagnostic, diagnosticCaller, Allow, Allowed },
	};

	for (const auto &testCase : cases) {
		SCOPED_TRACE(
			testing::Message()
			<< "lifecycle=" << static_cast<int>(testCase.lifecycleState)
			<< " operation=" << static_cast<int>(testCase.operation)
			<< " canAlwaysLogin=" << testCase.caller.canAlwaysLogin
			<< " staffDiagnostic=" << testCase.caller.staffDiagnostic
		);
		const auto decision = DatabaseOutageAdmissionPolicy::evaluate(
			makeSnapshot(DatabaseOutageState::Healthy),
			testCase.operation,
			testCase.caller,
			testCase.lifecycleState
		);

		EXPECT_EQ(decision.disposition, testCase.disposition);
		EXPECT_EQ(decision.reason, testCase.reason);
	}
}

TEST(DatabaseOutageAdmissionPolicyTest, RequiresExplicitDiagnosticClassificationAndCapability) {
	using enum DatabaseOutageAdmissionOperation;
	using enum DatabaseOutageAdmissionReason;

	const auto missingCapability = DatabaseOutageAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Maintenance),
		StaffDiagnostic,
		regularCaller,
		GAME_STATE_NORMAL
	);
	EXPECT_FALSE(missingCapability.allowed());
	EXPECT_EQ(missingCapability.reason, DiagnosticCapabilityRequired);

	const DatabaseOutageAdmissionCallerContext allCapabilities {
		.canAlwaysLogin = true,
		.staffDiagnostic = true,
	};
	const auto handoff = DatabaseOutageAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Maintenance),
		ChannelHandoff,
		allCapabilities,
		GAME_STATE_NORMAL
	);
	const auto diagnostic = DatabaseOutageAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Maintenance),
		StaffDiagnostic,
		allCapabilities,
		GAME_STATE_NORMAL
	);

	EXPECT_FALSE(handoff.allowed());
	EXPECT_EQ(handoff.reason, OutageMaintenance);
	EXPECT_TRUE(diagnostic.allowed());
	EXPECT_EQ(diagnostic.reason, Allowed);
}

TEST(DatabaseOutageAdmissionPolicyTest, RejectsUnknownOperationLifecycleAndOutageValuesFailClosed) {
	using enum DatabaseOutageAdmissionReason;

	const auto unknownOperation = DatabaseOutageAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		static_cast<DatabaseOutageAdmissionOperation>(0xFF),
		regularCaller,
		GAME_STATE_NORMAL
	);
	EXPECT_FALSE(unknownOperation.allowed());
	EXPECT_EQ(unknownOperation.reason, UnknownOperation);

	const auto unknownLifecycle = DatabaseOutageAdmissionPolicy::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		DatabaseOutageAdmissionOperation::AccountLogin,
		regularCaller,
		static_cast<GameState_t>(0xFF)
	);
	EXPECT_FALSE(unknownLifecycle.allowed());
	EXPECT_EQ(unknownLifecycle.reason, UnknownLifecycleState);

	auto unknownOutageSnapshot = makeSnapshot(DatabaseOutageState::Healthy);
	unknownOutageSnapshot.state = static_cast<DatabaseOutageState>(0xFF);
	const auto unknownOutage = DatabaseOutageAdmissionPolicy::evaluate(
		unknownOutageSnapshot,
		DatabaseOutageAdmissionOperation::AccountLogin,
		regularCaller,
		GAME_STATE_NORMAL
	);
	EXPECT_FALSE(unknownOutage.allowed());
	EXPECT_EQ(unknownOutage.reason, UnknownOutageState);
}

TEST(DatabaseOutageAdmissionPolicyTest, UsesOnlySuppliedImmutableInputsAndIsDeterministic) {
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

	const auto first = DatabaseOutageAdmissionPolicy::evaluate(
		snapshot,
		DatabaseOutageAdmissionOperation::ChannelHandoff,
		canAlwaysLoginCaller,
		GAME_STATE_NORMAL
	);
	const auto second = DatabaseOutageAdmissionPolicy::evaluate(
		snapshot,
		DatabaseOutageAdmissionOperation::ChannelHandoff,
		canAlwaysLoginCaller,
		GAME_STATE_NORMAL
	);

	EXPECT_EQ(first, second);
	EXPECT_FALSE(first.allowed());
	EXPECT_EQ(first.reason, DatabaseOutageAdmissionReason::OutageDegraded);
	expectSnapshotEqual(snapshot, original);

	auto healthySnapshot = snapshot;
	healthySnapshot.state = DatabaseOutageState::Healthy;
	const auto healthy = DatabaseOutageAdmissionPolicy::evaluate(
		healthySnapshot,
		DatabaseOutageAdmissionOperation::ChannelHandoff,
		canAlwaysLoginCaller,
		GAME_STATE_NORMAL
	);
	EXPECT_TRUE(healthy.allowed());
	EXPECT_NE(first, healthy);
}
