#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <limits>
	#include <mutex>
	#include <stdexcept>
#endif

using SessionFenceSubjectId = uint64_t;
using SessionFenceOwnershipGeneration = uint64_t;
using SessionFencePersistenceRevision = uint64_t;
using SessionFenceWriterToken = uint64_t;
using SessionFenceEventSequence = uint64_t;

enum class SessionFenceStatus : uint8_t {
	Vacant,
	Owned,
	Released,
};

enum class SessionFenceDisposition : uint8_t {
	Applied,
	AcceptedDuplicate,
	RejectedMalformed,
	RejectedStaleEvent,
	RejectedDuplicateEvent,
	RejectedState,
	RejectedSubject,
	RejectedGeneration,
	RejectedWriter,
	RejectedRevision,
};

enum class SessionFenceReason : uint8_t {
	Initial,
	OwnershipAcquired,
	OwnershipTransferred,
	OwnershipReleased,
	PersistenceRevisionAdvanced,
	MalformedContext,
	StaleEventSequence,
	DuplicateEventSequence,
	OwnershipAlreadyHeld,
	FenceNotOwned,
	SubjectMismatch,
	StaleOwnershipGeneration,
	OwnershipGenerationConflict,
	WriterMismatch,
	TransferRequired,
	StalePersistenceRevision,
	DuplicatePersistenceRevision,
	PersistenceRevisionGap,
	PersistenceRevisionExhausted,
};

struct SessionFenceOwnerContext final {
	SessionFenceSubjectId subjectId = 0;
	SessionFenceOwnershipGeneration ownershipGeneration = 0;
	SessionFenceWriterToken writerToken = 0;
};

struct SessionFenceSnapshot final {
	SessionFenceSubjectId subjectId = 0;
	SessionFenceStatus status = SessionFenceStatus::Vacant;
	SessionFenceOwnershipGeneration ownershipGeneration = 0;
	SessionFencePersistenceRevision persistenceRevision = 0;
	SessionFenceWriterToken authorizedWriterToken = 0;
	SessionFenceEventSequence lastEventSequence = 0;
	SessionFenceReason lastTransitionReason = SessionFenceReason::Initial;
	uint64_t transitionCount = 0;
};

struct SessionFenceWriteDecision final {
	SessionFenceDisposition disposition = SessionFenceDisposition::RejectedState;
	SessionFenceReason reason = SessionFenceReason::FenceNotOwned;
	SessionFencePersistenceRevision proposedRevision = 0;
	SessionFenceSnapshot fence;

	[[nodiscard]] bool authorized() const noexcept {
		return disposition == SessionFenceDisposition::Applied
			&& reason == SessionFenceReason::PersistenceRevisionAdvanced;
	}
};

struct SessionFenceEventResult final {
	SessionFenceDisposition disposition = SessionFenceDisposition::RejectedState;
	SessionFenceReason reason = SessionFenceReason::Initial;
	SessionFenceEventSequence eventSequence = 0;
	SessionFenceSnapshot before;
	SessionFenceSnapshot after;

	[[nodiscard]] bool stateChanged() const noexcept {
		return before.transitionCount != after.transitionCount;
	}

	[[nodiscard]] bool persistenceAuthorized() const noexcept {
		return disposition == SessionFenceDisposition::Applied
			&& reason == SessionFenceReason::PersistenceRevisionAdvanced;
	}
};

struct SessionFenceAcquireEvent final {
	SessionFenceEventSequence eventSequence = 0;
	SessionFenceSubjectId subjectId = 0;
	SessionFenceOwnershipGeneration ownershipGeneration = 0;
	SessionFenceWriterToken writerToken = 0;
};

struct SessionFenceTransferEvent final {
	SessionFenceEventSequence eventSequence = 0;
	SessionFenceOwnerContext currentOwner;
	SessionFenceOwnershipGeneration nextOwnershipGeneration = 0;
	SessionFenceWriterToken nextWriterToken = 0;
};

struct SessionFenceReleaseEvent final {
	SessionFenceEventSequence eventSequence = 0;
	SessionFenceOwnerContext currentOwner;
};

struct SessionFencePersistEvent final {
	SessionFenceEventSequence eventSequence = 0;
	SessionFenceOwnerContext currentOwner;
	SessionFencePersistenceRevision nextPersistenceRevision = 0;
};

/**
 * Owns one process-local model of the durable fence for one stable subject.
 *
 * The object is independent from databases, protocols, schedulers and clocks.
 * Callers supply a monotonic event sequence. All operations are internally
 * serialized and return immutable before/after snapshots.
 *
 * This object defines the compare-and-swap contract only. A future durable
 * adapter must enforce subject, ownership generation, writer token and current
 * persistence revision atomically in the authoritative database.
 */
