#include <gtest/gtest.h>

#include "database/database_failure_classification.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <atomic>
	#include <chrono>
	#include <cstdint>
	#include <fstream>
	#include <memory>
	#include <sstream>
	#include <string>
	#include <string_view>
	#include <thread>
	#include <vector>
#endif

using namespace std::chrono_literals;

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(PRS003B_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}

	std::string_view functionBody(const std::string &source, std::string_view begin, std::string_view end) {
		const auto beginPosition = source.find(begin);
		EXPECT_NE(beginPosition, std::string::npos) << begin;
		if (beginPosition == std::string::npos) {
			return {};
		}

		const auto endPosition = source.find(end, beginPosition + begin.size());
		EXPECT_NE(endPosition, std::string::npos) << end;
		if (endPosition == std::string::npos) {
			return {};
		}

		return std::string_view(source).substr(beginPosition, endPosition - beginPosition);
	}

	size_t countOccurrences(std::string_view source, std::string_view needle) {
		size_t count = 0;
		size_t position = 0;
		while ((position = source.find(needle, position)) != std::string_view::npos) {
			++count;
			position += needle.size();
		}
		return count;
	}
}

TEST(DatabaseFailureClassificationTest, KnownNotCommittedFailurePublishesFixedEvent) {
	const auto classification = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::Query,
		false,
		DatabaseNativeErrorKind::Other
	);
	ASSERT_EQ(classification.result, DatabaseRuntimeResultKind::FailureKnownNotCommitted);
	ASSERT_EQ(classification.failureReason, DatabaseOutageFailureReason::QueryFailed);
	ASSERT_EQ(classification.commitOutcome, DatabaseOutageCommitOutcome::KnownNotCommitted);

	DatabaseOutageStateMachine state({ 100ms, 50ms });
	DatabaseOutageEventPublisher publisher(state);
	const auto publication = publisher.publish(classification, 100ms);

	ASSERT_EQ(publication.disposition, DatabaseOutagePublicationDisposition::Published);
	ASSERT_TRUE(publication.event.has_value());
	EXPECT_EQ(publication.event->eventSequence, 1U);
	EXPECT_EQ(publication.event->eventTime, 100ms);
	EXPECT_EQ(publication.event->disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(publication.event->reason, DatabaseOutageEventReason::FirstRuntimeFailure);
	EXPECT_EQ(publication.event->after.state, DatabaseOutageState::Degraded);
	EXPECT_EQ(publication.event->after.lastFailureReason, DatabaseOutageFailureReason::QueryFailed);
	EXPECT_EQ(publication.event->after.lastFailureOutcome, DatabaseOutageCommitOutcome::KnownNotCommitted);
}

TEST(DatabaseFailureClassificationTest, UnknownCommitOutcomePublishesDirectDrainEvent) {
	const auto classification = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::TransactionCommit,
		false,
		DatabaseNativeErrorKind::ConnectionLost
	);
	ASSERT_EQ(classification.result, DatabaseRuntimeResultKind::FailureUnknownCommitOutcome);
	ASSERT_EQ(classification.failureReason, DatabaseOutageFailureReason::TransactionCommitFailed);
	ASSERT_EQ(classification.commitOutcome, DatabaseOutageCommitOutcome::Unknown);

	DatabaseOutageStateMachine state({ 100ms, 50ms });
	DatabaseOutageEventPublisher publisher(state);
	const auto publication = publisher.publish(classification, 200ms);

	ASSERT_TRUE(publication.event.has_value());
	EXPECT_EQ(publication.event->reason, DatabaseOutageEventReason::UnknownCommitOutcome);
	EXPECT_EQ(publication.event->after.state, DatabaseOutageState::Draining);
	EXPECT_EQ(publication.event->after.lastFailureReason, DatabaseOutageFailureReason::TransactionCommitFailed);
	EXPECT_EQ(publication.event->after.lastFailureOutcome, DatabaseOutageCommitOutcome::Unknown);
}

TEST(DatabaseFailureClassificationTest, ClassifiesOperationBoundariesConservatively) {
	const auto beginFailure = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::TransactionBegin,
		false,
		DatabaseNativeErrorKind::ConnectionLost
	);
	EXPECT_EQ(beginFailure.result, DatabaseRuntimeResultKind::FailureKnownNotCommitted);
	EXPECT_EQ(beginFailure.failureReason, DatabaseOutageFailureReason::TransactionBeginFailed);
	EXPECT_EQ(beginFailure.commitOutcome, DatabaseOutageCommitOutcome::KnownNotCommitted);

	const auto queryConnectionLoss = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::StoreQuery,
		false,
		DatabaseNativeErrorKind::ServerGone
	);
	EXPECT_EQ(queryConnectionLoss.result, DatabaseRuntimeResultKind::FailureUnknownCommitOutcome);
	EXPECT_EQ(queryConnectionLoss.failureReason, DatabaseOutageFailureReason::ServerGone);
	EXPECT_EQ(queryConnectionLoss.commitOutcome, DatabaseOutageCommitOutcome::Unknown);

	const auto rollbackFailure = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::TransactionRollback,
		false,
		DatabaseNativeErrorKind::Other
	);
	EXPECT_EQ(rollbackFailure.result, DatabaseRuntimeResultKind::FailureUnknownCommitOutcome);
	EXPECT_EQ(rollbackFailure.failureReason, DatabaseOutageFailureReason::QueryFailed);
	EXPECT_EQ(rollbackFailure.commitOutcome, DatabaseOutageCommitOutcome::Unknown);
}

