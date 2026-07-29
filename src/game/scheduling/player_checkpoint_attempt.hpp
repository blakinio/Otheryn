#pragma once

#include "game/scheduling/player_persistence_state.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <atomic>
	#include <cstdint>
	#include <exception>
	#include <functional>
	#include <memory>
	#include <utility>
	#include <vector>
#endif

inline constexpr uint32_t DEFAULT_PLAYER_CHECKPOINT_QUEUE_CAPACITY = 1024;

enum class PlayerCheckpointQueueAdmissionOutcome : uint8_t {
	admitted,
	queueFull,
};

struct PlayerCheckpointQueueAdmissionResult final {
	PlayerCheckpointQueueAdmissionOutcome outcome;
	bool checkpointReleased = false;
};

/**
 * Bounds the number of player checkpoint tasks admitted to the shared worker
 * pool. The counter includes queued and running checkpoint work, but owns no
 * thread, timer, retry policy, Player object or persistence behavior.
 */
class PlayerCheckpointQueueAdmission final {
public:
	explicit PlayerCheckpointQueueAdmission(uint32_t capacity = DEFAULT_PLAYER_CHECKPOINT_QUEUE_CAPACITY) noexcept :
		capacity_(capacity == 0 ? 1 : capacity) { }

	[[nodiscard]] bool tryAcquire() noexcept {
		auto outstanding = outstanding_.load(std::memory_order_relaxed);
		while (outstanding < capacity_) {
			if (outstanding_.compare_exchange_weak(outstanding, outstanding + 1, std::memory_order_acq_rel, std::memory_order_relaxed)) {
				return true;
			}
		}
		return false;
	}

	[[nodiscard]] bool release() noexcept {
		auto outstanding = outstanding_.load(std::memory_order_relaxed);
		while (outstanding > 0) {
			if (outstanding_.compare_exchange_weak(outstanding, outstanding - 1, std::memory_order_acq_rel, std::memory_order_relaxed)) {
				return true;
			}
		}
		return false;
	}

	[[nodiscard]] uint32_t capacity() const noexcept {
		return capacity_;
	}

	[[nodiscard]] uint32_t outstanding() const noexcept {
		return outstanding_.load(std::memory_order_acquire);
	}

private:
	const uint32_t capacity_;
	std::atomic<uint32_t> outstanding_ = 0;
};

/**
 * Releases one previously acquired admission slot on every scope exit. The
 * optional observer is best-effort operational telemetry and is never allowed
 * to turn a successful queue release into a persistence failure.
 */
class PlayerCheckpointQueueSlot final {
public:
	explicit PlayerCheckpointQueueSlot(PlayerCheckpointQueueAdmission &admission, std::function<void()> releaseObserver = {}) noexcept :
		admission_(&admission), releaseObserver_(std::move(releaseObserver)) { }

	PlayerCheckpointQueueSlot(const PlayerCheckpointQueueSlot &) = delete;
	PlayerCheckpointQueueSlot &operator=(const PlayerCheckpointQueueSlot &) = delete;

	~PlayerCheckpointQueueSlot() {
		(void)release();
	}

	[[nodiscard]] bool release() noexcept {
		auto* admission = std::exchange(admission_, nullptr);
		if (admission == nullptr || !admission->release()) {
			return false;
		}

		if (releaseObserver_) {
			try {
				releaseObserver_();
			} catch (...) {
				// Metrics must never alter checkpoint ownership or queue release.
			}
			releaseObserver_ = {};
		}
		return true;
	}

private:
	PlayerCheckpointQueueAdmission* admission_;
	std::function<void()> releaseObserver_;
};

[[nodiscard]] inline PlayerCheckpointQueueAdmissionResult tryAdmitPlayerCheckpoint(
	PlayerCheckpointQueueAdmission &admission,
	PlayerPersistenceState &state,
	PlayerPersistenceState::Generation generation
) noexcept {
	if (admission.tryAcquire()) {
		return {
			PlayerCheckpointQueueAdmissionOutcome::admitted,
			false,
		};
	}

	return {
		PlayerCheckpointQueueAdmissionOutcome::queueFull,
		state.abandonCheckpoint(generation),
	};
}

struct PlayerCheckpointGaugeSnapshot final {
	uint32_t queueCapacity = 0;
	uint32_t queueOutstanding = 0;
	uint64_t dirtyOwners = 0;
	int64_t oldestDirtyTimestampSeconds = 0;
};