class SessionRevisionFence final {
public:
	explicit SessionRevisionFence(SessionFenceSubjectId subjectId) :
		subjectId_(subjectId) {
		if (subjectId_ == 0) {
			throw std::invalid_argument("session fence subject id must be non-zero");
		}
	}

	SessionRevisionFence(const SessionRevisionFence &) = delete;
	SessionRevisionFence &operator=(const SessionRevisionFence &) = delete;

	[[nodiscard]] SessionFenceSnapshot snapshot() const {
		std::lock_guard lock(mutex_);
		return snapshotLocked();
	}

	[[nodiscard]] SessionFenceWriteDecision mayPersist(
		const SessionFenceOwnerContext &owner,
		SessionFencePersistenceRevision proposedRevision
	) const {
		std::lock_guard lock(mutex_);
		return evaluateWriteLocked(owner, proposedRevision);
	}

	[[nodiscard]] SessionFenceEventResult acquire(const SessionFenceAcquireEvent &event) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (event.eventSequence == 0 || event.subjectId == 0 || event.ownershipGeneration == 0 || event.writerToken == 0) {
			return makeResultLocked(SessionFenceDisposition::RejectedMalformed, SessionFenceReason::MalformedContext, event.eventSequence, before);
		}
		if (event.subjectId != subjectId_) {
			return makeResultLocked(SessionFenceDisposition::RejectedSubject, SessionFenceReason::SubjectMismatch, event.eventSequence, before);
		}
		if (const auto rejected = rejectEventSequenceLocked(event.eventSequence, before); rejected.has_value()) {
			return *rejected;
		}

		if (status_ == SessionFenceStatus::Owned) {
			if (event.ownershipGeneration < ownershipGeneration_) {
				return makeResultLocked(SessionFenceDisposition::RejectedGeneration, SessionFenceReason::StaleOwnershipGeneration, event.eventSequence, before);
			}
			if (event.ownershipGeneration == ownershipGeneration_) {
				if (event.writerToken == authorizedWriterToken_) {
					return makeResultLocked(SessionFenceDisposition::AcceptedDuplicate, SessionFenceReason::OwnershipAlreadyHeld, event.eventSequence, before);
				}
				return makeResultLocked(SessionFenceDisposition::RejectedGeneration, SessionFenceReason::OwnershipGenerationConflict, event.eventSequence, before);
			}
			return makeResultLocked(SessionFenceDisposition::RejectedState, SessionFenceReason::TransferRequired, event.eventSequence, before);
		}

		if (event.ownershipGeneration <= ownershipGeneration_) {
			const auto reason = event.ownershipGeneration < ownershipGeneration_
				? SessionFenceReason::StaleOwnershipGeneration
				: SessionFenceReason::OwnershipGenerationConflict;
			return makeResultLocked(SessionFenceDisposition::RejectedGeneration, reason, event.eventSequence, before);
		}

