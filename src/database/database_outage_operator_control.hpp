#pragma once

#include "database/database_outage_state.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <optional>
#endif

enum class DatabaseOutageOperatorResumeDisposition : uint8_t {
	Observed,
	Applied,
	RejectedUnauthorized,
	RejectedUnconfirmed,
	RejectedStaleOrDuplicate,
	RejectedStateMismatch,
	RejectedTransitionMismatch,
	RejectedSequenceMismatch,
	RejectedUnavailableState,
	RejectedRecoveryEvidence,
	RejectedStateOwner,
};

enum class DatabaseOutageOperatorAction : uint8_t {
	None,
	ResumeGameLifecycle,
};

struct DatabaseOutageOperatorResumeRequest final {
	bool authorized = false;
	bool explicitlyConfirmed = false;
	DatabaseOutageState expectedState = DatabaseOutageState::Healthy;
	uint64_t expectedTransitionCount = 0;
	DatabaseOutageEventSequence expectedLastEventSequence = 0;
	DatabaseOutageEventSequence eventSequence = 0;
	DatabaseOutageTimePoint eventTime { 0 };
};

struct DatabaseOutageOperatorResumeResult final {
	DatabaseOutageOperatorResumeDisposition disposition = DatabaseOutageOperatorResumeDisposition::Observed;
	DatabaseOutageOperatorAction action = DatabaseOutageOperatorAction::None;
	DatabaseOutageSnapshot before;
	std::optional<DatabaseOutageEventResult> event;
	DatabaseOutageSnapshot after;

	[[nodiscard]] bool applied() const noexcept {
		return disposition == DatabaseOutageOperatorResumeDisposition::Applied;
	}
};

/**
 * Typed explicit operator boundary for PRS-003 recovery.
 *
 * The controller owns no clock, thread, scheduler, transport, permission store,
 * database connection or game lifecycle. Callers authenticate the operator,
 * obtain one immutable status snapshot, explicitly confirm the action and
 * supply the exact observed generation plus a new monotonic event sequence and
 * time. Only an applied policy transition emits ResumeGameLifecycle for the
 * caller to handle through the existing lifecycle owner.
 */
class DatabaseOutageOperatorControl final {
public:
	explicit DatabaseOutageOperatorControl(DatabaseOutageStateMachine &stateOwner) noexcept :
		stateOwner_(stateOwner) { }

	DatabaseOutageOperatorControl(const DatabaseOutageOperatorControl &) = delete;
	DatabaseOutageOperatorControl &operator=(const DatabaseOutageOperatorControl &) = delete;

	[[nodiscard]] DatabaseOutageSnapshot status() const {
		return stateOwner_.snapshot();
	}

	[[nodiscard]] DatabaseOutageOperatorResumeResult resume(const DatabaseOutageOperatorResumeRequest &request) {
		const auto before = stateOwner_.snapshot();

		if (!request.authorized) {
			return rejected(DatabaseOutageOperatorResumeDisposition::RejectedUnauthorized, before);
		}
		if (!request.explicitlyConfirmed) {
			return rejected(DatabaseOutageOperatorResumeDisposition::RejectedUnconfirmed, before);
		}
		if (request.eventSequence == 0 || request.eventSequence <= before.lastEventSequence
			|| (before.lastEventTime.has_value() && request.eventTime < *before.lastEventTime)) {
			return rejected(DatabaseOutageOperatorResumeDisposition::RejectedStaleOrDuplicate, before);
		}
		if (request.expectedState != before.state) {
			return rejected(DatabaseOutageOperatorResumeDisposition::RejectedStateMismatch, before);
		}
		if (request.expectedTransitionCount != before.transitionCount) {
			return rejected(DatabaseOutageOperatorResumeDisposition::RejectedTransitionMismatch, before);
		}
		if (request.expectedLastEventSequence != before.lastEventSequence) {
			return rejected(DatabaseOutageOperatorResumeDisposition::RejectedSequenceMismatch, before);
		}
		if (before.state != DatabaseOutageState::Degraded && before.state != DatabaseOutageState::Maintenance) {
			return rejected(DatabaseOutageOperatorResumeDisposition::RejectedUnavailableState, before);
		}
		if (!before.recoveryEvidenceAccepted) {
			return rejected(DatabaseOutageOperatorResumeDisposition::RejectedRecoveryEvidence, before);
		}

		const auto event = stateOwner_.operatorResume(request.eventSequence, request.eventTime);
		const auto after = stateOwner_.snapshot();
		if (event.disposition == DatabaseOutageEventDisposition::Applied
			&& event.after.state == DatabaseOutageState::Healthy
			&& after.state == DatabaseOutageState::Healthy) {
			return DatabaseOutageOperatorResumeResult {
				.disposition = DatabaseOutageOperatorResumeDisposition::Applied,
				.action = DatabaseOutageOperatorAction::ResumeGameLifecycle,
				.before = before,
				.event = event,
				.after = after,
			};
		}

		DatabaseOutageOperatorResumeDisposition disposition = DatabaseOutageOperatorResumeDisposition::RejectedStateOwner;
		if (event.disposition == DatabaseOutageEventDisposition::RejectedStaleOrDuplicate) {
			disposition = DatabaseOutageOperatorResumeDisposition::RejectedStaleOrDuplicate;
		} else if (event.disposition == DatabaseOutageEventDisposition::RejectedState) {
			disposition = DatabaseOutageOperatorResumeDisposition::RejectedUnavailableState;
		} else if (event.disposition == DatabaseOutageEventDisposition::RejectedPrecondition) {
			disposition = DatabaseOutageOperatorResumeDisposition::RejectedRecoveryEvidence;
		}

		return DatabaseOutageOperatorResumeResult {
			.disposition = disposition,
			.action = DatabaseOutageOperatorAction::None,
			.before = before,
			.event = event,
			.after = after,
		};
	}

private:
	[[nodiscard]] static DatabaseOutageOperatorResumeResult rejected(
		DatabaseOutageOperatorResumeDisposition disposition,
		const DatabaseOutageSnapshot &snapshot
	) {
		return DatabaseOutageOperatorResumeResult {
			.disposition = disposition,
			.action = DatabaseOutageOperatorAction::None,
			.before = snapshot,
			.event = std::nullopt,
			.after = snapshot,
		};
	}

	DatabaseOutageStateMachine &stateOwner_;
};