TEST(DatabaseFailureClassificationTest, PublicationPreservesCallerVisibleFailureResults) {
	const auto classification = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::Query,
		false,
		DatabaseNativeErrorKind::Other
	);

	DatabaseOutageStateMachine boolState({ 100ms, 50ms });
	DatabaseOutageEventPublisher boolPublisher(boolState);
	EXPECT_FALSE(boolPublisher.publishAndPreserve(false, classification, 100ms));
	EXPECT_EQ(boolState.snapshot().state, DatabaseOutageState::Degraded);

	DatabaseOutageStateMachine pointerState({ 100ms, 50ms });
	DatabaseOutageEventPublisher pointerPublisher(pointerState);
	std::shared_ptr<int> callerResult;
	const auto preserved = pointerPublisher.publishAndPreserve(callerResult, classification, 100ms);
	EXPECT_EQ(preserved, nullptr);
	EXPECT_EQ(pointerState.snapshot().state, DatabaseOutageState::Degraded);
}

TEST(DatabaseFailureClassificationTest, SuccessAndSuccessfulEmptyResultPublishNoFailure) {
	const auto success = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::StoreQuery,
		true,
		DatabaseNativeErrorKind::Other
	);
	ASSERT_TRUE(success.succeeded());
	EXPECT_FALSE(success.failureReason.has_value());
	EXPECT_FALSE(success.commitOutcome.has_value());

	DatabaseOutageStateMachine state({ 100ms, 50ms });
	DatabaseOutageEventPublisher publisher(state);
	const auto publication = publisher.publish(success, 100ms);
	EXPECT_EQ(publication.disposition, DatabaseOutagePublicationDisposition::NotPublishedSuccess);
	EXPECT_FALSE(publication.event.has_value());

	std::shared_ptr<int> emptyResult;
	EXPECT_EQ(publisher.publishAndPreserve(emptyResult, success, 100ms), nullptr);
	const auto snapshot = state.snapshot();
	EXPECT_EQ(snapshot.state, DatabaseOutageState::Healthy);
	EXPECT_EQ(snapshot.transitionCount, 0U);
	EXPECT_EQ(snapshot.lastEventSequence, 0U);
	EXPECT_FALSE(snapshot.lastEventTime.has_value());
}

TEST(DatabaseFailureClassificationTest, DuplicateStaleAndRegressingEventsCannotTransitionTwice) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	DatabaseOutageEventPublisher publisher(state);
	const auto classification = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::Query,
		false,
		DatabaseNativeErrorKind::Other
	);
	const DatabaseRuntimeOutageEvent event {
		.sequence = 5,
		.time = 100ms,
		.classification = classification,
	};

	const auto first = publisher.publish(event);
	ASSERT_TRUE(first.event.has_value());
	EXPECT_EQ(first.event->disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(first.event->after.transitionCount, 1U);

	const auto duplicate = publisher.publish(event);
	ASSERT_TRUE(duplicate.event.has_value());
	EXPECT_EQ(duplicate.event->disposition, DatabaseOutageEventDisposition::RejectedStaleOrDuplicate);
	EXPECT_EQ(duplicate.event->after.transitionCount, 1U);

	const auto stale = publisher.publish(DatabaseRuntimeOutageEvent {
		.sequence = 4,
		.time = 110ms,
		.classification = classification,
	});
	ASSERT_TRUE(stale.event.has_value());
	EXPECT_EQ(stale.event->disposition, DatabaseOutageEventDisposition::RejectedStaleOrDuplicate);
	EXPECT_EQ(stale.event->after.transitionCount, 1U);

	const auto regressing = publisher.publish(DatabaseRuntimeOutageEvent {
		.sequence = 6,
		.time = 99ms,
		.classification = classification,
	});
	ASSERT_TRUE(regressing.event.has_value());
	EXPECT_EQ(regressing.event->disposition, DatabaseOutageEventDisposition::RejectedStaleOrDuplicate);
	EXPECT_EQ(regressing.event->after.transitionCount, 1U);
	EXPECT_EQ(state.snapshot().state, DatabaseOutageState::Degraded);
}

