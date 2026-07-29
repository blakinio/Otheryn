#include <gtest/gtest.h>

#include "database/session_revision_fence.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <atomic>
	#include <thread>
	#include <vector>
#endif

namespace {
	constexpr SessionFenceSubjectId subjectId = 42;
	constexpr SessionFenceWriterToken firstWriter = 1001;
	constexpr SessionFenceWriterToken secondWriter = 2002;

	SessionFenceOwnerContext owner(SessionFenceOwnershipGeneration generation, SessionFenceWriterToken writerToken) {
		return SessionFenceOwnerContext {
			.subjectId = subjectId,
			.ownershipGeneration = generation,
			.writerToken = writerToken,
		};
	}

	SessionFenceAcquireEvent acquisition(
		SessionFenceEventSequence sequence,
		SessionFenceOwnershipGeneration generation,
		SessionFenceWriterToken writerToken
	) {
		return SessionFenceAcquireEvent {
			.eventSequence = sequence,
			.subjectId = subjectId,
			.ownershipGeneration = generation,
			.writerToken = writerToken,
		};
	}
} // namespace

TEST(SessionRevisionFenceTest, RejectsInvalidStableSubject) {
	EXPECT_THROW((SessionRevisionFence { 0 }), std::invalid_argument);
}

TEST(SessionRevisionFenceTest, StartsVacantAndFailsClosedWithoutOwnership) {
	SessionRevisionFence fence(subjectId);
	const auto snapshot = fence.snapshot();

	EXPECT_EQ(snapshot.subjectId, subjectId);
	EXPECT_EQ(snapshot.status, SessionFenceStatus::Vacant);
	EXPECT_EQ(snapshot.ownershipGeneration, 0U);
	EXPECT_EQ(snapshot.persistenceRevision, 0U);
	EXPECT_EQ(snapshot.authorizedWriterToken, 0U);
	EXPECT_EQ(snapshot.lastEventSequence, 0U);
	EXPECT_EQ(snapshot.lastTransitionReason, SessionFenceReason::Initial);
	EXPECT_EQ(snapshot.transitionCount, 0U);

	const auto missing = fence.mayPersist({}, 1);
	EXPECT_FALSE(missing.authorized());
	EXPECT_EQ(missing.disposition, SessionFenceDisposition::RejectedMalformed);
	EXPECT_EQ(missing.reason, SessionFenceReason::MalformedContext);

	const auto unowned = fence.mayPersist(owner(1, firstWriter), 1);
	EXPECT_FALSE(unowned.authorized());
	EXPECT_EQ(unowned.reason, SessionFenceReason::FenceNotOwned);
}

TEST(SessionRevisionFenceTest, FirstOwnershipAcquisitionCreatesOneEffectiveTransition) {
	SessionRevisionFence fence(subjectId);
	const auto result = fence.acquire(acquisition(1, 1, firstWriter));

	EXPECT_EQ(result.disposition, SessionFenceDisposition::Applied);
	EXPECT_EQ(result.reason, SessionFenceReason::OwnershipAcquired);
	EXPECT_TRUE(result.stateChanged());
	EXPECT_EQ(result.before.status, SessionFenceStatus::Vacant);
	EXPECT_EQ(result.after.status, SessionFenceStatus::Owned);
	EXPECT_EQ(result.after.ownershipGeneration, 1U);
	EXPECT_EQ(result.after.authorizedWriterToken, firstWriter);
	EXPECT_EQ(result.after.persistenceRevision, 0U);
	EXPECT_EQ(result.after.lastEventSequence, 1U);
	EXPECT_EQ(result.after.transitionCount, 1U);
}

