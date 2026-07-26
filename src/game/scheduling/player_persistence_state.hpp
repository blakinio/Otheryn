#pragma once

#include <algorithm>
#include <cstdint>
#include <limits>
#include <optional>

/**
 * Tracks the persistence generation owned by one live Player object.
 *
 * This state object is intentionally independent from databases, schedulers and
 * wall-clock time. Callers mark persistence-relevant mutations, capture one
 * generation for an in-flight checkpoint, and acknowledge only that exact
 * generation when the save result is known.
 */
class PlayerPersistenceState final {
public:
	using Generation = uint64_t;

	[[nodiscard]] Generation markDirty() noexcept {
		if (dirtyGeneration_ < std::numeric_limits<Generation>::max()) {
			++dirtyGeneration_;
		}
		return dirtyGeneration_;
	}

	[[nodiscard]] bool isDirty() const noexcept {
		return dirtyGeneration_ > acknowledgedGeneration_;
	}

	[[nodiscard]] bool hasCheckpointInFlight() const noexcept {
		return inFlightGeneration_.has_value();
	}

	[[nodiscard]] bool canBeginCheckpoint(uint32_t maxConsecutiveFailures = std::numeric_limits<uint32_t>::max()) const noexcept {
		return isDirty()
			&& !hasCheckpointInFlight()
			&& consecutiveFailures_ < maxConsecutiveFailures;
	}

	[[nodiscard]] std::optional<Generation> beginCheckpoint(uint32_t maxConsecutiveFailures = std::numeric_limits<uint32_t>::max()) noexcept {
		if (!canBeginCheckpoint(maxConsecutiveFailures)) {
			return std::nullopt;
		}

		inFlightGeneration_ = dirtyGeneration_;
		return inFlightGeneration_;
	}

	[[nodiscard]] bool acknowledgeSuccess(Generation generation) noexcept {
		if (!matchesInFlight(generation)) {
			return false;
		}

		acknowledgedGeneration_ = std::max(acknowledgedGeneration_, generation);
		inFlightGeneration_.reset();
		consecutiveFailures_ = 0;
		return true;
	}

	[[nodiscard]] bool acknowledgeFailure(Generation generation) noexcept {
		if (!matchesInFlight(generation)) {
			return false;
		}

		inFlightGeneration_.reset();
		if (consecutiveFailures_ < std::numeric_limits<uint32_t>::max()) {
			++consecutiveFailures_;
		}
		return true;
	}

	[[nodiscard]] Generation dirtyGeneration() const noexcept {
		return dirtyGeneration_;
	}

	[[nodiscard]] Generation acknowledgedGeneration() const noexcept {
		return acknowledgedGeneration_;
	}

	[[nodiscard]] std::optional<Generation> inFlightGeneration() const noexcept {
		return inFlightGeneration_;
	}

	[[nodiscard]] uint32_t consecutiveFailures() const noexcept {
		return consecutiveFailures_;
	}

private:
	[[nodiscard]] bool matchesInFlight(Generation generation) const noexcept {
		return inFlightGeneration_.has_value() && *inFlightGeneration_ == generation;
	}

	Generation dirtyGeneration_ = 0;
	Generation acknowledgedGeneration_ = 0;
	std::optional<Generation> inFlightGeneration_;
	uint32_t consecutiveFailures_ = 0;
};