TEST(DatabaseFailureClassificationTest, SerializedControlEventsAdvanceOneMonotonicSequence) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	DatabaseOutageEventPublisher publisher(state);
	const auto classification = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::Query,
		false,
		DatabaseNativeErrorKind::Other
	);

	const auto failure = publisher.publish(classification, 100ms);
	ASSERT_TRUE(failure.event.has_value());
	ASSERT_EQ(failure.event->eventSequence, 1U);
	ASSERT_EQ(failure.event->after.state, DatabaseOutageState::Degraded);

	const auto degradedExpired = publisher.degradedDeadlineExpired(200ms);
	EXPECT_EQ(degradedExpired.eventSequence, 2U);
	EXPECT_EQ(degradedExpired.eventTime, 200ms);
	EXPECT_EQ(degradedExpired.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(degradedExpired.reason, DatabaseOutageEventReason::DegradedDeadlineExpired);
	EXPECT_EQ(degradedExpired.after.state, DatabaseOutageState::Draining);
	ASSERT_TRUE(degradedExpired.after.drainDeadline.has_value());

	const auto drainExpired = publisher.drainDeadlineExpired(*degradedExpired.after.drainDeadline);
	EXPECT_EQ(drainExpired.eventSequence, 3U);
	EXPECT_EQ(drainExpired.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(drainExpired.reason, DatabaseOutageEventReason::DrainDeadlineExpired);
	EXPECT_EQ(drainExpired.after.state, DatabaseOutageState::Maintenance);
	EXPECT_EQ(state.snapshot().lastEventSequence, 3U);
}

TEST(DatabaseFailureClassificationTest, ControlEventsClampRegressingCallerTime) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	DatabaseOutageEventPublisher publisher(state);
	const auto publication = publisher.publish(
		classifyDatabaseRuntimeResult(DatabaseRuntimeOperation::Query, false, DatabaseNativeErrorKind::Other),
		100ms
	);
	ASSERT_TRUE(publication.event.has_value());

	const auto earlyControl = publisher.degradedDeadlineExpired(50ms);
	EXPECT_EQ(earlyControl.eventSequence, 2U);
	EXPECT_EQ(earlyControl.eventTime, 100ms);
	EXPECT_EQ(earlyControl.disposition, DatabaseOutageEventDisposition::RejectedPrecondition);
	EXPECT_EQ(earlyControl.after.state, DatabaseOutageState::Degraded);
	EXPECT_EQ(state.snapshot().lastEventSequence, 2U);
}

TEST(DatabaseFailureClassificationTest, DrainCompletionIsDistinctFromDeadlineExpiry) {
	DatabaseOutageStateMachine completionState({ 100ms, 50ms });
	DatabaseOutageEventPublisher completionPublisher(completionState);
	const auto directDrain = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::TransactionCommit,
		false,
		DatabaseNativeErrorKind::ConnectionLost
	);
	ASSERT_TRUE(completionPublisher.publish(directDrain, 10ms).event.has_value());
	const auto completed = completionPublisher.drainCompleted(20ms);
	EXPECT_EQ(completed.reason, DatabaseOutageEventReason::DrainCompleted);
	EXPECT_EQ(completed.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(completed.after.state, DatabaseOutageState::Maintenance);

	DatabaseOutageStateMachine expiryState({ 100ms, 50ms });
	DatabaseOutageEventPublisher expiryPublisher(expiryState);
	const auto drainPublication = expiryPublisher.publish(directDrain, 10ms);
	ASSERT_TRUE(drainPublication.event.has_value());
	ASSERT_TRUE(drainPublication.event->after.drainDeadline.has_value());
	const auto expired = expiryPublisher.drainDeadlineExpired(*drainPublication.event->after.drainDeadline);
	EXPECT_EQ(expired.reason, DatabaseOutageEventReason::DrainDeadlineExpired);
	EXPECT_EQ(expired.disposition, DatabaseOutageEventDisposition::Applied);
	EXPECT_EQ(expired.after.state, DatabaseOutageState::Maintenance);
}

TEST(DatabaseFailureClassificationTest, ClassificationDoesNotParseHumanReadableErrors) {
	const auto classification = classifyDatabaseRuntimeResult(
		DatabaseRuntimeOperation::Query,
		false,
		DatabaseNativeErrorKind::ConnectionLost
	);
	EXPECT_EQ(classification.failureReason, DatabaseOutageFailureReason::ConnectionLost);
	EXPECT_EQ(classification.commitOutcome, DatabaseOutageCommitOutcome::Unknown);

	const auto source = readSource("src/database/database.cpp");
	const auto classifier = functionBody(source, "DatabaseNativeErrorKind classifyDatabaseNativeError", "void publishDatabaseRuntimeResult");
	EXPECT_NE(classifier.find("CR_SERVER_LOST"), std::string_view::npos);
	EXPECT_NE(classifier.find("CR_SERVER_GONE_ERROR"), std::string_view::npos);
	EXPECT_EQ(classifier.find("mysql_error"), std::string_view::npos);
	EXPECT_EQ(classifier.find("mysql_sqlstate"), std::string_view::npos);
}

