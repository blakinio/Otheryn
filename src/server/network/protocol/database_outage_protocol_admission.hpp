#pragma once

#include "database/database_failure_classification.hpp"
#include "server/network/protocol/database_outage_admission_policy.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <string_view>
#endif

enum class DatabaseOutageProtocolAdmissionDisposition : uint8_t {
	Allow,
	Reject,
	DeferExistingLifecycle,
};

struct DatabaseOutageProtocolAdmissionResult final {
	DatabaseOutageAdmissionDecision decision;
	DatabaseOutageProtocolAdmissionDisposition disposition = DatabaseOutageProtocolAdmissionDisposition::Reject;
	std::string_view message;

	[[nodiscard]] constexpr bool allowed() const noexcept {
		return disposition == DatabaseOutageProtocolAdmissionDisposition::Allow;
	}

	[[nodiscard]] constexpr bool rejected() const noexcept {
		return disposition == DatabaseOutageProtocolAdmissionDisposition::Reject;
	}

	[[nodiscard]] constexpr bool defersExistingLifecycle() const noexcept {
		return disposition == DatabaseOutageProtocolAdmissionDisposition::DeferExistingLifecycle;
	}
};

namespace DatabaseOutageProtocolAdmission {
	inline constexpr std::string_view StartupMessage = "Gameworld is starting up. Please wait.";
	inline constexpr std::string_view MaintenanceMessage = "Gameworld is under maintenance. Please re-connect in a while.";
	inline constexpr std::string_view ClosingMessage = "The game is just going down.\nPlease try again later.";
	inline constexpr std::string_view ClosedMessage = "Server is currently closed.\nPlease try again later.";
	inline constexpr std::string_view DegradedMessage = "Gameworld persistence is temporarily unavailable. Please try again later.";
	inline constexpr std::string_view DrainingMessage = "Gameworld is entering maintenance. Please try again later.";
	inline constexpr std::string_view UnavailableMessage = "Gameworld persistence is unavailable. Please try again later.";

	[[nodiscard]] constexpr std::string_view messageForReason(DatabaseOutageAdmissionReason reason) noexcept {
		using enum DatabaseOutageAdmissionReason;
		switch (reason) {
			case LifecycleStartup:
				return StartupMessage;
			case LifecycleMaintenance:
				return MaintenanceMessage;
			case LifecycleClosing:
				return ClosingMessage;
			case LifecycleClosed:
				return ClosedMessage;
			case OutageDegraded:
				return DegradedMessage;
			case OutageDraining:
				return DrainingMessage;
			case OutageMaintenance:
				return MaintenanceMessage;
			case Allowed:
				return {};
			case DiagnosticCapabilityRequired:
			case LifecycleShutdown:
			case UnknownOperation:
			case UnknownLifecycleState:
			case UnknownOutageState:
			default:
				return UnavailableMessage;
		}
	}

	[[nodiscard]] constexpr DatabaseOutageProtocolAdmissionResult evaluate(
		const DatabaseOutageSnapshot &snapshot,
		DatabaseOutageAdmissionOperation operation,
		DatabaseOutageAdmissionCallerContext caller,
		GameState_t lifecycleState,
		bool deferClosingAndClosed = false
	) noexcept {
		const auto decision = DatabaseOutageAdmissionPolicy::evaluate(snapshot, operation, caller, lifecycleState);
		if (decision.allowed()) {
			return DatabaseOutageProtocolAdmissionResult {
				.decision = decision,
				.disposition = DatabaseOutageProtocolAdmissionDisposition::Allow,
				.message = {},
			};
		}

		if (deferClosingAndClosed
		    && (decision.reason == DatabaseOutageAdmissionReason::LifecycleClosing
		        || decision.reason == DatabaseOutageAdmissionReason::LifecycleClosed)) {
			return DatabaseOutageProtocolAdmissionResult {
				.decision = decision,
				.disposition = DatabaseOutageProtocolAdmissionDisposition::DeferExistingLifecycle,
				.message = {},
			};
		}

		return DatabaseOutageProtocolAdmissionResult {
			.decision = decision,
			.disposition = DatabaseOutageProtocolAdmissionDisposition::Reject,
			.message = messageForReason(decision.reason),
		};
	}

	[[nodiscard]] inline DatabaseOutageProtocolAdmissionResult evaluateRuntime(
		DatabaseOutageAdmissionOperation operation,
		DatabaseOutageAdmissionCallerContext caller,
		GameState_t lifecycleState,
		bool deferClosingAndClosed = false
	) {
		return evaluate(getDatabaseOutageSnapshot(), operation, caller, lifecycleState, deferClosingAndClosed);
	}

	[[nodiscard]] inline DatabaseOutageProtocolAdmissionResult evaluateAccountLogin(GameState_t lifecycleState) {
		return evaluateRuntime(DatabaseOutageAdmissionOperation::AccountLogin, {}, lifecycleState);
	}

	[[nodiscard]] inline DatabaseOutageProtocolAdmissionResult evaluateGameLogin(GameState_t lifecycleState) {
		return evaluateRuntime(DatabaseOutageAdmissionOperation::GameLogin, {}, lifecycleState, true);
	}

	[[nodiscard]] inline DatabaseOutageProtocolAdmissionResult evaluateChannelHandoff(
		GameState_t lifecycleState,
		bool canAlwaysLogin
	) {
		return evaluateRuntime(
			DatabaseOutageAdmissionOperation::ChannelHandoff,
			DatabaseOutageAdmissionCallerContext { .canAlwaysLogin = canAlwaysLogin },
			lifecycleState
		);
	}

	/**
	 * Explicit staff-diagnostic path. Callers must supply a dedicated diagnostic
	 * capability; CanAlwaysLogin is deliberately neither accepted nor inferred.
	 */
	[[nodiscard]] inline DatabaseOutageProtocolAdmissionResult evaluateStaffDiagnostic(
		GameState_t lifecycleState,
		bool hasDiagnosticCapability
	) {
		return evaluateRuntime(
			DatabaseOutageAdmissionOperation::StaffDiagnostic,
			DatabaseOutageAdmissionCallerContext { .staffDiagnostic = hasDiagnosticCapability },
			lifecycleState
		);
	}
} // namespace DatabaseOutageProtocolAdmission