TEST(SessionRevisionFenceTest, DuplicateAcquisitionIsDeterministicAndCannotReplaceOwner) {
	SessionRevisionFence fence(subjectId);
	ASSERT_EQ(fence.acquire(acquisition(1, 4, firstWriter)).disposition, SessionFenceDisposition::Applied);

	const auto exactReplay = fence.acquire(acquisition(1, 4, firstWriter));
	EXPECT_EQ(exactReplay.disposition, SessionFenceDisposition::RejectedDuplicateEvent);
	EXPECT_EQ(exactReplay.reason, SessionFenceReason::DuplicateEventSequence);
	EXPECT_FALSE(exactReplay.stateChanged());

	const auto laterDuplicate = fence.acquire(acquisition(2, 4, firstWriter));
	EXPECT_EQ(laterDuplicate.disposition, SessionFenceDisposition::AcceptedDuplicate);
	EXPECT_EQ(laterDuplicate.reason, SessionFenceReason::OwnershipAlreadyHeld);
	EXPECT_FALSE(laterDuplicate.stateChanged());
	EXPECT_EQ(laterDuplicate.after.transitionCount, 1U);

	const auto conflictingWriter = fence.acquire(acquisition(3, 4, secondWriter));
	EXPECT_EQ(conflictingWriter.disposition, SessionFenceDisposition::RejectedGeneration);
	EXPECT_EQ(conflictingWriter.reason, SessionFenceReason::OwnershipGenerationConflict);
	EXPECT_EQ(conflictingWriter.after.authorizedWriterToken, firstWriter);
	EXPECT_EQ(conflictingWriter.after.transitionCount, 1U);

	const auto implicitReplacement = fence.acquire(acquisition(4, 5, secondWriter));
	EXPECT_EQ(implicitReplacement.disposition, SessionFenceDisposition::RejectedState);
	EXPECT_EQ(implicitReplacement.reason, SessionFenceReason::TransferRequired);
	EXPECT_EQ(implicitReplacement.after.ownershipGeneration, 4U);
	EXPECT_EQ(implicitReplacement.after.authorizedWriterToken, firstWriter);
}

TEST(SessionRevisionFenceTest, TransferMovesAuthorityForwardAndPreservesRevision) {
	SessionRevisionFence fence(subjectId);
	ASSERT_EQ(fence.acquire(acquisition(1, 1, firstWriter)).disposition, SessionFenceDisposition::Applied);
	ASSERT_TRUE(fence.persist({ 2, owner(1, firstWriter), 1 }).persistenceAuthorized());

	const auto transfer = fence.transfer({ 3, owner(1, firstWriter), 2, secondWriter });
	EXPECT_EQ(transfer.disposition, SessionFenceDisposition::Applied);
	EXPECT_EQ(transfer.reason, SessionFenceReason::OwnershipTransferred);
	EXPECT_EQ(transfer.before.ownershipGeneration, 1U);
	EXPECT_EQ(transfer.before.authorizedWriterToken, firstWriter);
	EXPECT_EQ(transfer.after.ownershipGeneration, 2U);
	EXPECT_EQ(transfer.after.authorizedWriterToken, secondWriter);
	EXPECT_EQ(transfer.after.persistenceRevision, 1U);
	EXPECT_EQ(transfer.after.transitionCount, 3U);
}

TEST(SessionRevisionFenceTest, PreviousOwnerCannotWriteAfterHandoffButCurrentOwnerCan) {
	SessionRevisionFence fence(subjectId);
	ASSERT_EQ(fence.acquire(acquisition(1, 10, firstWriter)).disposition, SessionFenceDisposition::Applied);
	ASSERT_EQ(fence.transfer({ 2, owner(10, firstWriter), 11, secondWriter }).disposition, SessionFenceDisposition::Applied);

	const auto staleWriter = fence.mayPersist(owner(10, firstWriter), 1);
	EXPECT_FALSE(staleWriter.authorized());
	EXPECT_EQ(staleWriter.disposition, SessionFenceDisposition::RejectedGeneration);
	EXPECT_EQ(staleWriter.reason, SessionFenceReason::StaleOwnershipGeneration);

	const auto wrongWriter = fence.mayPersist(owner(11, firstWriter), 1);
	EXPECT_FALSE(wrongWriter.authorized());
	EXPECT_EQ(wrongWriter.disposition, SessionFenceDisposition::RejectedWriter);
	EXPECT_EQ(wrongWriter.reason, SessionFenceReason::WriterMismatch);

	const auto currentWriter = fence.mayPersist(owner(11, secondWriter), 1);
	EXPECT_TRUE(currentWriter.authorized());
	EXPECT_TRUE(fence.persist({ 3, owner(11, secondWriter), 1 }).persistenceAuthorized());
	EXPECT_EQ(fence.snapshot().persistenceRevision, 1U);
}

