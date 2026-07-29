#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>
#include <string_view>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(PRS002_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}

	void expectContains(const std::string &source, std::string_view needle) {
		EXPECT_NE(source.find(needle), std::string::npos) << needle;
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

TEST(Prs002DirtyPlayerCheckpointContractTest, PinsScheduledSaveToRequestedPlayerObject) {
	const auto header = readSource("src/game/scheduling/save_manager.hpp");
	expectContains(header, "bool schedulePlayer(std::weak_ptr<Player> player);");
	expectContains(header, "bool scheduleDirtyPlayer(std::weak_ptr<Player> player, std::shared_ptr<PlayerPersistenceState> state);");
	expectContains(header, "std::owner_less<std::weak_ptr<Player>>");
	expectContains(header, "GUID or player runtime ID re-resolution");
	expectContains(header, "target the object that requested it");

	const auto source = readSource("src/game/scheduling/save_manager.cpp");
	expectContains(source, "auto playerToSave = playerPtr.lock();");
	expectContains(source, "auto state = persistenceStateFor(playerToSave);");
	expectContains(source, "state->markDirty(currentCheckpointTimestampSeconds())");
	expectContains(source, "const auto generation = state->beginCheckpoint();");
	EXPECT_EQ(source.find("m_playerMap"), std::string::npos);
}

TEST(Prs002DirtyPlayerCheckpointContractTest, AcknowledgesExactGenerationAndCoalescesNewerRequests) {
	const auto attempt = readSource("src/game/scheduling/player_checkpoint_attempt.hpp");
	expectContains(attempt, "state.acknowledgeFailure(generation)");
	expectContains(attempt, "state.acknowledgeSuccess(generation)");
	expectContains(attempt, "acknowledged && state.isDirty()");

	const auto source = readSource("src/game/scheduling/save_manager.cpp");
	expectContains(source, "executePlayerCheckpointAttempt(*state, generation");
	expectContains(source, "attempt.followUpRequired && player->isOnline()");
	expectContains(source, "scheduleDirtyPlayer(player, state);");
	expectContains(source, "Coalescing player save because a checkpoint is already in flight");

	const auto scheduleDirty = functionBody(source, "bool SaveManager::scheduleDirtyPlayer", "bool SaveManager::doSavePlayer");
	EXPECT_EQ(scheduleDirty.find("markDirty"), std::string_view::npos);
}

TEST(Prs002DirtyPlayerCheckpointContractTest, FailedAttemptHasNoImplicitFollowUpPath) {
	const auto attempt = readSource("src/game/scheduling/player_checkpoint_attempt.hpp");
	expectContains(attempt, "PlayerCheckpointAttemptOutcome::saveFailed");
	expectContains(attempt, "PlayerCheckpointAttemptOutcome::saveThrew");
	expectContains(attempt, "state.acknowledgeFailure(generation)");

	const auto source = readSource("src/game/scheduling/save_manager.cpp");
	const auto scheduleDirty = functionBody(source, "bool SaveManager::scheduleDirtyPlayer", "bool SaveManager::doSavePlayer");
	const auto successBranch = scheduleDirty.find("if (attempt.outcome == PlayerCheckpointAttemptOutcome::saved)");
	const auto followUp = scheduleDirty.find("if (attempt.followUpRequired");
	const auto failureBranch = scheduleDirty.find("if (!attempt.acknowledgementAccepted)", followUp);
	ASSERT_NE(successBranch, std::string_view::npos);
	ASSERT_NE(followUp, std::string_view::npos);
	ASSERT_NE(failureBranch, std::string_view::npos);
	EXPECT_LT(successBranch, followUp);
	EXPECT_LT(followUp, failureBranch);
}

TEST(Prs002DirtyPlayerCheckpointContractTest, BoundsQueueAdmissionBeforeDetachAndReleasesBeforeFollowUp) {
	const auto attempt = readSource("src/game/scheduling/player_checkpoint_attempt.hpp");
	expectContains(attempt, "DEFAULT_PLAYER_CHECKPOINT_QUEUE_CAPACITY = 1024");
	expectContains(attempt, "class PlayerCheckpointQueueAdmission final");
	expectContains(attempt, "state.abandonCheckpoint(generation)");

	const auto header = readSource("src/game/scheduling/save_manager.hpp");
	expectContains(header, "PlayerCheckpointQueueAdmission m_playerCheckpointQueueAdmission;");

	const auto source = readSource("src/game/scheduling/save_manager.cpp");
	const auto scheduleDirty = functionBody(source, "bool SaveManager::scheduleDirtyPlayer", "bool SaveManager::doSavePlayer");
	const auto admission = scheduleDirty.find("tryAdmitPlayerCheckpoint");
	const auto queueFull = scheduleDirty.find("PlayerCheckpointQueueAdmissionOutcome::queueFull");
	const auto detach = scheduleDirty.find("threadPool.detach_task");
	const auto earlyRelease = scheduleDirty.find("queueSlot.release()");
	const auto followUp = scheduleDirty.find("scheduleDirtyPlayer(player, state);");
	ASSERT_NE(admission, std::string_view::npos);
	ASSERT_NE(queueFull, std::string_view::npos);
	ASSERT_NE(detach, std::string_view::npos);
	ASSERT_NE(earlyRelease, std::string_view::npos);
	ASSERT_NE(followUp, std::string_view::npos);
	EXPECT_LT(admission, queueFull);
	EXPECT_LT(queueFull, detach);
	EXPECT_LT(earlyRelease, followUp);

	const auto savePlayer = functionBody(source, "bool SaveManager::savePlayer", "bool SaveManager::saveGuild");
	expectContains(std::string(savePlayer), "return schedulePlayer(player);");
}

TEST(Prs002DirtyPlayerCheckpointContractTest, MarksOnlyTrackedPlayerStorageMutations) {
	const auto managerHeader = readSource("src/game/scheduling/save_manager.hpp");
	expectContains(managerHeader, "static void markPlayerDirty(const std::shared_ptr<Player> &player);");
	expectContains(managerHeader, "inline static std::mutex m_playerPersistenceMutex;");

	const auto managerSource = readSource("src/game/scheduling/save_manager.cpp");
	const auto marker = functionBody(managerSource, "void SaveManager::markPlayerDirty", "bool SaveManager::schedulePlayer");
	expectContains(std::string(marker), "auto state = persistenceStateFor(player);");
	expectContains(std::string(marker), "state->markDirty(currentCheckpointTimestampSeconds())");
	EXPECT_EQ(marker.find("getInstance"), std::string_view::npos);
	EXPECT_EQ(marker.find("savePlayer("), std::string_view::npos);
	EXPECT_EQ(marker.find("schedulePlayer("), std::string_view::npos);

	const auto storage = readSource("src/creatures/players/components/player_storage.cpp");
	const auto ingest = functionBody(storage, "void PlayerStorage::ingest", "void PlayerStorage::add");
	expectContains(std::string(ingest), "add(row.key, row.value, true, false);");
	EXPECT_EQ(ingest.find("markPlayerDirty"), std::string_view::npos);

	const auto add = functionBody(storage, "void PlayerStorage::add", "int32_t PlayerStorage::get");
	expectContains(std::string(add), "if (shouldTrackModification)");
	expectContains(std::string(add), "SaveManager::markPlayerDirty(m_player.getPlayer());");
	EXPECT_EQ(add.find("g_saveManager"), std::string_view::npos);
	EXPECT_EQ(add.find("savePlayer("), std::string_view::npos);

	const auto remove = functionBody(storage, "bool PlayerStorage::remove", "void PlayerStorage::prepareForPersist");
	expectContains(std::string(remove), "SaveManager::markPlayerDirty(m_player.getPlayer());");
	EXPECT_EQ(remove.find("g_saveManager"), std::string_view::npos);
	EXPECT_EQ(remove.find("savePlayer("), std::string_view::npos);
}

TEST(Prs002DirtyPlayerCheckpointContractTest, ExportsBoundedLowCardinalityCheckpointMetrics) {
	const auto metricsHeader = readSource("src/lib/metrics/metrics.hpp");
	expectContains(metricsHeader, "void setGauge(std::string_view name, int64_t value)");
	expectContains(metricsHeader, "CreateInt64UpDownCounter");
	expectContains(metricsHeader, "gaugeValues");

	const auto source = readSource("src/game/scheduling/save_manager.cpp");
	expectContains(source, "player_checkpoint_queue_capacity");
	expectContains(source, "player_checkpoint_queue_outstanding");
	expectContains(source, "player_checkpoint_dirty_owners");
	expectContains(source, "player_checkpoint_oldest_dirty_timestamp_seconds");
	expectContains(source, "player_checkpoint_requests");
	expectContains(source, "player_checkpoint_attempts");
	expectContains(source, "player_checkpoint_successes");
	expectContains(source, "player_checkpoint_failures");
	expectContains(source, "player_checkpoint_thrown_attempts");
	expectContains(source, "player_checkpoint_queue_rejections");
	expectContains(source, "player_checkpoint_submission_failures");
	expectContains(source, "metrics::method_latency checkpointLatency(\"player_checkpoint_save\")");
	EXPECT_EQ(source.find("{ { \"player\""), std::string::npos);
	EXPECT_EQ(source.find("{ { \"guid\""), std::string::npos);
	EXPECT_EQ(source.find("{ { \"generation\""), std::string::npos);

	const auto state = readSource("src/game/scheduling/player_persistence_state.hpp");
	expectContains(state, "dirtySinceTimestampSeconds_");
	expectContains(state, "if (!isDirtyLocked())");
}

TEST(Prs002DirtyPlayerCheckpointContractTest, PreservesSaveOutcomeAndDomainBoundaries) {
	const auto manager = readSource("src/game/scheduling/save_manager.cpp");
	expectContains(manager, "Player::PlayerLock lock(player);");
	expectContains(manager, "bool saveSuccess = IOLoginData::savePlayer(player);");
	expectContains(manager, "return saveSuccess;");
	expectContains(manager, "return schedulePlayer(player);");
	expectContains(manager, "return doSavePlayer(player);");

	const auto loginData = readSource("src/io/iologindata.cpp");
	expectContains(loginData, "DBTransaction::executeWithinTransaction");
	expectContains(loginData, "stageOnlinePlayerWheelKV(player);");
	expectContains(loginData, "Exception occurred staging post-commit player data");
}

TEST(Prs002DirtyPlayerCheckpointContractTest, DoesNotMistakeSaveSideLockForMutationSerialization) {
	const auto player = readSource("src/creatures/players/player.cpp");
	const auto addSkillAdvance = functionBody(player, "void Player::addSkillAdvance", "void Player::setVarStats");
	expectContains(std::string(addSkillAdvance), "skills[skill].tries += count;");
	EXPECT_EQ(addSkillAdvance.find("PlayerLock"), std::string_view::npos);
	EXPECT_EQ(addSkillAdvance.find("mutex"), std::string_view::npos);
}

TEST(Prs002DirtyPlayerCheckpointContractTest, RecordsGenerationSafeTargetAndBoundedMutationCoverage) {
	const auto contract = readSource("docs/architecture/prs-002-dirty-player-checkpoint-contract.md");
	expectContains(contract, "Every persistence-relevant mutation advances a monotonic dirty generation.");
	expectContains(contract, "The save result acknowledges only the captured generation.");
	expectContains(contract, "A mutation during save remains dirty");
	expectContains(contract, "Queue coalescing is based on generation, not wall-clock timestamps.");
	expectContains(contract, "Session/revision fencing remains PRS-004");
	expectContains(contract, "Slice C — bounded mutation coverage");
	expectContains(contract, "bounded PRS-002D evidence");
	expectContains(contract, "bounded PRS-002H behavior");
	expectContains(contract, "bounded PRS-002I observability");
	expectContains(contract, "time() - player_checkpoint_oldest_dirty_timestamp_seconds");
}
