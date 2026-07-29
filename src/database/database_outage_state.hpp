#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <cstdint>
	#include <limits>
	#include <mutex>
	#include <optional>
	#include <stdexcept>
#endif

using DatabaseOutageTimePoint = std::chrono::milliseconds;
using DatabaseOutageEventSequence = uint64_t;

enum class DatabaseOutageState : uint8_t {
	Healthy,
	Degraded,
	Draining,
	Maintenance,
};

enum class DatabaseOutageFailureReason : uint8_t {
	ConnectionLost,
	ServerGone,
	TransactionBeginFailed,
	TransactionCommitFailed,
	QueryFailed,
	RecoveryProbeFailed,
};

enum class DatabaseOutageCommitOutcome : uint8_t {
	KnownNotCommitted,
	Unknown,
};

enum class DatabaseOutageEventReason : uint8_t {
	Initial,
	FirstRuntimeFailure,
	UnknownCommitOutcome,
	RepeatedRuntimeFailure,
	RuntimeFailureWhileUnavailable,
	DegradedDeadlineExpired,
	DrainCompleted,
	DrainDeadlineExpired,
	RecoveryEvidenceAccepted,
	OperatorMaintenance,
	OperatorResume,
	StaleOrDuplicateEvent,
};

enum class DatabaseOutageEventDisposition : uint8_t {
	Applied,
	AcceptedNoStateChange,
	RejectedStaleOrDuplicate,
	RejectedState,
	RejectedPrecondition,
};

struct DatabaseOutageSnapshot final {
	DatabaseOutageState state = DatabaseOutageState::Healthy;
	DatabaseOutageEventReason lastTransitionReason = DatabaseOutageEventReason::Initial;
	uint64_t transitionCount = 0;
	std::optional<DatabaseOutageTimePoint> firstFailureTime;
	std::optional<DatabaseOutageTimePoint> degradedDeadline;
	std::optional<DatabaseOutageTimePoint> drainDeadline;
	std::optional<DatabaseOutageFailureReason> lastFailureReason;
	std::optional<DatabaseOutageCommitOutcome> lastFailureOutcome;
	bool recoveryEvidenceAccepted = false;
	DatabaseOutageEventSequence lastEventSequence = 0;
	std::optional<DatabaseOutageTimePoint> lastEventTime;
};

struct DatabaseOutageEventResult final {
	DatabaseOutageEventDisposition disposition = DatabaseOutageEventDisposition::RejectedState;
	DatabaseOutageEventReason reason = DatabaseOutageEventReason::Initial;
	DatabaseOutageEventSequence eventSequence = 0;
	DatabaseOutageTimePoint eventTime { 0 };
	DatabaseOutageSnapshot before;
	DatabaseOutageSnapshot after;

	[[nodiscard]] bool stateChanged() const noexcept {
		return before.state != after.state;
	}
};

/**
 * Owns only database-outage policy state.
 *
 * The object is intentionally independent from Database, DatabaseTasks,
 * protocols, gameplay, clocks, schedulers and metrics. Callers supply one
 * monotonic event sequence and one deterministic monotonic time value for every
 * event. All methods are internally serialized.
 */
class DatabaseOutageStateMachine final {
public:
	struct Durations final {
		DatabaseOutageTimePoint degradedGrace;
		DatabaseOutageTimePoint drain;
	};

	explicit DatabaseOutageStateMachine(Durations durations) :
		durations_(durations) {
		if (durations_.degradedGrace.count() <= 0 || durations_.drain.count() <= 0) {
			throw std::invalid_argument("database outage durations must be positive");
		}
	}

	DatabaseOutageStateMachine(const DatabaseOutageStateMachine &) = delete;
	DatabaseOutageStateMachine &operator=(const DatabaseOutageStateMachine &) = delete;

	[[nodiscard]] DatabaseOutageSnapshot snapshot() const {
		std::lock_guard lock(mutex_);
		return snapshotLocked();
	}