[[nodiscard]] inline PlayerCheckpointGaugeSnapshot summarizePlayerCheckpointGauges(
	uint32_t queueCapacity,
	uint32_t queueOutstanding,
	const std::vector<std::shared_ptr<PlayerPersistenceState>> &states
) {
	PlayerCheckpointGaugeSnapshot snapshot {
		queueCapacity,
		queueOutstanding,
		0,
		0,
	};

	for (const auto &state : states) {
		if (!state || !state->isDirty()) {
			continue;
		}

		++snapshot.dirtyOwners;
		const auto timestamp = state->dirtySinceTimestampSeconds();
		if (timestamp.has_value() && (snapshot.oldestDirtyTimestampSeconds == 0 || *timestamp < snapshot.oldestDirtyTimestampSeconds)) {
			snapshot.oldestDirtyTimestampSeconds = *timestamp;
		}
	}
	return snapshot;
}

struct PlayerCheckpointTelemetrySnapshot final {
	uint64_t requests = 0;
	uint64_t attempts = 0;
	uint64_t successes = 0;
	uint64_t failures = 0;
	uint64_t thrownAttempts = 0;
	uint64_t queueRejections = 0;
	uint64_t submissionFailures = 0;
};

class PlayerCheckpointTelemetry final {
public:
	void recordRequest() noexcept {
		requests_.fetch_add(1, std::memory_order_relaxed);
	}

	void recordAttempt() noexcept {
		attempts_.fetch_add(1, std::memory_order_relaxed);
	}

	void recordSuccess() noexcept {
		successes_.fetch_add(1, std::memory_order_relaxed);
	}

	void recordFailure() noexcept {
		failures_.fetch_add(1, std::memory_order_relaxed);
	}

	void recordThrownAttempt() noexcept {
		failures_.fetch_add(1, std::memory_order_relaxed);
		thrownAttempts_.fetch_add(1, std::memory_order_relaxed);
	}

	void recordQueueRejection() noexcept {
		queueRejections_.fetch_add(1, std::memory_order_relaxed);
	}

	void recordSubmissionFailure() noexcept {
		submissionFailures_.fetch_add(1, std::memory_order_relaxed);
	}

	[[nodiscard]] PlayerCheckpointTelemetrySnapshot snapshot() const noexcept {
		return {
			requests_.load(std::memory_order_relaxed),
			attempts_.load(std::memory_order_relaxed),
			successes_.load(std::memory_order_relaxed),
			failures_.load(std::memory_order_relaxed),
			thrownAttempts_.load(std::memory_order_relaxed),
			queueRejections_.load(std::memory_order_relaxed),
			submissionFailures_.load(std::memory_order_relaxed),
		};
	}

private:
	std::atomic<uint64_t> requests_ = 0;
	std::atomic<uint64_t> attempts_ = 0;
	std::atomic<uint64_t> successes_ = 0;
	std::atomic<uint64_t> failures_ = 0;
	std::atomic<uint64_t> thrownAttempts_ = 0;
	std::atomic<uint64_t> queueRejections_ = 0;
	std::atomic<uint64_t> submissionFailures_ = 0;
};

enum class PlayerCheckpointAttemptOutcome : uint8_t {
	saved,
	saveFailed,
	saveThrew,
};

struct PlayerCheckpointAttemptResult final {
	PlayerCheckpointAttemptOutcome outcome;
	bool acknowledgementAccepted = false;
	bool followUpRequired = false;
	std::exception_ptr exception;
};

/**
 * Executes one captured player checkpoint generation against an injected save
 * attempt and records the exact success/failure acknowledgement decision.
 *
 * The helper owns no queue, timer, Player object or database behavior. It is a
 * deterministic boundary used by SaveManager so controlled failure tests can
 * prove acknowledgement and follow-up semantics without failing a real store.
 */
template <typename SaveAttempt>
[[nodiscard]] PlayerCheckpointAttemptResult executePlayerCheckpointAttempt(
	PlayerPersistenceState &state,
	PlayerPersistenceState::Generation generation,
	SaveAttempt &&saveAttempt
) {
	bool saveSuccess = false;
	try {
		saveSuccess = std::invoke(std::forward<SaveAttempt>(saveAttempt));
	} catch (...) {
		return {
			PlayerCheckpointAttemptOutcome::saveThrew,
			state.acknowledgeFailure(generation),
			false,
			std::current_exception(),
		};
	}

	if (!saveSuccess) {
		return {
			PlayerCheckpointAttemptOutcome::saveFailed,
			state.acknowledgeFailure(generation),
			false,
			{},
		};
	}

	const bool acknowledged = state.acknowledgeSuccess(generation);
	return {
		PlayerCheckpointAttemptOutcome::saved,
		acknowledged,
		acknowledged && state.isDirty(),
		{},
	};
}