TEST(SessionRevisionFenceTest, OlderEqualAndSkippedRevisionsFailClosed) {
	SessionRevisionFence fence(subjectId);
	ASSERT_EQ(fence.acquire(acquisition(1, 1, firstWriter)).disposition, SessionFenceDisposition::Applied);
	ASSERT_TRUE(fence.persist({ 2, owner(1, firstWriter), 1 }).persistenceAuthorized());
	ASSERT_TRUE(fence.persist({ 3, owner(1, firstWriter), 2 }).persistenceAuthorized());

	const auto stale = fence.mayPersist(owner(1, firstWriter), 1);
	EXPECT_FALSE(stale.authorized());
	EXPECT_EQ(stale.reason, SessionFenceReason::StalePersistenceRevision);

	const auto duplicate = fence.mayPersist(owner(1, firstWriter), 2);
	EXPECT_FALSE(duplicate.authorized());
	EXPECT_EQ(duplicate.reason, SessionFenceReason::DuplicatePersistenceRevision);

	const auto gap = fence.mayPersist(owner(1, firstWriter), 4);
	EXPECT_FALSE(gap.authorized());
	EXPECT_EQ(gap.reason, SessionFenceReason::PersistenceRevisionGap);

	const auto next = fence.mayPersist(owner(1, firstWriter), 3);
	EXPECT_TRUE(next.authorized());
	const auto applied = fence.persist({ 4, owner(1, firstWriter), 3 });
	EXPECT_TRUE(applied.persistenceAuthorized());
	EXPECT_EQ(applied.after.persistenceRevision, 3U);
	EXPECT_EQ(applied.after.transitionCount, 4U);
}

TEST(SessionRevisionFenceTest, RevisionRejectionsNeverAdvanceDurableModel) {
	SessionRevisionFence fence(subjectId);
	ASSERT_EQ(fence.acquire(acquisition(1, 1, firstWriter)).disposition, SessionFenceDisposition::Applied);
	ASSERT_TRUE(fence.persist({ 2, owner(1, firstWriter), 1 }).persistenceAuthorized());

	const auto duplicate = fence.persist({ 3, owner(1, firstWriter), 1 });
	EXPECT_EQ(duplicate.disposition, SessionFenceDisposition::RejectedRevision);
	EXPECT_EQ(duplicate.reason, SessionFenceReason::DuplicatePersistenceRevision);
	EXPECT_FALSE(duplicate.persistenceAuthorized());
	EXPECT_FALSE(duplicate.stateChanged());
	EXPECT_EQ(duplicate.after.persistenceRevision, 1U);
	EXPECT_EQ(duplicate.after.transitionCount, 2U);

	const auto gap = fence.persist({ 4, owner(1, firstWriter), 3 });
	EXPECT_EQ(gap.disposition, SessionFenceDisposition::RejectedRevision);
	EXPECT_EQ(gap.reason, SessionFenceReason::PersistenceRevisionGap);
	EXPECT_EQ(gap.after.persistenceRevision, 1U);
	EXPECT_EQ(gap.after.transitionCount, 2U);
}