	[[nodiscard]] DatabaseOutageEventResult runtimeFailure(
		DatabaseOutageEventSequence eventSequence,
		DatabaseOutageFailureReason failureReason,
		DatabaseOutageCommitOutcome outcome,
		DatabaseOutageTimePoint now
	) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (!beginEventLocked(eventSequence, now)) {
			return makeResultLocked(
				DatabaseOutageEventDisposition::RejectedStaleOrDuplicate,
				DatabaseOutageEventReason::StaleOrDuplicateEvent,
				eventSequence,
				now,
				before
			);
		}

		lastFailureReason_ = failureReason;
		lastFailureOutcome_ = outcome;
		recoveryEvidenceAccepted_ = false;

		if (state_ == DatabaseOutageState::Healthy) {
			firstFailureTime_ = now;
			if (outcome == DatabaseOutageCommitOutcome::Unknown) {
				degradedDeadline_.reset();
				enterDrainingLocked(now, DatabaseOutageEventReason::UnknownCommitOutcome);
				return makeResultLocked(DatabaseOutageEventDisposition::Applied, DatabaseOutageEventReason::UnknownCommitOutcome, eventSequence, now, before);
			}

			degradedDeadline_ = addDuration(now, durations_.degradedGrace);
			drainDeadline_.reset();
			transitionLocked(DatabaseOutageState::Degraded, DatabaseOutageEventReason::FirstRuntimeFailure);
			return makeResultLocked(DatabaseOutageEventDisposition::Applied, DatabaseOutageEventReason::FirstRuntimeFailure, eventSequence, now, before);
		}

		if (state_ == DatabaseOutageState::Degraded) {
			const auto reason = outcome == DatabaseOutageCommitOutcome::Unknown
				? DatabaseOutageEventReason::UnknownCommitOutcome
				: DatabaseOutageEventReason::RepeatedRuntimeFailure;
			enterDrainingLocked(now, reason);
			return makeResultLocked(DatabaseOutageEventDisposition::Applied, reason, eventSequence, now, before);
		}

