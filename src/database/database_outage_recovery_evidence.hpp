#pragma once

#include "database/database_outage_state.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <limits>
	#include <optional>
	#include <stdexcept>
#endif

enum class DatabaseRecoveryEvidenceAction : uint8_t {
	Continue,
	PublishRecoveryEvidenceAccepted,
	Stop,
	NoAction,
};

enum class DatabaseRecoveryEvidenceReason : uint8_t {
	CandidateStarted,
	ProbeSucceeded,
	ReadFailed,
	TransactionBeginFailed,
	TransactionWriteFailed,
	TransactionRollbackFailed,
	ProbeObjectChanged,
	DeadlineExpired,
	AttemptBudgetExhausted,
	CandidateInactive,
	AlreadyAccepted,
	QualifyingFailure,
	PublicationAccepted,
	PublicationRejected,
};

struct DatabaseRecoveryProbeAttempt final {
	bool readSucceeded = false;
	bool transactionBeginSucceeded = false;
	bool transactionWriteSucceeded = false;
	bool transactionRollbackSucceeded = false;
	bool probeObjectUnchanged = false;
};

struct DatabaseRecoveryEvidenceDecision final {
	DatabaseRecoveryEvidenceAction action = DatabaseRecoveryEvidenceAction::NoAction;
	DatabaseRecoveryEvidenceReason reason = DatabaseRecoveryEvidenceReason::CandidateInactive;
	uint32_t attempts = 0;
	uint32_t consecutiveSuccesses = 0;
	bool candidateActive = false;
	bool publicationPending = false;
	bool evidenceAccepted = false;
	bool deadlineExpired = false;
	bool attemptBudgetExhausted = false;
	std::optional<DatabaseOutageTimePoint> deadline;
};

struct DatabaseRecoveryEvidenceSummary final {
	uint32_t attempts = 0;
	uint32_t consecutiveSuccesses = 0;
	uint32_t readFailures = 0;
	uint32_t transactionBeginFailures = 0;
	uint32_t transactionWriteFailures = 0;
	uint32_t transactionRollbackFailures = 0;
	uint32_t probeObjectChangedFailures = 0;
	uint32_t qualifyingFailures = 0;
	uint32_t publicationAttempts = 0;
	uint32_t acceptedPublications = 0;
	bool candidateActive = false;
	bool publicationPending = false;
	bool evidenceAccepted = false;
	bool deadlineExpired = false;
	bool attemptBudgetExhausted = false;
	std::optional<DatabaseOutageTimePoint> deadline;
	DatabaseRecoveryEvidenceReason lastReason = DatabaseRecoveryEvidenceReason::CandidateInactive;
};

class DatabaseOutageRecoveryEvidence final {
public:
	struct Bounds final {
		uint32_t requiredConsecutiveSuccesses = 0;
		uint32_t maxAttempts = 0;
		DatabaseOutageTimePoint window { 0 };
	};

	explicit DatabaseOutageRecoveryEvidence(Bounds bounds) :
		bounds_(bounds) {
		if (bounds_.requiredConsecutiveSuccesses == 0 || bounds_.maxAttempts == 0 || bounds_.maxAttempts < bounds_.requiredConsecutiveSuccesses || bounds_.window.count() <= 0) {
			throw std::invalid_argument("database recovery evidence bounds must be finite and positive");
		}
	}

	DatabaseOutageRecoveryEvidence(const DatabaseOutageRecoveryEvidence &) = delete;
	DatabaseOutageRecoveryEvidence &operator=(const DatabaseOutageRecoveryEvidence &) = delete;

	[[nodiscard]] DatabaseRecoveryEvidenceDecision begin(DatabaseOutageTimePoint now) noexcept {
		attempts_ = 0;
		consecutiveSuccesses_ = 0;
		candidateActive_ = true;
		publicationPending_ = false;
		evidenceAccepted_ = false;
		deadlineExpired_ = false;
		attemptBudgetExhausted_ = false;
		deadline_ = addDuration(now, bounds_.window);
		lastReason_ = DatabaseRecoveryEvidenceReason::CandidateStarted;
		return decision(DatabaseRecoveryEvidenceAction::Continue, lastReason_);
	}