TEST(SessionRevisionFenceTest, ReleaseInvalidatesWriterAndReacquisitionRequiresNewerGeneration) {
	SessionRevisionFence fence(subjectId);
	ASSERT_EQ(fence.acquire(acquisition(1, 5, firstWriter)).disposition, SessionFenceDisposition::Applied);
	ASSERT_TRUE(fence.persist({ 2, owner(5, firstWriter), 1 }).persistenceAuthorized());

	const auto released = fence.release({ 3, owner(5, firstWriter) });
	EXPECT_EQ(released.disposition, SessionFenceDisposition::Applied);
	EXPECT_EQ(released.after.status, SessionFenceStatus::Released);
	EXPECT_EQ(released.after.authorizedWriterToken, 0U);
	EXPECT_EQ(released.after.ownershipGeneration, 5U);
	EXPECT_EQ(released.after.persistenceRevision, 1U);

	const auto formerWriter = fence.mayPersist(owner(5, firstWriter), 2);
	EXPECT_FALSE(formerWriter.authorized());
	EXPECT_EQ(formerWriter.reason, SessionFenceReason::FenceNotOwned);

	const auto sameGeneration = fence.acquire(acquisition(4, 5, secondWriter));
	EXPECT_EQ(sameGeneration.disposition, SessionFenceDisposition::RejectedGeneration);
	EXPECT_EQ(sameGeneration.reason, SessionFenceReason::OwnershipGenerationConflict);

	const auto reacquired = fence.acquire(acquisition(5, 6, secondWriter));
	EXPECT_EQ(reacquired.disposition, SessionFenceDisposition::Applied);
	EXPECT_EQ(reacquired.after.status, SessionFenceStatus::Owned);
	EXPECT_EQ(reacquired.after.ownershipGeneration, 6U);
	EXPECT_EQ(reacquired.after.persistenceRevision, 1U);
	EXPECT_TRUE(fence.mayPersist(owner(6, secondWriter), 2).authorized());
}

TEST(SessionRevisionFenceTest, StaleTransferAndReleaseCannotMoveOwnershipBackward) {
	SessionRevisionFence fence(subjectId);
	ASSERT_EQ(fence.acquire(acquisition(1, 7, firstWriter)).disposition, SessionFenceDisposition::Applied);
	ASSERT_EQ(fence.transfer({ 2, owner(7, firstWriter), 8, secondWriter }).disposition, SessionFenceDisposition::Applied);

	const auto staleTransfer = fence.transfer({ 3, owner(7, firstWriter), 9, firstWriter });
	EXPECT_EQ(staleTransfer.disposition, SessionFenceDisposition::RejectedGeneration);
	EXPECT_EQ(staleTransfer.reason, SessionFenceReason::StaleOwnershipGeneration);
	EXPECT_EQ(staleTransfer.after.ownershipGeneration, 8U);
	EXPECT_EQ(staleTransfer.after.authorizedWriterToken, secondWriter);

	const auto staleRelease = fence.release({ 4, owner(7, firstWriter) });
	EXPECT_EQ(staleRelease.disposition, SessionFenceDisposition::RejectedGeneration);
	EXPECT_EQ(staleRelease.reason, SessionFenceReason::StaleOwnershipGeneration);
	EXPECT_EQ(staleRelease.after.status, SessionFenceStatus::Owned);
	EXPECT_EQ(staleRelease.after.transitionCount, 2U);
}

TEST(SessionRevisionFenceTest, StaleAndDuplicateEventSequencesAreRejected) {
	SessionRevisionFence fence(subjectId);
	ASSERT_EQ(fence.acquire(acquisition(10, 1, firstWriter)).disposition, SessionFenceDisposition::Applied);

	const auto stale = fence.persist({ 9, owner(1, firstWriter), 1 });
	EXPECT_EQ(stale.disposition, SessionFenceDisposition::RejectedStaleEvent);
	EXPECT_EQ(stale.reason, SessionFenceReason::StaleEventSequence);
	EXPECT_EQ(stale.after.lastEventSequence, 10U);
	EXPECT_EQ(stale.after.persistenceRevision, 0U);

	const auto duplicate = fence.persist({ 10, owner(1, firstWriter), 1 });
	EXPECT_EQ(duplicate.disposition, SessionFenceDisposition::RejectedDuplicateEvent);
	EXPECT_EQ(duplicate.reason, SessionFenceReason::DuplicateEventSequence);
	EXPECT_EQ(duplicate.after.lastEventSequence, 10U);
	EXPECT_EQ(duplicate.after.persistenceRevision, 0U);

	const auto fresh = fence.persist({ 11, owner(1, firstWriter), 1 });
	EXPECT_TRUE(fresh.persistenceAuthorized());
	EXPECT_EQ(fresh.after.lastEventSequence, 11U);
}

