#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <chrono>
	#include <condition_variable>
	#include <cstdint>
	#include <limits>
	#include <mutex>
	#include <optional>
#endif

/**
 * Tracks the persistence generation owned by one live Player object.
 *
 * This state object is intentionally independent from databases, schedulers and
 * wall-clock acquisition. Callers may supply a Unix timestamp for one continuous
 * dirty interval, while generation acknowledgement remains entirely
 * deterministic and independent from a clock source.
 *
 * All operations are internally synchronized so a game-thread save request may
 * safely race with save-worker acknowledgement.
 */
class PlayerPersistenceState final {
public:
	using Generation = uint64_t;

	Generation markDirty(std::optional<int64_t> dirtyTimestampSeconds = std::nullopt) {
		std::lock_guard lock(mutex_);
		if (dirtyGeneration_ < std::numeric_limits<Generation>::max()) {
			++dirtyGeneration_;
		}
		if (isDirtyLocked() && !dirtySinceTimestampSeconds_.has_value() && dirtyTimestampSeconds.has_value()) {
			dirtySinceTimestampSeconds_ = dirtyTimestampSeconds;
		}
		return dirtyGeneration_;
	}

	[[nodiscard]] bool isDirty() const {
		std::lock_guard lock(mutex_);
		return isDirtyLocked();
	}

	[[nodiscard]] bool hasCheckpointInFlight() const {
		std::lock_guard lock(mutex_);
		return inFlightGeneration_.has_value();
	}

	[[nodiscard]] bool canBeginCheckpoint(uint32_t maxConsecutiveFailures = std::numeric_limits<uint32_t>::max()) const {
		std::lock_guard lock(mutex_);
		return canBeginCheckpointLocked(maxConsecutiveFailures);
	}

	[[nodiscard]] std::optional<Generation> beginCheckpoint(uint32_t maxConsecutiveFailures = std::numeric_limits<uint32_t>::max()) {
		std::lock_guard lock(mutex_);
		if (!canBeginCheckpointLocked(maxConsecutiveFailures)) {
			return std::nullopt;
		}

		inFlightGeneration_ = dirtyGeneration_;
		return inFlightGeneration_;
	}

	/**
	 * Waits a finite interval for an older checkpoint owner to settle and then
	 * atomically claims the newest dirty generation for a synchronous final save.
	 *
	 * A timeout never steals, releases or acknowledges the existing owner. The
	 * caller must mark the final state dirty before invoking this operation.
	 */
	[[nodiscard]] std::optional<Generation> beginFinalCheckpoint(std::chrono::milliseconds waitTimeout) {
		std::unique_lock lock(mutex_);
		if (!checkpointSettled_.wait_for(lock, waitTimeout, [this] {
			    return !inFlightGeneration_.has_value();
		    })) {
			return std::nullopt;
		}
		if (!isDirtyLocked()) {
			return std::nullopt;
		}

		inFlightGeneration_ = dirtyGeneration_;
		return inFlightGeneration_;
	}

	bool abandonCheckpoint(Generation generation) {
		std::lock_guard lock(mutex_);
		if (!matchesInFlightLocked(generation)) {
			return false;
		}

		inFlightGeneration_.reset();
		checkpointSettled_.notify_all();
		return true;
	}

	bool acknowledgeSuccess(Generation generation) {
		std::lock_guard lock(mutex_);
		if (!matchesInFlightLocked(generation)) {
			return false;
		}

		acknowledgedGeneration_ = std::max(acknowledgedGeneration_, generation);
		inFlightGeneration_.reset();
		consecutiveFailures_ = 0;
		if (!isDirtyLocked()) {
			dirtySinceTimestampSeconds_.reset();
		}
		checkpointSettled_.notify_all();
		return true;
	}

	bool acknowledgeFailure(Generation generation) {
		std::lock_guard lock(mutex_);
		if (!matchesInFlightLocked(generation)) {
			return false;
		}

		inFlightGeneration_.reset();
		if (consecutiveFailures_ < std::numeric_limits<uint32_t>::max()) {
			++consecutiveFailures_;
		}
		checkpointSettled_.notify_all();
		return true;
	}

	[[nodiscard]] Generation dirtyGeneration() const {
		std::lock_guard lock(mutex_);
		return dirtyGeneration_;
	}

	[[nodiscard]] Generation acknowledgedGeneration() const {
		std::lock_guard lock(mutex_);
		return acknowledgedGeneration_;
	}

	[[nodiscard]] std::optional<Generation> inFlightGeneration() const {
		std::lock_guard lock(mutex_);
		return inFlightGeneration_;
	}

	[[nodiscard]] uint32_t consecutiveFailures() const {
		std::lock_guard lock(mutex_);
		return consecutiveFailures_;
	}

	[[nodiscard]] std::optional<int64_t> dirtySinceTimestampSeconds() const {
		std::lock_guard lock(mutex_);
		return dirtySinceTimestampSeconds_;
	}

private:
	[[nodiscard]] bool isDirtyLocked() const noexcept {
		return dirtyGeneration_ > acknowledgedGeneration_;
	}

	[[nodiscard]] bool canBeginCheckpointLocked(uint32_t maxConsecutiveFailures) const noexcept {
		return isDirtyLocked()
			&& !inFlightGeneration_.has_value()
			&& consecutiveFailures_ < maxConsecutiveFailures;
	}

	[[nodiscard]] bool matchesInFlightLocked(Generation generation) const noexcept {
		return inFlightGeneration_.has_value() && *inFlightGeneration_ == generation;
	}

	mutable std::mutex mutex_;
	std::condition_variable checkpointSettled_;
	Generation dirtyGeneration_ = 0;
	Generation acknowledgedGeneration_ = 0;
	std::optional<Generation> inFlightGeneration_;
	std::optional<int64_t> dirtySinceTimestampSeconds_;
	uint32_t consecutiveFailures_ = 0;
};
