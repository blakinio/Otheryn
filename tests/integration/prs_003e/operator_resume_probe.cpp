#include "database/database_outage_operator_control.hpp"

#include <atomic>
#include <chrono>
#include <iostream>
#include <stdexcept>
#include <string_view>
#include <thread>

using namespace std::chrono_literals;

namespace {
	void require(bool condition, std::string_view message) {
		if (!condition) {
			throw std::runtime_error(std::string(message));
		}
	}

	DatabaseOutageOperatorResumeRequest requestFor(
		const DatabaseOutageSnapshot &snapshot,
		DatabaseOutageEventSequence eventSequence,
		DatabaseOutageTimePoint eventTime
	) {
		return DatabaseOutageOperatorResumeRequest {
			.authorized = true,
			.explicitlyConfirmed = true,
			.expectedState = snapshot.state,
			.expectedTransitionCount = snapshot.transitionCount,
			.expectedLastEventSequence = snapshot.lastEventSequence,
			.eventSequence = eventSequence,
			.eventTime = eventTime,
		};
	}

	void proveReadOnlyStatusAndRejectedRequests() {
		DatabaseOutageStateMachine owner({ 10ms, 10ms });
		DatabaseOutageOperatorControl control(owner);

		const auto initial = control.status();
		const auto repeated = control.status();
		require(initial.state == DatabaseOutageState::Healthy, "initial status must be healthy");
		require(initial.transitionCount == repeated.transitionCount, "status inspection must not transition state");
		require(initial.lastEventSequence == repeated.lastEventSequence, "status inspection must not consume an event sequence");

		auto healthyRequest = requestFor(initial, 1, 1ms);
		const auto unavailable = control.resume(healthyRequest);
		require(unavailable.disposition == DatabaseOutageOperatorResumeDisposition::RejectedUnavailableState, "healthy state must reject operator resume");
		require(unavailable.action == DatabaseOutageOperatorAction::None, "rejected request must not emit lifecycle action");
		require(control.status().lastEventSequence == 0, "precondition rejection must not consume state-owner sequence");

		(void)owner.runtimeFailure(
			1,
			DatabaseOutageFailureReason::QueryFailed,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			100ms
		);
		const auto degraded = control.status();
		require(degraded.state == DatabaseOutageState::Degraded, "known-not-committed failure must enter degraded");
		require(!degraded.recoveryEvidenceAccepted, "ordinary runtime state must not imply recovery evidence");

		auto unauthorizedRequest = requestFor(degraded, 2, 101ms);
		unauthorizedRequest.authorized = false;
		const auto unauthorized = control.resume(unauthorizedRequest);
		require(unauthorized.disposition == DatabaseOutageOperatorResumeDisposition::RejectedUnauthorized, "unauthorized request must reject");
		require(control.status().lastEventSequence == degraded.lastEventSequence, "unauthorized request must not consume sequence");

		auto unconfirmedRequest = requestFor(degraded, 2, 101ms);
		unconfirmedRequest.explicitlyConfirmed = false;
		const auto unconfirmed = control.resume(unconfirmedRequest);
		require(unconfirmed.disposition == DatabaseOutageOperatorResumeDisposition::RejectedUnconfirmed, "unconfirmed request must reject");

		auto wrongStateRequest = requestFor(degraded, 2, 101ms);
		wrongStateRequest.expectedState = DatabaseOutageState::Maintenance;
		require(
			control.resume(wrongStateRequest).disposition == DatabaseOutageOperatorResumeDisposition::RejectedStateMismatch,
			"wrong expected state must reject"
		);

		auto wrongTransitionRequest = requestFor(degraded, 2, 101ms);
		++wrongTransitionRequest.expectedTransitionCount;
		require(
			control.resume(wrongTransitionRequest).disposition == DatabaseOutageOperatorResumeDisposition::RejectedTransitionMismatch,
			"wrong transition generation must reject"
		);

		auto wrongSequenceRequest = requestFor(degraded, 2, 101ms);
		++wrongSequenceRequest.expectedLastEventSequence;
		require(
			control.resume(wrongSequenceRequest).disposition == DatabaseOutageOperatorResumeDisposition::RejectedSequenceMismatch,
			"wrong observed event sequence must reject"
		);

		auto staleRequest = requestFor(degraded, degraded.lastEventSequence, 101ms);
		require(
			control.resume(staleRequest).disposition == DatabaseOutageOperatorResumeDisposition::RejectedStaleOrDuplicate,
			"duplicate event sequence must reject"
		);

		const auto missingEvidence = control.resume(requestFor(degraded, 2, 101ms));
		require(missingEvidence.disposition == DatabaseOutageOperatorResumeDisposition::RejectedRecoveryEvidence, "one ordinary successful path must be insufficient");
		require(!missingEvidence.event.has_value(), "missing-evidence rejection must not call the state owner");
	}

