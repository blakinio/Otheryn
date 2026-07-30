#include <gtest/gtest.h>

#include "game/database_outage_drain_orchestrator.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <fstream>
	#include <sstream>
	#include <string>
	#include <string_view>
#endif

using namespace std::chrono_literals;

namespace {
	DatabaseOutageSnapshot drainingSnapshot(uint64_t transitionCount, DatabaseOutageTimePoint deadline) {
		return {
			.state = DatabaseOutageState::Draining,
			.lastTransitionReason = DatabaseOutageEventReason::DegradedDeadlineExpired,
			.transitionCount = transitionCount,
			.drainDeadline = deadline,
		};
	}

	DatabaseOutageSnapshot maintenanceSnapshot(uint64_t transitionCount) {
		return {
			.state = DatabaseOutageState::Maintenance,
			.lastTransitionReason = DatabaseOutageEventReason::DrainDeadlineExpired,
			.transitionCount = transitionCount,
		};
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

	size_t countOccurrences(std::string_view source, std::string_view needle) {
		size_t count = 0;
		size_t position = 0;
		while ((position = source.find(needle, position)) != std::string_view::npos) {
			++count;
			position += needle.size();
		}
		return count;
	}
}

TEST(DatabaseOutageDrainOrchestratorTest, SortsDeduplicatesAndCompletesOneFiniteGeneration) {
	DatabaseOutageDrainOrchestrator orchestrator;
	const auto snapshot = drainingSnapshot(7, 500ms);
	ASSERT_TRUE(orchestrator.begin(snapshot, { 3, 1, 3, 2 }));

	const auto first = orchestrator.next(snapshot, 100ms);
	ASSERT_EQ(first.action, DatabaseOutageDrainAction::AttemptPlayer);
	ASSERT_EQ(first.playerId, 1U);
	EXPECT_EQ(orchestrator.next(snapshot, 100ms).action, DatabaseOutageDrainAction::None);
	const DatabaseOutageDrainPlayerAttemptResult firstResult {
		.playerFound = true,
		.removed = true,
		.finalSaveObserved = true,
		.finalSaveSucceeded = true,
	};
	ASSERT_TRUE(orchestrator.recordAttempt(1, firstResult));

	const auto second = orchestrator.next(snapshot, 100ms);
	ASSERT_EQ(second.playerId, 2U);
	const DatabaseOutageDrainPlayerAttemptResult secondResult {
		.playerFound = true,
		.removed = true,
		.finalSaveObserved = true,
		.finalSaveSucceeded = false,
	};
	ASSERT_TRUE(orchestrator.recordAttempt(2, secondResult));

	const auto third = orchestrator.next(snapshot, 100ms);
	ASSERT_EQ(third.playerId, 3U);
	ASSERT_TRUE(orchestrator.recordAttempt(3, {}));

	EXPECT_EQ(orchestrator.next(snapshot, 100ms).action, DatabaseOutageDrainAction::CompleteDrain);
	const auto summary = orchestrator.summary();
	EXPECT_EQ(summary.transitionCount, 7U);
	EXPECT_EQ(summary.capturedPlayers, 3U);
	EXPECT_EQ(summary.attemptLimit, 3U);
	EXPECT_EQ(summary.attempts, 3U);
	EXPECT_EQ(summary.missingPlayers, 1U);
	EXPECT_EQ(summary.removalFailures, 0U);
	EXPECT_EQ(summary.finalSaveNotObserved, 0U);
	EXPECT_EQ(summary.finalSaveFailures, 1U);
	EXPECT_FALSE(summary.deadlineExpired);
	EXPECT_FALSE(summary.failClosed);
}

TEST(DatabaseOutageDrainOrchestratorTest, DeadlinePublishesBeforeFiniteCleanupContinues) {
	DatabaseOutageDrainOrchestrator orchestrator;
	const auto draining = drainingSnapshot(8, 100ms);
	ASSERT_TRUE(orchestrator.begin(draining, { 2, 1 }));
	EXPECT_EQ(orchestrator.next(draining, 100ms).action, DatabaseOutageDrainAction::ExpireDrain);

	const auto maintenance = maintenanceSnapshot(9);
	const auto firstCleanup = orchestrator.next(maintenance, 101ms);
	ASSERT_EQ(firstCleanup.playerId, 1U);
	const DatabaseOutageDrainPlayerAttemptResult firstCleanupResult {
		.playerFound = true,
		.removed = false,
		.finalSaveObserved = false,
		.finalSaveSucceeded = false,
	};
	ASSERT_TRUE(orchestrator.recordAttempt(1, firstCleanupResult));

	const auto secondCleanup = orchestrator.next(maintenance, 102ms);
	ASSERT_EQ(secondCleanup.playerId, 2U);
	const DatabaseOutageDrainPlayerAttemptResult secondCleanupResult {
		.playerFound = true,
		.removed = true,
		.finalSaveObserved = true,
		.finalSaveSucceeded = true,
	};
	ASSERT_TRUE(orchestrator.recordAttempt(2, secondCleanupResult));

	EXPECT_EQ(orchestrator.next(maintenance, 103ms).action, DatabaseOutageDrainAction::CleanupComplete);
	const auto summary = orchestrator.summary();
	EXPECT_TRUE(summary.deadlineExpired);
	EXPECT_EQ(summary.attempts, 2U);
	EXPECT_EQ(summary.removalFailures, 1U);
	EXPECT_EQ(summary.finalSaveNotObserved, 1U);
	EXPECT_EQ(summary.finalSaveFailures, 0U);
}

TEST(DatabaseOutageDrainOrchestratorTest, InvalidSnapshotFailsClosedWithoutAttempt) {
	DatabaseOutageDrainOrchestrator orchestrator;
	DatabaseOutageSnapshot invalid;
	invalid.state = DatabaseOutageState::Degraded;
	invalid.transitionCount = 1;
	EXPECT_FALSE(orchestrator.begin(invalid, { 1 }));
	EXPECT_EQ(orchestrator.next(invalid, 10ms).action, DatabaseOutageDrainAction::FailClosedMaintenance);
	EXPECT_EQ(orchestrator.summary().attempts, 0U);
	EXPECT_TRUE(orchestrator.summary().failClosed);
}

TEST(DatabaseOutageDrainOrchestratorTest, MismatchedAttemptResultFailsClosedWithoutAdvancing) {
	DatabaseOutageDrainOrchestrator orchestrator;
	const auto snapshot = drainingSnapshot(2, 500ms);
	ASSERT_TRUE(orchestrator.begin(snapshot, { 5 }));
	ASSERT_EQ(orchestrator.next(snapshot, 100ms).playerId, 5U);
	const DatabaseOutageDrainPlayerAttemptResult wrongPlayerResult {
		.playerFound = true,
		.removed = true,
		.finalSaveObserved = true,
		.finalSaveSucceeded = true,
	};
	EXPECT_FALSE(orchestrator.recordAttempt(6, wrongPlayerResult));
	EXPECT_EQ(orchestrator.next(snapshot, 100ms).action, DatabaseOutageDrainAction::FailClosedMaintenance);
	EXPECT_EQ(orchestrator.summary().attempts, 0U);
	EXPECT_TRUE(orchestrator.summary().failClosed);
}

TEST(DatabaseOutageDrainOrchestratorTest, MissingPlayerAdvancesOnceAndIsNeverRetried) {
	DatabaseOutageDrainOrchestrator orchestrator;
	const auto snapshot = drainingSnapshot(3, 500ms);
	ASSERT_TRUE(orchestrator.begin(snapshot, { 9, 10 }));
	ASSERT_EQ(orchestrator.next(snapshot, 100ms).playerId, 9U);
	ASSERT_TRUE(orchestrator.recordAttempt(9, {}));
	ASSERT_EQ(orchestrator.next(snapshot, 100ms).playerId, 10U);
	const DatabaseOutageDrainPlayerAttemptResult finalResult {
		.playerFound = true,
		.removed = true,
		.finalSaveObserved = true,
		.finalSaveSucceeded = true,
	};
	ASSERT_TRUE(orchestrator.recordAttempt(10, finalResult));
	EXPECT_EQ(orchestrator.next(snapshot, 100ms).action, DatabaseOutageDrainAction::CompleteDrain);
	EXPECT_EQ(orchestrator.summary().attempts, orchestrator.summary().attemptLimit);
}

TEST(DatabaseOutageDrainOrchestratorTest, RuntimeWiringReusesOneExistingSaveWithoutRetryOrReplay) {
	const auto databaseSource = readSource("src/database/database.cpp");
	const auto attemptBody = functionBody(
		databaseSource,
		"DatabaseOutageDrainPlayerAttemptResult attemptDatabaseOutageDrainPlayer",
		"void logDatabaseOutageDrainSummary"
	);
	EXPECT_NE(attemptBody.find("removePlayerForDatabaseOutageDrain"), std::string_view::npos);
	EXPECT_EQ(attemptBody.find("mysql_query"), std::string_view::npos);
	EXPECT_EQ(attemptBody.find("mysql_ping"), std::string_view::npos);
	EXPECT_EQ(attemptBody.find("connect("), std::string_view::npos);

	const auto decisionBody = functionBody(
		databaseSource,
		"void handleDatabaseOutageDrainDecision",
		"void runDatabaseOutageDrainTick"
	);
	EXPECT_NE(decisionBody.find("drainCompleted"), std::string_view::npos);
	EXPECT_NE(decisionBody.find("drainDeadlineExpired"), std::string_view::npos);
	EXPECT_EQ(decisionBody.find("while ("), std::string_view::npos);
	EXPECT_EQ(decisionBody.find("for ("), std::string_view::npos);
	EXPECT_EQ(decisionBody.find("mysql_query"), std::string_view::npos);
	EXPECT_EQ(decisionBody.find("mysql_ping"), std::string_view::npos);
	EXPECT_EQ(decisionBody.find("connect("), std::string_view::npos);

	const auto schedulerBody = functionBody(
		databaseSource,
		"void scheduleDatabaseOutageDrainTick",
		"void handleDatabaseOutageDrainDecision"
	);
	EXPECT_EQ(countOccurrences(schedulerBody, "scheduleEvent("), 1U);
	EXPECT_EQ(schedulerBody.find("cycleEvent("), std::string_view::npos);
	EXPECT_EQ(schedulerBody.find("while ("), std::string_view::npos);

	const auto saveManagerSource = readSource("src/game/scheduling/save_manager.cpp");
	const auto removalBody = functionBody(
		saveManagerSource,
		"DatabaseOutageDrainPlayerRemovalResult SaveManager::removePlayerForDatabaseOutageDrain",
		"bool SaveManager::savePlayerFinal"
	);
	EXPECT_EQ(countOccurrences(removalBody, "player->removePlayer(true, true);"), 1U);
	EXPECT_EQ(removalBody.find("savePlayerFinal("), std::string_view::npos);
	EXPECT_EQ(removalBody.find("doSavePlayer("), std::string_view::npos);
	EXPECT_EQ(removalBody.find("while ("), std::string_view::npos);
	EXPECT_EQ(removalBody.find("for ("), std::string_view::npos);

	const auto playerSource = readSource("src/creatures/players/player.cpp");
	const auto onRemoveBody = functionBody(
		playerSource,
		"void Player::onRemoveCreature",
		"void Player::onCreatureMove"
	);
	EXPECT_EQ(countOccurrences(onRemoveBody, "g_saveManager().savePlayer(player);"), 1U);
}
