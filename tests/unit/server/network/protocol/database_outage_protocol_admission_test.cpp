#include <gtest/gtest.h>

#include "server/network/protocol/database_outage_protocol_admission.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <array>
	#include <string_view>
#endif

namespace {
	constexpr DatabaseOutageSnapshot makeSnapshot(DatabaseOutageState state) noexcept {
		DatabaseOutageSnapshot snapshot;
		snapshot.state = state;
		return snapshot;
	}

	constexpr auto healthyAccount = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		DatabaseOutageAdmissionOperation::AccountLogin,
		{},
		GAME_STATE_NORMAL
	);
	static_assert(healthyAccount.allowed());
	static_assert(healthyAccount.message.empty());
	static_assert(noexcept(DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		DatabaseOutageAdmissionOperation::AccountLogin,
		{},
		GAME_STATE_NORMAL
	)));
}

TEST(DatabaseOutageProtocolAdmissionTest, GatesEveryLiveOperationForOutageStates) {
	struct TestCase final {
		DatabaseOutageState outageState;
		DatabaseOutageAdmissionOperation operation;
		DatabaseOutageAdmissionCallerContext caller;
		DatabaseOutageAdmissionReason reason;
		std::string_view message;
	};

	using enum DatabaseOutageAdmissionOperation;
	using enum DatabaseOutageAdmissionReason;
	using enum DatabaseOutageState;
	using namespace DatabaseOutageProtocolAdmission;

	constexpr std::array cases {
		TestCase { Degraded, AccountLogin, {}, OutageDegraded, DegradedMessage },
		TestCase { Draining, AccountLogin, {}, OutageDraining, DrainingMessage },
		TestCase { Maintenance, AccountLogin, {}, OutageMaintenance, MaintenanceMessage },
		TestCase { Degraded, GameLogin, { .canAlwaysLogin = true }, OutageDegraded, DegradedMessage },
		TestCase { Draining, GameLogin, { .canAlwaysLogin = true }, OutageDraining, DrainingMessage },
		TestCase { Maintenance, GameLogin, { .canAlwaysLogin = true }, OutageMaintenance, MaintenanceMessage },
		TestCase { Degraded, ChannelHandoff, { .canAlwaysLogin = true }, OutageDegraded, DegradedMessage },
		TestCase { Draining, ChannelHandoff, { .canAlwaysLogin = true }, OutageDraining, DrainingMessage },
		TestCase { Maintenance, ChannelHandoff, { .canAlwaysLogin = true }, OutageMaintenance, MaintenanceMessage },
	};

	for (const auto &testCase : cases) {
		SCOPED_TRACE(
			testing::Message()
			<< "outage=" << static_cast<int>(testCase.outageState)
			<< " operation=" << static_cast<int>(testCase.operation)
		);
		const auto result = evaluate(
			makeSnapshot(testCase.outageState),
			testCase.operation,
			testCase.caller,
			GAME_STATE_NORMAL
		);

		EXPECT_TRUE(result.rejected());
		EXPECT_EQ(result.decision.reason, testCase.reason);
		EXPECT_EQ(result.message, testCase.message);
	}
}

TEST(DatabaseOutageProtocolAdmissionTest, DefersOnlyExistingGameLoginClosingAndClosedChecks) {
	using enum DatabaseOutageAdmissionOperation;
	using enum DatabaseOutageAdmissionReason;

	const auto closing = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		GameLogin,
		{},
		GAME_STATE_CLOSING,
		true
	);
	const auto closed = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		GameLogin,
		{},
		GAME_STATE_CLOSED,
		true
	);
	const auto outageStillRejects = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Degraded),
		GameLogin,
		{ .canAlwaysLogin = true },
		GAME_STATE_CLOSING,
		true
	);

	EXPECT_TRUE(closing.defersExistingLifecycle());
	EXPECT_EQ(closing.decision.reason, LifecycleClosing);
	EXPECT_TRUE(closed.defersExistingLifecycle());
	EXPECT_EQ(closed.decision.reason, LifecycleClosed);
	EXPECT_TRUE(outageStillRejects.rejected());
	EXPECT_EQ(outageStillRejects.decision.reason, OutageDegraded);
}

TEST(DatabaseOutageProtocolAdmissionTest, HandoffUsesOnlyTheExistingPlayerCapability) {
	using enum DatabaseOutageAdmissionOperation;
	using enum DatabaseOutageAdmissionReason;

	const auto ordinaryClosing = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		ChannelHandoff,
		{},
		GAME_STATE_CLOSING
	);
	const auto privilegedClosing = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		ChannelHandoff,
		{ .canAlwaysLogin = true },
		GAME_STATE_CLOSING
	);
	const auto privilegedOutage = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Draining),
		ChannelHandoff,
		{ .canAlwaysLogin = true },
		GAME_STATE_NORMAL
	);

	EXPECT_TRUE(ordinaryClosing.rejected());
	EXPECT_EQ(ordinaryClosing.decision.reason, LifecycleClosing);
	EXPECT_EQ(ordinaryClosing.message, DatabaseOutageProtocolAdmission::ClosingMessage);
	EXPECT_TRUE(privilegedClosing.allowed());
	EXPECT_TRUE(privilegedOutage.rejected());
	EXPECT_EQ(privilegedOutage.decision.reason, OutageDraining);
}

