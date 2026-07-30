#pragma once

#include "database/database_outage_state.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <limits>
	#include <mutex>
	#include <optional>
#endif

enum class DatabaseRuntimeOperation : uint8_t {
	Query,
	StoreQuery,
	TransactionBegin,
	TransactionCommit,
	TransactionRollback,
};

enum class DatabaseNativeErrorKind : uint8_t {
	None,
	ConnectionLost,
	ServerGone,
	Other,
};

enum class DatabaseRuntimeResultKind : uint8_t {
	Success,
	FailureKnownNotCommitted,
	FailureUnknownCommitOutcome,
};

struct DatabaseRuntimeResultClassification final {
	DatabaseRuntimeResultKind result = DatabaseRuntimeResultKind::Success;
	std::optional<DatabaseOutageFailureReason> failureReason;
	std::optional<DatabaseOutageCommitOutcome> commitOutcome;

	[[nodiscard]] constexpr bool succeeded() const noexcept {
		return result == DatabaseRuntimeResultKind::Success;
	}
};

[[nodiscard]] constexpr DatabaseRuntimeResultClassification classifyDatabaseRuntimeResult(
	DatabaseRuntimeOperation operation,
	bool succeeded,
	DatabaseNativeErrorKind nativeError
) noexcept {
	if (succeeded) {
		return {};
	}

	DatabaseOutageFailureReason failureReason = DatabaseOutageFailureReason::QueryFailed;
	if (operation == DatabaseRuntimeOperation::TransactionBegin) {
		failureReason = DatabaseOutageFailureReason::TransactionBeginFailed;
	} else if (operation == DatabaseRuntimeOperation::TransactionCommit) {
		failureReason = DatabaseOutageFailureReason::TransactionCommitFailed;
	} else if (nativeError == DatabaseNativeErrorKind::ConnectionLost) {
		failureReason = DatabaseOutageFailureReason::ConnectionLost;
	} else if (nativeError == DatabaseNativeErrorKind::ServerGone) {
		failureReason = DatabaseOutageFailureReason::ServerGone;
	}

	const bool connectionOutcomeUnknown = (nativeError == DatabaseNativeErrorKind::ConnectionLost || nativeError == DatabaseNativeErrorKind::ServerGone)
		&& (operation == DatabaseRuntimeOperation::Query || operation == DatabaseRuntimeOperation::StoreQuery);
	const bool commitOutcomeUnknown = operation == DatabaseRuntimeOperation::TransactionCommit
		|| operation == DatabaseRuntimeOperation::TransactionRollback
		|| connectionOutcomeUnknown;

	return DatabaseRuntimeResultClassification {
		.result = commitOutcomeUnknown
			? DatabaseRuntimeResultKind::FailureUnknownCommitOutcome
			: DatabaseRuntimeResultKind::FailureKnownNotCommitted,
		.failureReason = failureReason,
		.commitOutcome = commitOutcomeUnknown
			? DatabaseOutageCommitOutcome::Unknown
			: DatabaseOutageCommitOutcome::KnownNotCommitted,
	};
}

struct DatabaseRuntimeOutageEvent final {
	DatabaseOutageEventSequence sequence = 0;
	DatabaseOutageTimePoint time { 0 };
	DatabaseRuntimeResultClassification classification;
};

enum class DatabaseOutagePublicationDisposition : uint8_t {
	NotPublishedSuccess,
	Published,
};

struct DatabaseOutagePublicationResult final {
	DatabaseOutagePublicationDisposition disposition = DatabaseOutagePublicationDisposition::NotPublishedSuccess;
	std::optional<DatabaseOutageEventResult> event;
};

/**
 * Serializes runtime failures and bounded control events to one PRS-003 state owner.
 *
 * The publisher owns only event sequencing. It cannot reconnect, replay SQL,
 * retry an operation, schedule a deadline or change gameplay state. Generated
 * events clamp caller time to the owner's last accepted monotonic time. Explicit
 * runtime-failure events retain their supplied sequence and time so duplicate,
 * stale and regressing publication remains state-machine validated.
 */
class DatabaseOutageEventPublisher final {
public:
	explicit DatabaseOutageEventPublisher(DatabaseOutageStateMachine &stateOwner) noexcept :
		stateOwner_(stateOwner) { }

	DatabaseOutageEventPublisher(const DatabaseOutageEventPublisher &) = delete;
	DatabaseOutageEventPublisher &operator=(const DatabaseOutageEventPublisher &) = delete;