		return makeResultLocked(
			DatabaseOutageEventDisposition::AcceptedNoStateChange,
			DatabaseOutageEventReason::RuntimeFailureWhileUnavailable,
			eventSequence,
			now,
			before
		);
	}

	[[nodiscard]] DatabaseOutageEventResult degradedDeadlineExpired(DatabaseOutageEventSequence eventSequence, DatabaseOutageTimePoint now) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (!beginEventLocked(eventSequence, now)) {
			return staleResultLocked(eventSequence, now, before);
		}
		if (state_ != DatabaseOutageState::Degraded) {
			return makeResultLocked(DatabaseOutageEventDisposition::RejectedState, DatabaseOutageEventReason::DegradedDeadlineExpired, eventSequence, now, before);
		}
		if (!degradedDeadline_.has_value() || now < *degradedDeadline_) {
			return makeResultLocked(DatabaseOutageEventDisposition::RejectedPrecondition, DatabaseOutageEventReason::DegradedDeadlineExpired, eventSequence, now, before);
		}

		enterDrainingLocked(now, DatabaseOutageEventReason::DegradedDeadlineExpired);
		return makeResultLocked(DatabaseOutageEventDisposition::Applied, DatabaseOutageEventReason::DegradedDeadlineExpired, eventSequence, now, before);
	}

	[[nodiscard]] DatabaseOutageEventResult drainCompleted(DatabaseOutageEventSequence eventSequence, DatabaseOutageTimePoint now) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (!beginEventLocked(eventSequence, now)) {
			return staleResultLocked(eventSequence, now, before);
		}
		if (state_ != DatabaseOutageState::Draining) {
			return makeResultLocked(DatabaseOutageEventDisposition::RejectedState, DatabaseOutageEventReason::DrainCompleted, eventSequence, now, before);
		}

		recoveryEvidenceAccepted_ = false;
		transitionLocked(DatabaseOutageState::Maintenance, DatabaseOutageEventReason::DrainCompleted);
		return makeResultLocked(DatabaseOutageEventDisposition::Applied, DatabaseOutageEventReason::DrainCompleted, eventSequence, now, before);
	}

	[[nodiscard]] DatabaseOutageEventResult drainDeadlineExpired(DatabaseOutageEventSequence eventSequence, DatabaseOutageTimePoint now) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (!beginEventLocked(eventSequence, now)) {
			return staleResultLocked(eventSequence, now, before);
		}
		if (state_ != DatabaseOutageState::Draining) {
			return makeResultLocked(DatabaseOutageEventDisposition::RejectedState, DatabaseOutageEventReason::DrainDeadlineExpired, eventSequence, now, before);
		}
		if (!drainDeadline_.has_value() || now < *drainDeadline_) {
			return makeResultLocked(DatabaseOutageEventDisposition::RejectedPrecondition, DatabaseOutageEventReason::DrainDeadlineExpired, eventSequence, now, before);
		}

		recoveryEvidenceAccepted_ = false;
		transitionLocked(DatabaseOutageState::Maintenance, DatabaseOutageEventReason::DrainDeadlineExpired);
		return makeResultLocked(DatabaseOutageEventDisposition::Applied, DatabaseOutageEventReason::DrainDeadlineExpired, eventSequence, now, before);
	}

	[[nodiscard]] DatabaseOutageEventResult recoveryEvidenceAccepted(DatabaseOutageEventSequence eventSequence, DatabaseOutageTimePoint now) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (!beginEventLocked(eventSequence, now)) {
			return staleResultLocked(eventSequence, now, before);
		}
		if (state_ != DatabaseOutageState::Degraded && state_ != DatabaseOutageState::Maintenance) {
			return makeResultLocked(DatabaseOutageEventDisposition::RejectedState, DatabaseOutageEventReason::RecoveryEvidenceAccepted, eventSequence, now, before);
		}

		recoveryEvidenceAccepted_ = true;
		return makeResultLocked(DatabaseOutageEventDisposition::AcceptedNoStateChange, DatabaseOutageEventReason::RecoveryEvidenceAccepted, eventSequence, now, before);
	}

	[[nodiscard]] DatabaseOutageEventResult operatorEnterMaintenance(DatabaseOutageEventSequence eventSequence, DatabaseOutageTimePoint now) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (!beginEventLocked(eventSequence, now)) {
			return staleResultLocked(eventSequence, now, before);
		}
		if (state_ == DatabaseOutageState::Maintenance) {
			return makeResultLocked(DatabaseOutageEventDisposition::RejectedState, DatabaseOutageEventReason::OperatorMaintenance, eventSequence, now, before);
		}

		recoveryEvidenceAccepted_ = false;
		transitionLocked(DatabaseOutageState::Maintenance, DatabaseOutageEventReason::OperatorMaintenance);
		return makeResultLocked(DatabaseOutageEventDisposition::Applied, DatabaseOutageEventReason::OperatorMaintenance, eventSequence, now, before);
	}

	[[nodiscard]] DatabaseOutageEventResult operatorResume(DatabaseOutageEventSequence eventSequence, DatabaseOutageTimePoint now) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (!beginEventLocked(eventSequence, now)) {
			return staleResultLocked(eventSequence, now, before);
		}
		if (state_ != DatabaseOutageState::Degraded && state_ != DatabaseOutageState::Maintenance) {
			return makeResultLocked(DatabaseOutageEventDisposition::RejectedState, DatabaseOutageEventReason::OperatorResume, eventSequence, now, before);
		}
		if (!recoveryEvidenceAccepted_) {
			return makeResultLocked(DatabaseOutageEventDisposition::RejectedPrecondition, DatabaseOutageEventReason::OperatorResume, eventSequence, now, before);
		}

		transitionLocked(DatabaseOutageState::Healthy, DatabaseOutageEventReason::OperatorResume);
		const auto emittedAfter = snapshotLocked();
		clearActiveFailureIntervalLocked();
		return DatabaseOutageEventResult {
			.disposition = DatabaseOutageEventDisposition::Applied,
			.reason = DatabaseOutageEventReason::OperatorResume,
			.eventSequence = eventSequence,
			.eventTime = now,
			.before = before,
			.after = emittedAfter,
		};
	}