TEST(SessionRevisionFenceTest, MalformedAndWrongSubjectEventsFailClosedWithoutConsumingSequence) {
	SessionRevisionFence fence(subjectId);

	const auto malformed = fence.acquire({ 100, subjectId, 0, firstWriter });
	EXPECT_EQ(malformed.disposition, SessionFenceDisposition::RejectedMalformed);
	EXPECT_EQ(malformed.reason, SessionFenceReason::MalformedContext);
	EXPECT_EQ(malformed.after.lastEventSequence, 0U);
	EXPECT_EQ(malformed.after.transitionCount, 0U);

	const auto wrongSubject = fence.acquire({ 100, subjectId + 1, 1, firstWriter });
	EXPECT_EQ(wrongSubject.disposition, SessionFenceDisposition::RejectedSubject);
	EXPECT_EQ(wrongSubject.reason, SessionFenceReason::SubjectMismatch);
	EXPECT_EQ(wrongSubject.after.lastEventSequence, 0U);

	const auto valid = fence.acquire(acquisition(1, 1, firstWriter));
	EXPECT_EQ(valid.disposition, SessionFenceDisposition::Applied);
	EXPECT_EQ(valid.after.lastEventSequence, 1U);

	const auto zeroRevision = fence.persist({ 2, owner(1, firstWriter), 0 });
	EXPECT_EQ(zeroRevision.disposition, SessionFenceDisposition::RejectedMalformed);
	EXPECT_EQ(zeroRevision.after.lastEventSequence, 1U);
	EXPECT_EQ(zeroRevision.after.persistenceRevision, 0U);
}

TEST(SessionRevisionFenceTest, EventResultsRetainImmutableBeforeAndAfterSnapshots) {
	SessionRevisionFence fence(subjectId);
	const auto acquisitionResult = fence.acquire(acquisition(1, 1, firstWriter));
	ASSERT_EQ(acquisitionResult.after.status, SessionFenceStatus::Owned);
	ASSERT_EQ(acquisitionResult.after.persistenceRevision, 0U);

	ASSERT_TRUE(fence.persist({ 2, owner(1, firstWriter), 1 }).persistenceAuthorized());
	ASSERT_EQ(fence.transfer({ 3, owner(1, firstWriter), 2, secondWriter }).disposition, SessionFenceDisposition::Applied);

	EXPECT_EQ(acquisitionResult.before.status, SessionFenceStatus::Vacant);
	EXPECT_EQ(acquisitionResult.before.ownershipGeneration, 0U);
	EXPECT_EQ(acquisitionResult.after.status, SessionFenceStatus::Owned);
	EXPECT_EQ(acquisitionResult.after.ownershipGeneration, 1U);
	EXPECT_EQ(acquisitionResult.after.authorizedWriterToken, firstWriter);
	EXPECT_EQ(acquisitionResult.after.persistenceRevision, 0U);
	EXPECT_EQ(acquisitionResult.after.transitionCount, 1U);

	const auto current = fence.snapshot();
	EXPECT_EQ(current.ownershipGeneration, 2U);
	EXPECT_EQ(current.authorizedWriterToken, secondWriter);
	EXPECT_EQ(current.persistenceRevision, 1U);
	EXPECT_EQ(current.transitionCount, 3U);
}