	void proveDegradedResumeAndIntervalClearing() {
		DatabaseOutageStateMachine owner({ 10ms, 10ms });
		DatabaseOutageOperatorControl control(owner);

		(void)owner.runtimeFailure(
			1,
			DatabaseOutageFailureReason::ConnectionLost,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			100ms
		);
		(void)owner.recoveryEvidenceAccepted(2, 101ms);
		const auto eligible = control.status();
		require(eligible.state == DatabaseOutageState::Degraded, "evidence must not auto-resume degraded state");
		require(eligible.recoveryEvidenceAccepted, "accepted evidence must be visible to operator status");

		const auto applied = control.resume(requestFor(eligible, 3, 102ms));
		require(applied.applied(), "explicit degraded resume must apply");
		require(applied.action == DatabaseOutageOperatorAction::ResumeGameLifecycle, "applied policy resume must emit lifecycle action");
		require(applied.event.has_value(), "applied policy resume must expose state-owner event");
		require(applied.event->reason == DatabaseOutageEventReason::OperatorResume, "applied event must use operator-resume reason");
		require(applied.after.state == DatabaseOutageState::Healthy, "final owner snapshot must be healthy");
		require(!applied.after.firstFailureTime.has_value(), "successful resume must clear first failure time");
		require(!applied.after.degradedDeadline.has_value(), "successful resume must clear degraded deadline");
		require(!applied.after.drainDeadline.has_value(), "successful resume must clear drain deadline");
		require(!applied.after.lastFailureReason.has_value(), "successful resume must clear failure reason");
		require(!applied.after.lastFailureOutcome.has_value(), "successful resume must clear failure outcome");
		require(!applied.after.recoveryEvidenceAccepted, "successful resume must consume accepted evidence");

		const auto duplicate = control.resume(requestFor(eligible, 3, 102ms));
		require(!duplicate.applied(), "duplicate explicit request must not apply twice");
		require(duplicate.action == DatabaseOutageOperatorAction::None, "duplicate request must not emit a second lifecycle action");
	}