private:
	[[nodiscard]] static DatabaseOutageTimePoint addDuration(DatabaseOutageTimePoint now, DatabaseOutageTimePoint duration) noexcept {
		const auto maximum = DatabaseOutageTimePoint::max().count();
		if (now.count() > maximum - duration.count()) {
			return DatabaseOutageTimePoint::max();
		}
		return now + duration;
	}

	[[nodiscard]] bool beginEventLocked(DatabaseOutageEventSequence eventSequence, DatabaseOutageTimePoint now) noexcept {
		if (eventSequence == 0 || eventSequence <= lastEventSequence_) {
			return false;
		}
		if (lastEventTime_.has_value() && now < *lastEventTime_) {
			return false;
		}

		lastEventSequence_ = eventSequence;
		lastEventTime_ = now;
		return true;
	}

	void transitionLocked(DatabaseOutageState nextState, DatabaseOutageEventReason reason) noexcept {
		state_ = nextState;
		lastTransitionReason_ = reason;
		if (transitionCount_ < std::numeric_limits<uint64_t>::max()) {
			++transitionCount_;
		}
	}

	void enterDrainingLocked(DatabaseOutageTimePoint now, DatabaseOutageEventReason reason) noexcept {
		recoveryEvidenceAccepted_ = false;
		drainDeadline_ = addDuration(now, durations_.drain);
		transitionLocked(DatabaseOutageState::Draining, reason);
	}

	void clearActiveFailureIntervalLocked() noexcept {
		firstFailureTime_.reset();
		degradedDeadline_.reset();
		drainDeadline_.reset();
		lastFailureReason_.reset();
		lastFailureOutcome_.reset();
		recoveryEvidenceAccepted_ = false;
	}

	[[nodiscard]] DatabaseOutageSnapshot snapshotLocked() const {
		return DatabaseOutageSnapshot {
			.state = state_,
			.lastTransitionReason = lastTransitionReason_,
			.transitionCount = transitionCount_,
			.firstFailureTime = firstFailureTime_,
			.degradedDeadline = degradedDeadline_,
			.drainDeadline = drainDeadline_,
			.lastFailureReason = lastFailureReason_,
			.lastFailureOutcome = lastFailureOutcome_,
			.recoveryEvidenceAccepted = recoveryEvidenceAccepted_,
			.lastEventSequence = lastEventSequence_,
			.lastEventTime = lastEventTime_,
		};
	}

	[[nodiscard]] DatabaseOutageEventResult staleResultLocked(
		DatabaseOutageEventSequence eventSequence,
		DatabaseOutageTimePoint now,
		const DatabaseOutageSnapshot &before
	) const {
		return makeResultLocked(
			DatabaseOutageEventDisposition::RejectedStaleOrDuplicate,
			DatabaseOutageEventReason::StaleOrDuplicateEvent,
			eventSequence,
			now,
			before
		);
	}

	[[nodiscard]] DatabaseOutageEventResult makeResultLocked(
		DatabaseOutageEventDisposition disposition,
		DatabaseOutageEventReason reason,
		DatabaseOutageEventSequence eventSequence,
		DatabaseOutageTimePoint now,
		const DatabaseOutageSnapshot &before
	) const {
		return DatabaseOutageEventResult {
			.disposition = disposition,
			.reason = reason,
			.eventSequence = eventSequence,
			.eventTime = now,
			.before = before,
			.after = snapshotLocked(),
		};
	}

	const Durations durations_;
	mutable std::mutex mutex_;
	DatabaseOutageState state_ = DatabaseOutageState::Healthy;
	DatabaseOutageEventReason lastTransitionReason_ = DatabaseOutageEventReason::Initial;
	uint64_t transitionCount_ = 0;
	std::optional<DatabaseOutageTimePoint> firstFailureTime_;
	std::optional<DatabaseOutageTimePoint> degradedDeadline_;
	std::optional<DatabaseOutageTimePoint> drainDeadline_;
	std::optional<DatabaseOutageFailureReason> lastFailureReason_;
	std::optional<DatabaseOutageCommitOutcome> lastFailureOutcome_;
	bool recoveryEvidenceAccepted_ = false;
	DatabaseOutageEventSequence lastEventSequence_ = 0;
	std::optional<DatabaseOutageTimePoint> lastEventTime_;
};