		status_ = SessionFenceStatus::Owned;
		ownershipGeneration_ = event.ownershipGeneration;
		authorizedWriterToken_ = event.writerToken;
		transitionLocked(SessionFenceReason::OwnershipAcquired);
		return makeResultLocked(SessionFenceDisposition::Applied, SessionFenceReason::OwnershipAcquired, event.eventSequence, before);
	}

	[[nodiscard]] SessionFenceEventResult transfer(const SessionFenceTransferEvent &event) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (!validOwnerContext(event.currentOwner) || event.eventSequence == 0 || event.nextOwnershipGeneration == 0 || event.nextWriterToken == 0) {
			return makeResultLocked(SessionFenceDisposition::RejectedMalformed, SessionFenceReason::MalformedContext, event.eventSequence, before);
		}
		if (event.currentOwner.subjectId != subjectId_) {
			return makeResultLocked(SessionFenceDisposition::RejectedSubject, SessionFenceReason::SubjectMismatch, event.eventSequence, before);
		}
		if (const auto rejected = rejectEventSequenceLocked(event.eventSequence, before); rejected.has_value()) {
			return *rejected;
		}
		if (const auto rejected = rejectCurrentOwnerLocked(event.currentOwner, event.eventSequence, before); rejected.has_value()) {
			return *rejected;
		}
		if (event.nextOwnershipGeneration <= ownershipGeneration_) {
			const auto reason = event.nextOwnershipGeneration < ownershipGeneration_
				? SessionFenceReason::StaleOwnershipGeneration
				: SessionFenceReason::OwnershipGenerationConflict;
			return makeResultLocked(SessionFenceDisposition::RejectedGeneration, reason, event.eventSequence, before);
		}

		ownershipGeneration_ = event.nextOwnershipGeneration;
		authorizedWriterToken_ = event.nextWriterToken;
		transitionLocked(SessionFenceReason::OwnershipTransferred);
		return makeResultLocked(SessionFenceDisposition::Applied, SessionFenceReason::OwnershipTransferred, event.eventSequence, before);
	}

	[[nodiscard]] SessionFenceEventResult release(const SessionFenceReleaseEvent &event) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (!validOwnerContext(event.currentOwner) || event.eventSequence == 0) {
			return makeResultLocked(SessionFenceDisposition::RejectedMalformed, SessionFenceReason::MalformedContext, event.eventSequence, before);
		}
		if (event.currentOwner.subjectId != subjectId_) {
			return makeResultLocked(SessionFenceDisposition::RejectedSubject, SessionFenceReason::SubjectMismatch, event.eventSequence, before);
		}
		if (const auto rejected = rejectEventSequenceLocked(event.eventSequence, before); rejected.has_value()) {
			return *rejected;
		}
		if (const auto rejected = rejectCurrentOwnerLocked(event.currentOwner, event.eventSequence, before); rejected.has_value()) {
			return *rejected;
		}

		status_ = SessionFenceStatus::Released;
		authorizedWriterToken_ = 0;
		transitionLocked(SessionFenceReason::OwnershipReleased);
		return makeResultLocked(SessionFenceDisposition::Applied, SessionFenceReason::OwnershipReleased, event.eventSequence, before);
	}

	[[nodiscard]] SessionFenceEventResult persist(const SessionFencePersistEvent &event) {
		std::lock_guard lock(mutex_);
		const auto before = snapshotLocked();
		if (!validOwnerContext(event.currentOwner) || event.eventSequence == 0 || event.nextPersistenceRevision == 0) {
			return makeResultLocked(SessionFenceDisposition::RejectedMalformed, SessionFenceReason::MalformedContext, event.eventSequence, before);
		}
		if (event.currentOwner.subjectId != subjectId_) {
			return makeResultLocked(SessionFenceDisposition::RejectedSubject, SessionFenceReason::SubjectMismatch, event.eventSequence, before);
		}
		if (const auto rejected = rejectEventSequenceLocked(event.eventSequence, before); rejected.has_value()) {
			return *rejected;
		}

		const auto decision = evaluateWriteLocked(event.currentOwner, event.nextPersistenceRevision);
		if (!decision.authorized()) {
			return makeResultLocked(decision.disposition, decision.reason, event.eventSequence, before);
		}

		persistenceRevision_ = event.nextPersistenceRevision;
		transitionLocked(SessionFenceReason::PersistenceRevisionAdvanced);
		return makeResultLocked(SessionFenceDisposition::Applied, SessionFenceReason::PersistenceRevisionAdvanced, event.eventSequence, before);
	}