	void proveMaintenanceResumeAndFailureInvalidation() {
		DatabaseOutageStateMachine maintenanceOwner({ 10ms, 10ms });
		DatabaseOutageOperatorControl maintenanceControl(maintenanceOwner);
		(void)maintenanceOwner.runtimeFailure(
			1,
			DatabaseOutageFailureReason::TransactionCommitFailed,
			DatabaseOutageCommitOutcome::Unknown,
			200ms
		);
		(void)maintenanceOwner.drainCompleted(2, 201ms);
		(void)maintenanceOwner.recoveryEvidenceAccepted(3, 202ms);
		const auto maintenance = maintenanceControl.status();
		require(maintenance.state == DatabaseOutageState::Maintenance, "drain completion must enter maintenance");
		require(maintenance.recoveryEvidenceAccepted, "maintenance evidence must be accepted without auto-resume");
		const auto resumed = maintenanceControl.resume(requestFor(maintenance, 4, 203ms));
		require(resumed.applied(), "explicit maintenance resume must apply after evidence");
		require(resumed.after.state == DatabaseOutageState::Healthy, "maintenance resume must finish healthy");

		DatabaseOutageStateMachine invalidatedOwner({ 10ms, 10ms });
		DatabaseOutageOperatorControl invalidatedControl(invalidatedOwner);
		(void)invalidatedOwner.runtimeFailure(
			1,
			DatabaseOutageFailureReason::ServerGone,
			DatabaseOutageCommitOutcome::Unknown,
			300ms
		);
		(void)invalidatedOwner.drainCompleted(2, 301ms);
		(void)invalidatedOwner.recoveryEvidenceAccepted(3, 302ms);
		(void)invalidatedOwner.runtimeFailure(
			4,
			DatabaseOutageFailureReason::RecoveryProbeFailed,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			303ms
		);
		const auto invalidated = invalidatedControl.status();
		require(invalidated.state == DatabaseOutageState::Maintenance, "later maintenance failure must preserve maintenance state");
		require(!invalidated.recoveryEvidenceAccepted, "later qualifying failure must invalidate evidence");
		const auto rejected = invalidatedControl.resume(requestFor(invalidated, 5, 304ms));
		require(rejected.disposition == DatabaseOutageOperatorResumeDisposition::RejectedRecoveryEvidence, "invalidated evidence must block explicit resume");
		require(rejected.action == DatabaseOutageOperatorAction::None, "invalidated evidence must not emit lifecycle action");
	}

	void proveConcurrentExactOnceResume() {
		DatabaseOutageStateMachine owner({ 10ms, 10ms });
		DatabaseOutageOperatorControl control(owner);
		(void)owner.runtimeFailure(
			1,
			DatabaseOutageFailureReason::QueryFailed,
			DatabaseOutageCommitOutcome::KnownNotCommitted,
			400ms
		);
		(void)owner.recoveryEvidenceAccepted(2, 401ms);
		const auto eligible = control.status();

		const auto requestA = requestFor(eligible, 3, 402ms);
		const auto requestB = requestFor(eligible, 4, 403ms);
		DatabaseOutageOperatorResumeResult resultA;
		DatabaseOutageOperatorResumeResult resultB;
		std::atomic<bool> start { false };

		std::thread threadA([&] {
			while (!start.load(std::memory_order_acquire)) {
				std::this_thread::yield();
			}
			resultA = control.resume(requestA);
		});
		std::thread threadB([&] {
			while (!start.load(std::memory_order_acquire)) {
				std::this_thread::yield();
			}
			resultB = control.resume(requestB);
		});

		start.store(true, std::memory_order_release);
		threadA.join();
		threadB.join();

		const int appliedCount = static_cast<int>(resultA.applied()) + static_cast<int>(resultB.applied());
		const int lifecycleActionCount = static_cast<int>(resultA.action == DatabaseOutageOperatorAction::ResumeGameLifecycle)
			+ static_cast<int>(resultB.action == DatabaseOutageOperatorAction::ResumeGameLifecycle);
		require(appliedCount == 1, "concurrent explicit requests must produce exactly one applied resume");
		require(lifecycleActionCount == 1, "concurrent explicit requests must emit exactly one lifecycle action");
		require(control.status().state == DatabaseOutageState::Healthy, "concurrent resume must finish healthy");
	}
}

int main() {
	try {
		proveReadOnlyStatusAndRejectedRequests();
		proveDegradedResumeAndIntervalClearing();
		proveMaintenanceResumeAndFailureInvalidation();
		proveConcurrentExactOnceResume();
		std::cout << "PRS-003E-C operator resume evidence: PASS\n";
		return 0;
	} catch (const std::exception &error) {
		std::cerr << "PRS-003E-C operator resume evidence: FAIL: " << error.what() << '\n';
		return 1;
	}
}