TEST(SessionRevisionFenceTest, TransitionCounterChangesOnlyForEffectiveStateChanges) {
	SessionRevisionFence fence(subjectId);
	ASSERT_EQ(fence.acquire(acquisition(1, 1, firstWriter)).after.transitionCount, 1U);

	EXPECT_EQ(fence.acquire(acquisition(2, 1, firstWriter)).after.transitionCount, 1U);
	EXPECT_EQ(fence.persist({ 3, owner(1, firstWriter), 2 }).after.transitionCount, 1U);
	EXPECT_EQ(fence.release({ 4, owner(1, secondWriter) }).after.transitionCount, 1U);

	EXPECT_EQ(fence.persist({ 5, owner(1, firstWriter), 1 }).after.transitionCount, 2U);
	EXPECT_EQ(fence.release({ 6, owner(1, firstWriter) }).after.transitionCount, 3U);
	EXPECT_EQ(fence.acquire(acquisition(7, 2, secondWriter)).after.transitionCount, 4U);
}

TEST(SessionRevisionFenceTest, ConcurrentDuplicateAcquisitionProducesAtMostOneEffectiveTransition) {
	SessionRevisionFence fence(subjectId);
	constexpr uint32_t threadCount = 16;
	std::atomic<uint32_t> applied = 0;
	std::atomic<uint32_t> duplicates = 0;
	std::vector<std::thread> workers;
	workers.reserve(threadCount);

	for (uint32_t index = 0; index < threadCount; ++index) {
		workers.emplace_back([&] {
			const auto result = fence.acquire(acquisition(1, 1, firstWriter));
			if (result.disposition == SessionFenceDisposition::Applied) {
				++applied;
			} else if (result.disposition == SessionFenceDisposition::RejectedDuplicateEvent) {
				++duplicates;
			}
		});
	}
	for (auto &worker : workers) {
		worker.join();
	}

	EXPECT_EQ(applied.load(), 1U);
	EXPECT_EQ(duplicates.load(), threadCount - 1);
	EXPECT_EQ(fence.snapshot().status, SessionFenceStatus::Owned);
	EXPECT_EQ(fence.snapshot().transitionCount, 1U);
}

TEST(SessionRevisionFenceTest, ConcurrentDuplicateTransferProducesAtMostOneEffectiveHandoff) {
	SessionRevisionFence fence(subjectId);
	ASSERT_EQ(fence.acquire(acquisition(1, 1, firstWriter)).disposition, SessionFenceDisposition::Applied);

	constexpr uint32_t threadCount = 16;
	std::atomic<uint32_t> applied = 0;
	std::atomic<uint32_t> duplicates = 0;
	std::vector<std::thread> workers;
	workers.reserve(threadCount);

	for (uint32_t index = 0; index < threadCount; ++index) {
		workers.emplace_back([&] {
			const auto result = fence.transfer({ 2, owner(1, firstWriter), 2, secondWriter });
			if (result.disposition == SessionFenceDisposition::Applied) {
				++applied;
			} else if (result.disposition == SessionFenceDisposition::RejectedDuplicateEvent) {
				++duplicates;
			}
		});
	}
	for (auto &worker : workers) {
		worker.join();
	}

	EXPECT_EQ(applied.load(), 1U);
	EXPECT_EQ(duplicates.load(), threadCount - 1);
	const auto snapshot = fence.snapshot();
	EXPECT_EQ(snapshot.status, SessionFenceStatus::Owned);
	EXPECT_EQ(snapshot.ownershipGeneration, 2U);
	EXPECT_EQ(snapshot.authorizedWriterToken, secondWriter);
	EXPECT_EQ(snapshot.transitionCount, 2U);
	EXPECT_FALSE(fence.mayPersist(owner(1, firstWriter), 1).authorized());
	EXPECT_TRUE(fence.mayPersist(owner(2, secondWriter), 1).authorized());
}
