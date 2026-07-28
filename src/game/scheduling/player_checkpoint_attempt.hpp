#pragma once

#include "game/scheduling/player_persistence_state.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <atomic>
	#include <exception>
	#include <functional>
	#include <utility>
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
 * Releases one previously acquired admission slot on every scope exit. Call
 * release() early before scheduling a success follow-up so a capacity of one
 * cannot reject its own next generation.
 */
class PlayerCheckpointQueueSlot final {
public:
	explicit PlayerCheckpointQueueSlot(PlayerCheckpointQueueAdmission &admission) noexcept :
		admission_(&admission) { }

	PlayerCheckpointQueueSlot(const PlayerCheckpointQueueSlot &) = delete;
	PlayerCheckpointQueueSlot &operator=(const PlayerCheckpointQueueSlot &) = delete;

	~PlayerCheckpointQueueSlot() {
		(void)release();
	}

	[[nodiscard]] bool release() noexcept {
		auto* admission = std::exchange(admission_, nullptr);
		return admission != nullptr && admission->release();
	}

private:
	PlayerCheckpointQueueAdmission* admission_;
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
