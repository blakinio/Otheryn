#include <gtest/gtest.h>

#include "server/network/protocol/database_outage_admission_gate.hpp"

namespace {
	[[nodiscard]] DatabaseOutageSnapshot makeSnapshot(DatabaseOutageState state) noexcept {
		DatabaseOutageSnapshot snapshot;
		snapshot.state = state;
		return snapshot;
	}

	struct CountingSnapshotProvider final {
		DatabaseOutageSnapshot snapshot;
		int* reads = nullptr;

		[[nodiscard]] DatabaseOutageSnapshot operator()() const noexcept {
			++(*reads);
			return snapshot;
		}
	};

	template <typename Mutation>
	bool runAdmittedMutation(
		CountingSnapshotProvider provider,
		DatabaseOutageAdmissionOperation operation,
		DatabaseOutageAdmissionCallerContext caller,
		GameState_t lifecycleState,
		Mutation &&mutation
	) {
		const auto decision = DatabaseOutageAdmissionGate::evaluateLive(provider, operation, caller, lifecycleState);
		if (!decision.allowed()) {
			return false;
		}

		std::forward<Mutation>(mutation)();
		return true;
	}
}

TEST(DatabaseOutageAdmissionGateTest, ReadsExactlyOneImmutableSnapshotPerAdmissionAttempt) {
	int reads = 0;
	const CountingSnapshotProvider provider {
		.snapshot = makeSnapshot(DatabaseOutageState::Healthy),
		.reads = &reads,
	};

	const auto decision = DatabaseOutageAdmissionGate::evaluateLive(
		provider,
		DatabaseOutageAdmissionOperation::AccountLogin,
		{},
		GAME_STATE_NORMAL
	);

	EXPECT_TRUE(decision.allowed());
	EXPECT_EQ(reads, 1);
}

TEST(DatabaseOutageAdmissionGateTest, ReusesOnePreWorkSnapshotForEarlyOutageAndCapabilityEvaluation) {
	int reads = 0;
	const auto snapshot = DatabaseOutageAdmissionGate::capture(
		CountingSnapshotProvider { makeSnapshot(DatabaseOutageState::Healthy), &reads }
	);

	const auto earlyOutageDecision = DatabaseOutageAdmissionGate::evaluate(
		snapshot,
		DatabaseOutageAdmissionOperation::GameLogin,
		{},
		GAME_STATE_NORMAL
	);
	const auto capabilityDecision = DatabaseOutageAdmissionGate::evaluate(
		snapshot,
		DatabaseOutageAdmissionOperation::GameLogin,
		{ .canAlwaysLogin = true },
		GAME_STATE_CLOSED
	);

	EXPECT_TRUE(earlyOutageDecision.allowed());
	EXPECT_TRUE(capabilityDecision.allowed());
	EXPECT_EQ(reads, 1);
}

TEST(DatabaseOutageAdmissionGateTest, PreservesNarrowCanAlwaysLoginLifecycleBehavior) {
	int gameReads = 0;
	int handoffReads = 0;
	const auto healthy = makeSnapshot(DatabaseOutageState::Healthy);

	const auto ordinaryGameLogin = DatabaseOutageAdmissionGate::evaluateLive(
		CountingSnapshotProvider { healthy, &gameReads },
		DatabaseOutageAdmissionOperation::GameLogin,
		{},
		GAME_STATE_CLOSED
	);
	const auto privilegedHandoff = DatabaseOutageAdmissionGate::evaluateLive(
		CountingSnapshotProvider { healthy, &handoffReads },
		DatabaseOutageAdmissionOperation::ChannelHandoff,
		{ .canAlwaysLogin = true },
		GAME_STATE_CLOSED
	);

	EXPECT_FALSE(ordinaryGameLogin.allowed());
	EXPECT_EQ(ordinaryGameLogin.reason, DatabaseOutageAdmissionReason::LifecycleClosed);
	EXPECT_TRUE(privilegedHandoff.allowed());
	EXPECT_EQ(gameReads, 1);
	EXPECT_EQ(handoffReads, 1);
}

TEST(DatabaseOutageAdmissionGateTest, OutageAndUnknownStatesRejectEvenPrivilegedCallersFailClosed) {
	int outageReads = 0;
	int unknownReads = 0;
	auto unknown = makeSnapshot(DatabaseOutageState::Healthy);
	unknown.state = static_cast<DatabaseOutageState>(0xFF);

	const auto outage = DatabaseOutageAdmissionGate::evaluateLive(
		CountingSnapshotProvider { makeSnapshot(DatabaseOutageState::Degraded), &outageReads },
		DatabaseOutageAdmissionOperation::GameLogin,
		{ .canAlwaysLogin = true },
		GAME_STATE_NORMAL
	);
	const auto unknownState = DatabaseOutageAdmissionGate::evaluateLive(
		CountingSnapshotProvider { unknown, &unknownReads },
		DatabaseOutageAdmissionOperation::ChannelHandoff,
		{ .canAlwaysLogin = true },
		GAME_STATE_NORMAL
	);

	EXPECT_FALSE(outage.allowed());
	EXPECT_EQ(outage.reason, DatabaseOutageAdmissionReason::OutageDegraded);
	EXPECT_FALSE(unknownState.allowed());
	EXPECT_EQ(unknownState.reason, DatabaseOutageAdmissionReason::UnknownOutageState);
	EXPECT_EQ(outageReads, 1);
	EXPECT_EQ(unknownReads, 1);
}

TEST(DatabaseOutageAdmissionGateTest, RejectionPreventsPostAdmissionMutation) {
	int reads = 0;
	int mutations = 0;
	const bool admitted = runAdmittedMutation(
		CountingSnapshotProvider { makeSnapshot(DatabaseOutageState::Draining), &reads },
		DatabaseOutageAdmissionOperation::ChannelHandoff,
		{ .canAlwaysLogin = true },
		GAME_STATE_NORMAL,
		[&mutations] { ++mutations; }
	);

	EXPECT_FALSE(admitted);
	EXPECT_EQ(reads, 1);
	EXPECT_EQ(mutations, 0);
}