	[[nodiscard]] DatabaseOutagePublicationResult publish(
		const DatabaseRuntimeResultClassification &classification,
		DatabaseOutageTimePoint now
	) {
		std::lock_guard lock(mutex_);
		if (classification.succeeded()) {
			return {};
		}

		return publishLocked(nextSequenceLocked(), classification, clampTimeLocked(now));
	}

	[[nodiscard]] DatabaseOutagePublicationResult publish(const DatabaseRuntimeOutageEvent &event) {
		std::lock_guard lock(mutex_);
		if (event.classification.succeeded()) {
			return {};
		}

		advanceSequenceLocked(event.sequence);
		return publishLocked(event.sequence, event.classification, event.time);
	}

	[[nodiscard]] DatabaseOutageEventResult degradedDeadlineExpired(DatabaseOutageTimePoint now) {
		std::lock_guard lock(mutex_);
		return stateOwner_.degradedDeadlineExpired(nextSequenceLocked(), clampTimeLocked(now));
	}

	[[nodiscard]] DatabaseOutageEventResult drainCompleted(DatabaseOutageTimePoint now) {
		std::lock_guard lock(mutex_);
		return stateOwner_.drainCompleted(nextSequenceLocked(), clampTimeLocked(now));
	}

	[[nodiscard]] DatabaseOutageEventResult drainDeadlineExpired(DatabaseOutageTimePoint now) {
		std::lock_guard lock(mutex_);
		return stateOwner_.drainDeadlineExpired(nextSequenceLocked(), clampTimeLocked(now));
	}

	template <typename Result>
	[[nodiscard]] Result publishAndPreserve(
		Result callerResult,
		const DatabaseRuntimeResultClassification &classification,
		DatabaseOutageTimePoint now
	) {
		(void)publish(classification, now);
		return callerResult;
	}

	[[nodiscard]] DatabaseOutageSnapshot snapshot() const {
		return stateOwner_.snapshot();
	}

private:
	[[nodiscard]] DatabaseOutageTimePoint clampTimeLocked(DatabaseOutageTimePoint now) const {
		const auto snapshot = stateOwner_.snapshot();
		if (snapshot.lastEventTime.has_value() && now < *snapshot.lastEventTime) {
			return *snapshot.lastEventTime;
		}
		return now;
	}

	[[nodiscard]] DatabaseOutageEventSequence nextSequenceLocked() noexcept {
		const auto sequence = nextSequence_;
		if (nextSequence_ < std::numeric_limits<DatabaseOutageEventSequence>::max()) {
			++nextSequence_;
		}
		return sequence;
	}

	void advanceSequenceLocked(DatabaseOutageEventSequence sequence) noexcept {
		if (sequence < nextSequence_) {
			return;
		}
		if (sequence == std::numeric_limits<DatabaseOutageEventSequence>::max()) {
			nextSequence_ = sequence;
			return;
		}
		nextSequence_ = sequence + 1;
	}

	[[nodiscard]] DatabaseOutagePublicationResult publishLocked(
		DatabaseOutageEventSequence sequence,
		const DatabaseRuntimeResultClassification &classification,
		DatabaseOutageTimePoint now
	) {
		const auto failureReason = classification.failureReason.value_or(DatabaseOutageFailureReason::QueryFailed);
		const auto commitOutcome = classification.commitOutcome.value_or(DatabaseOutageCommitOutcome::Unknown);
		return DatabaseOutagePublicationResult {
			.disposition = DatabaseOutagePublicationDisposition::Published,
			.event = stateOwner_.runtimeFailure(sequence, failureReason, commitOutcome, now),
		};
	}

	DatabaseOutageStateMachine &stateOwner_;
	mutable std::mutex mutex_;
	DatabaseOutageEventSequence nextSequence_ = 1;
};

[[nodiscard]] DatabaseOutageSnapshot getDatabaseOutageSnapshot();
[[nodiscard]] DatabaseOutageEventResult publishDatabaseOutageDegradedDeadlineExpired(DatabaseOutageTimePoint now);
[[nodiscard]] DatabaseOutageEventResult publishDatabaseOutageDrainCompleted(DatabaseOutageTimePoint now);
[[nodiscard]] DatabaseOutageEventResult publishDatabaseOutageDrainDeadlineExpired(DatabaseOutageTimePoint now);