private:
	[[nodiscard]] static bool validOwnerContext(const SessionFenceOwnerContext &owner) noexcept {
		return owner.subjectId != 0 && owner.ownershipGeneration != 0 && owner.writerToken != 0;
	}

	[[nodiscard]] SessionFenceWriteDecision evaluateWriteLocked(
		const SessionFenceOwnerContext &owner,
		SessionFencePersistenceRevision proposedRevision
	) const {
		const auto fence = snapshotLocked();
		if (!validOwnerContext(owner) || proposedRevision == 0) {
			return { SessionFenceDisposition::RejectedMalformed, SessionFenceReason::MalformedContext, proposedRevision, fence };
		}
		if (owner.subjectId != subjectId_) {
			return { SessionFenceDisposition::RejectedSubject, SessionFenceReason::SubjectMismatch, proposedRevision, fence };
		}
		if (status_ != SessionFenceStatus::Owned) {
			return { SessionFenceDisposition::RejectedState, SessionFenceReason::FenceNotOwned, proposedRevision, fence };
		}
		if (owner.ownershipGeneration < ownershipGeneration_) {
			return { SessionFenceDisposition::RejectedGeneration, SessionFenceReason::StaleOwnershipGeneration, proposedRevision, fence };
		}
		if (owner.ownershipGeneration > ownershipGeneration_) {
			return { SessionFenceDisposition::RejectedGeneration, SessionFenceReason::OwnershipGenerationConflict, proposedRevision, fence };
		}
		if (owner.writerToken != authorizedWriterToken_) {
			return { SessionFenceDisposition::RejectedWriter, SessionFenceReason::WriterMismatch, proposedRevision, fence };
		}
		if (proposedRevision < persistenceRevision_) {
			return { SessionFenceDisposition::RejectedRevision, SessionFenceReason::StalePersistenceRevision, proposedRevision, fence };
		}
		if (proposedRevision == persistenceRevision_) {
			return { SessionFenceDisposition::RejectedRevision, SessionFenceReason::DuplicatePersistenceRevision, proposedRevision, fence };
		}
		if (persistenceRevision_ == std::numeric_limits<SessionFencePersistenceRevision>::max()) {
			return { SessionFenceDisposition::RejectedRevision, SessionFenceReason::PersistenceRevisionExhausted, proposedRevision, fence };
		}
		if (proposedRevision != persistenceRevision_ + 1) {
			return { SessionFenceDisposition::RejectedRevision, SessionFenceReason::PersistenceRevisionGap, proposedRevision, fence };
		}

		return { SessionFenceDisposition::Applied, SessionFenceReason::PersistenceRevisionAdvanced, proposedRevision, fence };
	}

	[[nodiscard]] std::optional<SessionFenceEventResult> rejectEventSequenceLocked(
		SessionFenceEventSequence eventSequence,
		const SessionFenceSnapshot &before
	) {
		if (eventSequence < lastEventSequence_) {
			return makeResultLocked(SessionFenceDisposition::RejectedStaleEvent, SessionFenceReason::StaleEventSequence, eventSequence, before);
		}
		if (eventSequence == lastEventSequence_) {
			return makeResultLocked(SessionFenceDisposition::RejectedDuplicateEvent, SessionFenceReason::DuplicateEventSequence, eventSequence, before);
		}

		lastEventSequence_ = eventSequence;
		return std::nullopt;
	}

	[[nodiscard]] std::optional<SessionFenceEventResult> rejectCurrentOwnerLocked(
		const SessionFenceOwnerContext &owner,
		SessionFenceEventSequence eventSequence,
		const SessionFenceSnapshot &before
	) const {
		if (status_ != SessionFenceStatus::Owned) {
			return makeResultLocked(SessionFenceDisposition::RejectedState, SessionFenceReason::FenceNotOwned, eventSequence, before);
		}
		if (owner.ownershipGeneration < ownershipGeneration_) {
			return makeResultLocked(SessionFenceDisposition::RejectedGeneration, SessionFenceReason::StaleOwnershipGeneration, eventSequence, before);
		}
		if (owner.ownershipGeneration > ownershipGeneration_) {
			return makeResultLocked(SessionFenceDisposition::RejectedGeneration, SessionFenceReason::OwnershipGenerationConflict, eventSequence, before);
		}
		if (owner.writerToken != authorizedWriterToken_) {
			return makeResultLocked(SessionFenceDisposition::RejectedWriter, SessionFenceReason::WriterMismatch, eventSequence, before);
		}
		return std::nullopt;
	}

	void transitionLocked(SessionFenceReason reason) noexcept {
		lastTransitionReason_ = reason;
		if (transitionCount_ < std::numeric_limits<uint64_t>::max()) {
			++transitionCount_;
		}
	}

	[[nodiscard]] SessionFenceSnapshot snapshotLocked() const noexcept {
		return SessionFenceSnapshot {
			.subjectId = subjectId_,
			.status = status_,
			.ownershipGeneration = ownershipGeneration_,
			.persistenceRevision = persistenceRevision_,
			.authorizedWriterToken = authorizedWriterToken_,
			.lastEventSequence = lastEventSequence_,
			.lastTransitionReason = lastTransitionReason_,
			.transitionCount = transitionCount_,
		};
	}

	[[nodiscard]] SessionFenceEventResult makeResultLocked(
		SessionFenceDisposition disposition,
		SessionFenceReason reason,
		SessionFenceEventSequence eventSequence,
		const SessionFenceSnapshot &before
	) const noexcept {
		return SessionFenceEventResult {
			.disposition = disposition,
			.reason = reason,
			.eventSequence = eventSequence,
			.before = before,
			.after = snapshotLocked(),
		};
	}

	mutable std::mutex mutex_;
	const SessionFenceSubjectId subjectId_;
	SessionFenceStatus status_ = SessionFenceStatus::Vacant;
	SessionFenceOwnershipGeneration ownershipGeneration_ = 0;
	SessionFencePersistenceRevision persistenceRevision_ = 0;
	SessionFenceWriterToken authorizedWriterToken_ = 0;
	SessionFenceEventSequence lastEventSequence_ = 0;
	SessionFenceReason lastTransitionReason_ = SessionFenceReason::Initial;
	uint64_t transitionCount_ = 0;
};