TEST(DatabaseFailureClassificationTest, PublicationAddsNoReconnectReplayOrRetryLoop) {
	const auto source = readSource("src/database/database.cpp");
	const auto retryQuery = functionBody(source, "bool Database::retryQuery", "bool Database::executeQuery");
	EXPECT_EQ(countOccurrences(retryQuery, "mysql_query(handle, query.data())"), 1U);
	EXPECT_NE(retryQuery.find("(void)retries;"), std::string_view::npos);
	EXPECT_EQ(retryQuery.find("connect("), std::string_view::npos);
	EXPECT_EQ(retryQuery.find("mysql_ping"), std::string_view::npos);
	EXPECT_EQ(retryQuery.find("while ("), std::string_view::npos);
	EXPECT_EQ(retryQuery.find("for ("), std::string_view::npos);

	const auto publisher = functionBody(source, "void publishDatabaseRuntimeResult", "bool executeRuntimeQueryOnce");
	EXPECT_EQ(publisher.find("mysql_query"), std::string_view::npos);
	EXPECT_EQ(publisher.find("connect("), std::string_view::npos);
	EXPECT_EQ(publisher.find("mysql_ping"), std::string_view::npos);
}

TEST(DatabaseFailureClassificationTest, RuntimeControlWrappersDelegateWithoutDatabaseWork) {
	const auto source = readSource("src/database/database.cpp");
	const auto wrappers = functionBody(
		source,
		"DatabaseOutageEventResult publishDatabaseOutageDegradedDeadlineExpired",
		"Database::~Database"
	);
	EXPECT_EQ(countOccurrences(wrappers, "degradedDeadlineExpired(now)"), 1U);
	EXPECT_EQ(countOccurrences(wrappers, "drainCompleted(now)"), 1U);
	EXPECT_EQ(countOccurrences(wrappers, "drainDeadlineExpired(now)"), 1U);
	EXPECT_EQ(wrappers.find("mysql_"), std::string_view::npos);
	EXPECT_EQ(wrappers.find("connect("), std::string_view::npos);
	EXPECT_EQ(wrappers.find("while ("), std::string_view::npos);
	EXPECT_EQ(wrappers.find("for ("), std::string_view::npos);
}

TEST(DatabaseFailureClassificationTest, ConcurrentDuplicatePublicationIsSerialized) {
	DatabaseOutageStateMachine state({ 100ms, 50ms });
	DatabaseOutageEventPublisher publisher(state);
	const DatabaseRuntimeOutageEvent event {
		.sequence = 1,
		.time = 100ms,
		.classification = classifyDatabaseRuntimeResult(
			DatabaseRuntimeOperation::Query,
			false,
			DatabaseNativeErrorKind::Other
		),
	};

	constexpr uint32_t threadCount = 16;
	std::atomic<uint32_t> applied = 0;
	std::atomic<uint32_t> stale = 0;
	std::atomic<uint32_t> missing = 0;
	std::vector<std::thread> workers;
	workers.reserve(threadCount);
	for (uint32_t threadIndex = 0; threadIndex < threadCount; ++threadIndex) {
		workers.emplace_back([&publisher, &event, &applied, &stale, &missing] {
			const auto publication = publisher.publish(event);
			if (!publication.event.has_value()) {
				missing.fetch_add(1, std::memory_order_relaxed);
				return;
			}
			if (publication.event->disposition == DatabaseOutageEventDisposition::Applied) {
				applied.fetch_add(1, std::memory_order_relaxed);
			} else if (publication.event->disposition == DatabaseOutageEventDisposition::RejectedStaleOrDuplicate) {
				stale.fetch_add(1, std::memory_order_relaxed);
			}
		});
	}
	for (auto &worker : workers) {
		worker.join();
	}

	EXPECT_EQ(missing.load(std::memory_order_relaxed), 0U);
	EXPECT_EQ(applied.load(std::memory_order_relaxed), 1U);
	EXPECT_EQ(stale.load(std::memory_order_relaxed), threadCount - 1);
	const auto snapshot = state.snapshot();
	EXPECT_EQ(snapshot.state, DatabaseOutageState::Degraded);
	EXPECT_EQ(snapshot.transitionCount, 1U);
	EXPECT_EQ(snapshot.lastEventSequence, 1U);
}