	[[nodiscard]] DatabaseRecoveryEvidenceDecision recordProbe(const DatabaseRecoveryProbeAttempt &attempt, DatabaseOutageTimePoint now) noexcept {
		if (evidenceAccepted_ || publicationPending_) {
			lastReason_ = DatabaseRecoveryEvidenceReason::AlreadyAccepted;
			return decision(DatabaseRecoveryEvidenceAction::NoAction, lastReason_);
		}
		if (!candidateActive_) {
			lastReason_ = attemptBudgetExhausted_
				? DatabaseRecoveryEvidenceReason::AttemptBudgetExhausted
				: DatabaseRecoveryEvidenceReason::CandidateInactive;
			return decision(DatabaseRecoveryEvidenceAction::Stop, lastReason_);
		}
		if (!deadline_.has_value() || now >= *deadline_) {
			candidateActive_ = false;
			deadlineExpired_ = true;
			consecutiveSuccesses_ = 0;
			lastReason_ = DatabaseRecoveryEvidenceReason::DeadlineExpired;
			return decision(DatabaseRecoveryEvidenceAction::Stop, lastReason_);
		}
		if (attempts_ >= bounds_.maxAttempts) {
			candidateActive_ = false;
			attemptBudgetExhausted_ = true;
			consecutiveSuccesses_ = 0;
			lastReason_ = DatabaseRecoveryEvidenceReason::AttemptBudgetExhausted;
			return decision(DatabaseRecoveryEvidenceAction::Stop, lastReason_);
		}

		++attempts_;
		const auto failure = classifyFailure(attempt);
		if (failure.has_value()) {
			consecutiveSuccesses_ = 0;
			observeFailure(*failure);
			lastReason_ = *failure;
			if (attempts_ >= bounds_.maxAttempts) {
				candidateActive_ = false;
				attemptBudgetExhausted_ = true;
			}
			return decision(candidateActive_ ? DatabaseRecoveryEvidenceAction::Continue : DatabaseRecoveryEvidenceAction::Stop, lastReason_);
		}

		if (consecutiveSuccesses_ < std::numeric_limits<uint32_t>::max()) {
			++consecutiveSuccesses_;
		}
		lastReason_ = DatabaseRecoveryEvidenceReason::ProbeSucceeded;
		if (consecutiveSuccesses_ >= bounds_.requiredConsecutiveSuccesses) {
			candidateActive_ = false;
			publicationPending_ = true;
			return decision(DatabaseRecoveryEvidenceAction::PublishRecoveryEvidenceAccepted, lastReason_);
		}
		if (attempts_ >= bounds_.maxAttempts) {
			candidateActive_ = false;
			attemptBudgetExhausted_ = true;
			lastReason_ = DatabaseRecoveryEvidenceReason::AttemptBudgetExhausted;
			return decision(DatabaseRecoveryEvidenceAction::Stop, lastReason_);
		}
		return decision(DatabaseRecoveryEvidenceAction::Continue, lastReason_);
	}

	[[nodiscard]] std::optional<DatabaseOutageEventResult> publishIfReady(
		DatabaseOutageStateMachine &stateOwner,
		DatabaseOutageEventSequence eventSequence,
		DatabaseOutageTimePoint now
	) noexcept {
		if (!publicationPending_) {
			return std::nullopt;
		}
		publicationPending_ = false;
		if (publicationAttempts_ < std::numeric_limits<uint32_t>::max()) {
			++publicationAttempts_;
		}
		auto event = stateOwner.recoveryEvidenceAccepted(eventSequence, now);
		if (event.disposition == DatabaseOutageEventDisposition::AcceptedNoStateChange && event.after.recoveryEvidenceAccepted) {
			evidenceAccepted_ = true;
			if (acceptedPublications_ < std::numeric_limits<uint32_t>::max()) {
				++acceptedPublications_;
			}
			lastReason_ = DatabaseRecoveryEvidenceReason::PublicationAccepted;
		} else {
			evidenceAccepted_ = false;
			lastReason_ = DatabaseRecoveryEvidenceReason::PublicationRejected;
		}
		return event;
	}

	[[nodiscard]] DatabaseRecoveryEvidenceDecision qualifyingFailure() noexcept {
		candidateActive_ = false;
		publicationPending_ = false;
		evidenceAccepted_ = false;
		consecutiveSuccesses_ = 0;
		if (qualifyingFailures_ < std::numeric_limits<uint32_t>::max()) {
			++qualifyingFailures_;
		}
		lastReason_ = DatabaseRecoveryEvidenceReason::QualifyingFailure;
		return decision(DatabaseRecoveryEvidenceAction::Stop, lastReason_);
	}

