#include <gtest/gtest.h>

#include "game/database_outage_mutation_gate.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <array>
	#include <chrono>
	#include <fstream>
	#include <sstream>
	#include <string>
	#include <string_view>
#endif

namespace {
	constexpr DatabaseOutageSnapshot makeSnapshot(DatabaseOutageState state) noexcept {
		DatabaseOutageSnapshot snapshot;
		snapshot.state = state;
		return snapshot;
	}

	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(PRS003_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}

	std::string_view functionBody(const std::string &source, std::string_view begin, std::string_view end) {
		const auto beginPosition = source.find(begin);
		EXPECT_NE(beginPosition, std::string::npos) << begin;
		if (beginPosition == std::string::npos) {
			return {};
		}

		const auto endPosition = source.find(end, beginPosition + begin.size());
		EXPECT_NE(endPosition, std::string::npos) << end;
		if (endPosition == std::string::npos) {
			return {};
		}
		return std::string_view(source).substr(beginPosition, endPosition - beginPosition);
	}
} // namespace

TEST(DatabaseOutageMutationGateTest, CapturesOnceExecutesOnceAndPreservesTheMutationResult) {
	using namespace std::chrono_literals;

	DatabaseOutageSnapshot snapshot = makeSnapshot(DatabaseOutageState::Healthy);
	snapshot.transitionCount = 7;
	snapshot.lastEventSequence = 11;
	snapshot.lastEventTime = 120ms;
	const auto original = snapshot;
	int captures = 0;
	int mutations = 0;

	const auto result = DatabaseOutageMutationGate::executeLive(
		[&] {
			++captures;
			return snapshot;
		},
		DatabaseOutageMutationOperation::CriticalDurable,
		GAME_STATE_NORMAL,
		[&] {
			++mutations;
			return false;
		}
	);

	EXPECT_TRUE(result.decision.allowed());
	EXPECT_TRUE(result.executed);
	EXPECT_FALSE(result.mutationResult);
	EXPECT_EQ(captures, 1);
	EXPECT_EQ(mutations, 1);
	EXPECT_EQ(snapshot.state, original.state);
	EXPECT_EQ(snapshot.transitionCount, original.transitionCount);
	EXPECT_EQ(snapshot.lastEventSequence, original.lastEventSequence);
	EXPECT_EQ(snapshot.lastEventTime, original.lastEventTime);
}

TEST(DatabaseOutageMutationGateTest, RejectsCriticalDurableOutageStatesBeforeMutation) {
	struct TestCase final {
		DatabaseOutageState state;
		DatabaseOutageMutationReason reason;
	};

	using enum DatabaseOutageMutationReason;
	using enum DatabaseOutageState;
	constexpr std::array cases {
		TestCase { Degraded, OutageDegradedDurableMutation },
		TestCase { Draining, OutageDraining },
		TestCase { Maintenance, OutageMaintenance },
	};

	for (const auto &testCase : cases) {
		SCOPED_TRACE(static_cast<int>(testCase.state));
		int captures = 0;
		int mutations = 0;
		const auto result = DatabaseOutageMutationGate::executeLive(
			[&] {
				++captures;
				return makeSnapshot(testCase.state);
			},
			DatabaseOutageMutationOperation::CriticalDurable,
			GAME_STATE_NORMAL,
			[&] {
				++mutations;
				return true;
			}
		);

		EXPECT_FALSE(result.decision.allowed());
		EXPECT_EQ(result.decision.reason, testCase.reason);
		EXPECT_FALSE(result.executed);
		EXPECT_FALSE(result.mutationResult);
		EXPECT_EQ(captures, 1);
		EXPECT_EQ(mutations, 0);
	}
}

TEST(DatabaseOutageMutationGateTest, RejectsLifecycleAndUnknownValuesWithoutMutation) {
	int mutations = 0;
	const auto mutation = [&] {
		++mutations;
		return true;
	};

	const auto lifecycleRejected = DatabaseOutageMutationGate::executeLive(
		[] { return makeSnapshot(DatabaseOutageState::Healthy); },
		DatabaseOutageMutationOperation::CriticalDurable,
		GAME_STATE_CLOSING,
		mutation
	);
	EXPECT_EQ(lifecycleRejected.decision.reason, DatabaseOutageMutationReason::LifecycleClosing);
	EXPECT_FALSE(lifecycleRejected.executed);

	const auto operationRejected = DatabaseOutageMutationGate::executeLive(
		[] { return makeSnapshot(DatabaseOutageState::Healthy); },
		static_cast<DatabaseOutageMutationOperation>(0xFF),
		GAME_STATE_NORMAL,
		mutation
	);
	EXPECT_EQ(operationRejected.decision.reason, DatabaseOutageMutationReason::UnknownOperation);
	EXPECT_FALSE(operationRejected.executed);

	auto unknownOutage = makeSnapshot(DatabaseOutageState::Healthy);
	unknownOutage.state = static_cast<DatabaseOutageState>(0xFF);
	const auto outageRejected = DatabaseOutageMutationGate::executeLive(
		[unknownOutage] { return unknownOutage; },
		DatabaseOutageMutationOperation::CriticalDurable,
		GAME_STATE_NORMAL,
		mutation
	);
	EXPECT_EQ(outageRejected.decision.reason, DatabaseOutageMutationReason::UnknownOutageState);
	EXPECT_FALSE(outageRejected.executed);
	EXPECT_EQ(mutations, 0);
}

TEST(DatabaseOutageMutationGateTest, ProducesDeterministicDecisionsForIdenticalInputs) {
	const auto snapshot = makeSnapshot(DatabaseOutageState::Degraded);
	int mutations = 0;
	const auto evaluate = [&] {
		return DatabaseOutageMutationGate::executeLive(
			[snapshot] { return snapshot; },
			DatabaseOutageMutationOperation::CriticalDurable,
			GAME_STATE_NORMAL,
			[&] {
				++mutations;
				return true;
			}
		);
	};

	const auto first = evaluate();
	const auto second = evaluate();

	EXPECT_EQ(first.decision, second.decision);
	EXPECT_EQ(first.executed, second.executed);
	EXPECT_EQ(first.mutationResult, second.mutationResult);
	EXPECT_EQ(mutations, 0);
}

TEST(DatabaseOutageMutationGateTest, WiresTheLiveBankSetterBehindTheCriticalDurableGate) {
	const auto source = readSource("src/game/bank/bank.cpp");
	const auto balance = functionBody(source, "bool Bank::balance(uint64_t amount) const", "uint64_t Bank::balance()");

	const auto gatePosition = balance.find("DatabaseOutageMutationGate::executeLive");
	const auto setterPosition = balance.find("bankable->setBankBalance(amount)");
	EXPECT_NE(gatePosition, std::string_view::npos);
	EXPECT_NE(setterPosition, std::string_view::npos);
	EXPECT_LT(gatePosition, setterPosition);
	EXPECT_NE(balance.find("getDatabaseOutageSnapshot"), std::string_view::npos);
	EXPECT_NE(balance.find("DatabaseOutageMutationOperation::CriticalDurable"), std::string_view::npos);
	EXPECT_NE(balance.find("g_game().getGameState()"), std::string_view::npos);
	EXPECT_NE(balance.find("return result.mutationResult;"), std::string_view::npos);
}
