#pragma once

#include "database/database_outage_state.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstddef>
	#include <cstdint>
	#include <optional>
	#include <utility>
	#include <vector>
#endif

enum class DatabaseOutageDrainAction : uint8_t {
	None,
	AttemptPlayer,
	CompleteDrain,
	ExpireDrain,
	CleanupComplete,
	FailClosedMaintenance,
};

struct DatabaseOutageDrainDecision final {
	DatabaseOutageDrainAction action = DatabaseOutageDrainAction::None;
	std::optional<uint32_t> playerId;
};

struct DatabaseOutageDrainPlayerAttemptResult final {
	bool playerFound = false;
	bool removed = false;
	bool finalSaveSucceeded = false;
};

struct DatabaseOutageDrainSummary final {
	uint64_t transitionCount = 0;
	size_t capturedPlayers = 0;
	size_t attemptLimit = 0;
	size_t attempts = 0;
	size_t missingPlayers = 0;
	size_t removalFailures = 0;
	size_t finalSaveFailures = 0;
	bool deadlineExpired = false;
};

class DatabaseOutageDrainOrchestrator final {
public:
	[[nodiscard]] bool begin(const DatabaseOutageSnapshot &snapshot, std::vector<uint32_t> playerIds) {
		reset();
		if (snapshot.state != DatabaseOutageState::Draining || !snapshot.drainDeadline.has_value()) {
			failClosed_ = true;
			return false;
		}

		transitionCount_ = snapshot.transitionCount;
		deadline_ = *snapshot.drainDeadline;
		playerIds_ = std::move(playerIds);
		attemptLimit_ = playerIds_.size();
		active_ = true;
		return true;
	}

	void reset() noexcept {
		playerIds_.clear();
		transitionCount_ = 0;
		deadline_ = DatabaseOutageTimePoint { 0 };
		cursor_ = 0;
		attemptLimit_ = 0;
		missingPlayers_ = 0;
		removalFailures_ = 0;
		finalSaveFailures_ = 0;
		active_ = false;
		maintenanceCleanup_ = false;
		deadlineExpired_ = false;
		failClosed_ = false;
	}

	[[nodiscard]] bool matches(const DatabaseOutageSnapshot &snapshot) const noexcept {
		return active_ && transitionCount_ == snapshot.transitionCount;
	}

	[[nodiscard]] bool hasPendingCleanup() const noexcept {
		return active_ && maintenanceCleanup_ && cursor_ < attemptLimit_;
	}

	[[nodiscard]] DatabaseOutageDrainDecision next(const DatabaseOutageSnapshot &snapshot, DatabaseOutageTimePoint now) noexcept {
		if (failClosed_) {
			return { .action = DatabaseOutageDrainAction::FailClosedMaintenance };
		}
		if (!active_) {
			return {};
		}

		if (maintenanceCleanup_) {
			if (cursor_ >= attemptLimit_) {
				active_ = false;
				return { .action = DatabaseOutageDrainAction::CleanupComplete };
			}
			return {
				.action = DatabaseOutageDrainAction::AttemptPlayer,
				.playerId = playerIds_[cursor_],
			};
		}

		if (snapshot.state != DatabaseOutageState::Draining || snapshot.transitionCount != transitionCount_ || !snapshot.drainDeadline.has_value()) {
			failClosed_ = true;
			return { .action = DatabaseOutageDrainAction::FailClosedMaintenance };
		}

		if (now >= deadline_) {
			maintenanceCleanup_ = true;
			deadlineExpired_ = true;
			return { .action = DatabaseOutageDrainAction::ExpireDrain };
		}
		if (cursor_ >= attemptLimit_) {
			active_ = false;
			return { .action = DatabaseOutageDrainAction::CompleteDrain };
		}

		return {
			.action = DatabaseOutageDrainAction::AttemptPlayer,
			.playerId = playerIds_[cursor_],
		};
	}

	void recordAttempt(const DatabaseOutageDrainPlayerAttemptResult &result) noexcept {
		if (!active_ || cursor_ >= attemptLimit_) {
			return;
		}

		++cursor_;
		if (!result.playerFound) {
			++missingPlayers_;
			return;
		}
		if (!result.removed) {
			++removalFailures_;
		}
		if (!result.finalSaveSucceeded) {
			++finalSaveFailures_;
		}
	}

	[[nodiscard]] bool attemptsExhausted() const noexcept {
		return cursor_ >= attemptLimit_;
	}

	[[nodiscard]] DatabaseOutageDrainSummary summary() const noexcept {
		return {
			.transitionCount = transitionCount_,
			.capturedPlayers = playerIds_.size(),
			.attemptLimit = attemptLimit_,
			.attempts = cursor_,
			.missingPlayers = missingPlayers_,
			.removalFailures = removalFailures_,
			.finalSaveFailures = finalSaveFailures_,
			.deadlineExpired = deadlineExpired_,
		};
	}

private:
	std::vector<uint32_t> playerIds_;
	uint64_t transitionCount_ = 0;
	DatabaseOutageTimePoint deadline_ { 0 };
	size_t cursor_ = 0;
	size_t attemptLimit_ = 0;
	size_t missingPlayers_ = 0;
	size_t removalFailures_ = 0;
	size_t finalSaveFailures_ = 0;
	bool active_ = false;
	bool maintenanceCleanup_ = false;
	bool deadlineExpired_ = false;
	bool failClosed_ = false;
};