	[[nodiscard]] DatabaseRecoveryEvidenceSummary summary() const noexcept {
		return DatabaseRecoveryEvidenceSummary {
			.attempts = attempts_,
			.consecutiveSuccesses = consecutiveSuccesses_,
			.readFailures = readFailures_,
			.transactionBeginFailures = transactionBeginFailures_,
			.transactionWriteFailures = transactionWriteFailures_,
			.transactionRollbackFailures = transactionRollbackFailures_,
			.probeObjectChangedFailures = probeObjectChangedFailures_,
			.qualifyingFailures = qualifyingFailures_,
			.publicationAttempts = publicationAttempts_,
			.acceptedPublications = acceptedPublications_,
			.candidateActive = candidateActive_,
			.publicationPending = publicationPending_,
			.evidenceAccepted = evidenceAccepted_,
			.deadlineExpired = deadlineExpired_,
			.attemptBudgetExhausted = attemptBudgetExhausted_,
			.deadline = deadline_,
			.lastReason = lastReason_,
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

	[[nodiscard]] static std::optional<DatabaseRecoveryEvidenceReason> classifyFailure(const DatabaseRecoveryProbeAttempt &attempt) noexcept {
		if (!attempt.readSucceeded) {
			return DatabaseRecoveryEvidenceReason::ReadFailed;
		}
		if (!attempt.transactionBeginSucceeded) {
			return DatabaseRecoveryEvidenceReason::TransactionBeginFailed;
		}
		if (!attempt.transactionWriteSucceeded) {
			return DatabaseRecoveryEvidenceReason::TransactionWriteFailed;
		}
		if (!attempt.transactionRollbackSucceeded) {
			return DatabaseRecoveryEvidenceReason::TransactionRollbackFailed;
		}
		if (!attempt.probeObjectUnchanged) {
			return DatabaseRecoveryEvidenceReason::ProbeObjectChanged;
		}
		return std::nullopt;
	}

	void observeFailure(DatabaseRecoveryEvidenceReason reason) noexcept {
		uint32_t* counter = nullptr;
		switch (reason) {
			case DatabaseRecoveryEvidenceReason::ReadFailed:
				counter = &readFailures_;
				break;
			case DatabaseRecoveryEvidenceReason::TransactionBeginFailed:
				counter = &transactionBeginFailures_;
				break;
			case DatabaseRecoveryEvidenceReason::TransactionWriteFailed:
				counter = &transactionWriteFailures_;
				break;
			case DatabaseRecoveryEvidenceReason::TransactionRollbackFailed:
				counter = &transactionRollbackFailures_;
				break;
			case DatabaseRecoveryEvidenceReason::ProbeObjectChanged:
				counter = &probeObjectChangedFailures_;
				break;
			default:
				break;
		}
		if (counter != nullptr && *counter < std::numeric_limits<uint32_t>::max()) {
			++(*counter);
		}
	}

	[[nodiscard]] DatabaseRecoveryEvidenceDecision decision(DatabaseRecoveryEvidenceAction action, DatabaseRecoveryEvidenceReason reason) const noexcept {
		return DatabaseRecoveryEvidenceDecision {
			.action = action,
			.reason = reason,
			.attempts = attempts_,
			.consecutiveSuccesses = consecutiveSuccesses_,
			.candidateActive = candidateActive_,
			.publicationPending = publicationPending_,
			.evidenceAccepted = evidenceAccepted_,
			.deadlineExpired = deadlineExpired_,
			.attemptBudgetExhausted = attemptBudgetExhausted_,
			.deadline = deadline_,
		};
	}

	const Bounds bounds_;
	uint32_t attempts_ = 0;
	uint32_t consecutiveSuccesses_ = 0;
	uint32_t readFailures_ = 0;
	uint32_t transactionBeginFailures_ = 0;
	uint32_t transactionWriteFailures_ = 0;
	uint32_t transactionRollbackFailures_ = 0;
	uint32_t probeObjectChangedFailures_ = 0;
	uint32_t qualifyingFailures_ = 0;
	uint32_t publicationAttempts_ = 0;
	uint32_t acceptedPublications_ = 0;
	bool candidateActive_ = false;
	bool publicationPending_ = false;
	bool evidenceAccepted_ = false;
	bool deadlineExpired_ = false;
	bool attemptBudgetExhausted_ = false;
	std::optional<DatabaseOutageTimePoint> deadline_;
	DatabaseRecoveryEvidenceReason lastReason_ = DatabaseRecoveryEvidenceReason::CandidateInactive;
};