TEST(DatabaseOutageProtocolAdmissionTest, StaffDiagnosticIsASeparateExplicitCapabilityPath) {
	using enum DatabaseOutageAdmissionOperation;
	using enum DatabaseOutageAdmissionReason;

	const auto missingCapability = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Maintenance),
		StaffDiagnostic,
		{},
		GAME_STATE_NORMAL
	);
	const auto canAlwaysIsNotDiagnostic = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Maintenance),
		StaffDiagnostic,
		{ .canAlwaysLogin = true },
		GAME_STATE_NORMAL
	);
	const auto explicitDiagnostic = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Maintenance),
		StaffDiagnostic,
		{ .staffDiagnostic = true },
		GAME_STATE_NORMAL
	);
	const auto degradedDiagnostic = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Degraded),
		StaffDiagnostic,
		{ .staffDiagnostic = true },
		GAME_STATE_NORMAL
	);

	EXPECT_TRUE(missingCapability.rejected());
	EXPECT_EQ(missingCapability.decision.reason, DiagnosticCapabilityRequired);
	EXPECT_TRUE(canAlwaysIsNotDiagnostic.rejected());
	EXPECT_EQ(canAlwaysIsNotDiagnostic.decision.reason, DiagnosticCapabilityRequired);
	EXPECT_TRUE(explicitDiagnostic.allowed());
	EXPECT_TRUE(degradedDiagnostic.rejected());
	EXPECT_EQ(degradedDiagnostic.decision.reason, OutageDegraded);
}

TEST(DatabaseOutageProtocolAdmissionTest, UnknownValuesRejectWithOneBoundedMessage) {
	using enum DatabaseOutageAdmissionOperation;
	using enum DatabaseOutageAdmissionReason;

	const auto unknownOperation = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		static_cast<DatabaseOutageAdmissionOperation>(0xFF),
		{},
		GAME_STATE_NORMAL
	);
	const auto unknownLifecycle = DatabaseOutageProtocolAdmission::evaluate(
		makeSnapshot(DatabaseOutageState::Healthy),
		AccountLogin,
		{},
		static_cast<GameState_t>(0xFF)
	);
	auto unknownSnapshot = makeSnapshot(DatabaseOutageState::Healthy);
	unknownSnapshot.state = static_cast<DatabaseOutageState>(0xFF);
	const auto unknownOutage = DatabaseOutageProtocolAdmission::evaluate(
		unknownSnapshot,
		AccountLogin,
		{},
		GAME_STATE_NORMAL
	);

	for (const auto* result : { &unknownOperation, &unknownLifecycle, &unknownOutage }) {
		EXPECT_TRUE(result->rejected());
		EXPECT_EQ(result->message, DatabaseOutageProtocolAdmission::UnavailableMessage);
		EXPECT_LT(result->message.size(), 128U);
		EXPECT_EQ(result->message.find("SELECT"), std::string_view::npos);
		EXPECT_EQ(result->message.find("player"), std::string_view::npos);
	}
	EXPECT_EQ(unknownOperation.decision.reason, UnknownOperation);
	EXPECT_EQ(unknownLifecycle.decision.reason, UnknownLifecycleState);
	EXPECT_EQ(unknownOutage.decision.reason, UnknownOutageState);
}

TEST(DatabaseOutageProtocolAdmissionTest, RepeatedEvaluationIsDeterministicAndSnapshotIsImmutable) {
	DatabaseOutageSnapshot snapshot = makeSnapshot(DatabaseOutageState::Degraded);
	snapshot.transitionCount = 7;
	snapshot.lastEventSequence = 11;
	const auto original = snapshot;

	const auto first = DatabaseOutageProtocolAdmission::evaluate(
		snapshot,
		DatabaseOutageAdmissionOperation::ChannelHandoff,
		{ .canAlwaysLogin = true },
		GAME_STATE_NORMAL
	);
	const auto second = DatabaseOutageProtocolAdmission::evaluate(
		snapshot,
		DatabaseOutageAdmissionOperation::ChannelHandoff,
		{ .canAlwaysLogin = true },
		GAME_STATE_NORMAL
	);

	EXPECT_EQ(first.decision, second.decision);
	EXPECT_EQ(first.disposition, second.disposition);
	EXPECT_EQ(first.message, second.message);
	EXPECT_EQ(snapshot.state, original.state);
	EXPECT_EQ(snapshot.transitionCount, original.transitionCount);
	EXPECT_EQ(snapshot.lastEventSequence, original.lastEventSequence);
}
