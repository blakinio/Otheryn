#pragma once

#include "database/database_outage_state.hpp"
#include "game/game_definitions.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
#endif

enum class DatabaseOutageAdmissionOperation : uint8_t {
	AccountLogin,
	GameLogin,
	ChannelHandoff,
	StaffDiagnostic,
};

enum class DatabaseOutageAdmissionDisposition : uint8_t {
	Allow,
	Reject,
};

enum class DatabaseOutageAdmissionReason : uint8_t {
	Allowed,
	UnknownOperation,
	DiagnosticCapabilityRequired,
	LifecycleStartup,
	LifecycleShutdown,
	LifecycleMaintenance,
	LifecycleClosing,
	LifecycleClosed,
	UnknownLifecycleState,
	OutageDegraded,
	OutageDraining,
	OutageMaintenance,
	UnknownOutageState,
};

struct DatabaseOutageAdmissionCallerContext final {
	bool canAlwaysLogin = false;
	bool staffDiagnostic = false;
};

struct DatabaseOutageAdmissionDecision final {
	DatabaseOutageAdmissionDisposition disposition = DatabaseOutageAdmissionDisposition::Reject;
	DatabaseOutageAdmissionReason reason = DatabaseOutageAdmissionReason::UnknownOperation;
	DatabaseOutageAdmissionOperation operation = DatabaseOutageAdmissionOperation::AccountLogin;
	DatabaseOutageState outageState = DatabaseOutageState::Healthy;
	GameState_t lifecycleState = GAME_STATE_STARTUP;

	[[nodiscard]] constexpr bool allowed() const noexcept {
		return disposition == DatabaseOutageAdmissionDisposition::Allow;
	}

	friend constexpr bool operator==(const DatabaseOutageAdmissionDecision &, const DatabaseOutageAdmissionDecision &) = default;
};

namespace DatabaseOutageAdmissionPolicy {
	namespace detail {
		[[nodiscard]] constexpr DatabaseOutageAdmissionDecision makeDecision(
			DatabaseOutageAdmissionDisposition disposition,
			DatabaseOutageAdmissionReason reason,
			DatabaseOutageAdmissionOperation operation,
			DatabaseOutageState outageState,
			GameState_t lifecycleState
		) noexcept {
			return DatabaseOutageAdmissionDecision {
				.disposition = disposition,
				.reason = reason,
				.operation = operation,
				.outageState = outageState,
				.lifecycleState = lifecycleState,
			};
		}

		[[nodiscard]] constexpr DatabaseOutageAdmissionDecision reject(
			DatabaseOutageAdmissionReason reason,
			DatabaseOutageAdmissionOperation operation,
			DatabaseOutageState outageState,
			GameState_t lifecycleState
		) noexcept {
			return makeDecision(DatabaseOutageAdmissionDisposition::Reject, reason, operation, outageState, lifecycleState);
		}

		[[nodiscard]] constexpr bool isKnownOperation(DatabaseOutageAdmissionOperation operation) noexcept {
			switch (operation) {
				case DatabaseOutageAdmissionOperation::AccountLogin:
				case DatabaseOutageAdmissionOperation::GameLogin:
				case DatabaseOutageAdmissionOperation::ChannelHandoff:
				case DatabaseOutageAdmissionOperation::StaffDiagnostic:
					return true;
				default:
					return false;
			}
		}
	} // namespace detail

	/**
	 * Evaluates admission from immutable caller-supplied values only.
	 *
	 * The policy owns no database, protocol, session, player, channel or mutable
	 * outage state. It performs no I/O and returns one fixed decision suitable for
	 * a later protocol adapter.
	 */
	[[nodiscard]] constexpr DatabaseOutageAdmissionDecision evaluate(
		const DatabaseOutageSnapshot &snapshot,
		DatabaseOutageAdmissionOperation operation,
		DatabaseOutageAdmissionCallerContext caller,
		GameState_t lifecycleState
	) noexcept {
		using enum DatabaseOutageAdmissionOperation;
		using enum DatabaseOutageAdmissionReason;

		if (!detail::isKnownOperation(operation)) {
			return detail::reject(UnknownOperation, operation, snapshot.state, lifecycleState);
		}

		switch (lifecycleState) {
			case GAME_STATE_STARTUP:
				return detail::reject(LifecycleStartup, operation, snapshot.state, lifecycleState);
			case GAME_STATE_SHUTDOWN:
				return detail::reject(LifecycleShutdown, operation, snapshot.state, lifecycleState);
			case GAME_STATE_MAINTAIN:
				if (operation != StaffDiagnostic) {
					return detail::reject(LifecycleMaintenance, operation, snapshot.state, lifecycleState);
				}
				break;
			case GAME_STATE_CLOSING:
				if ((operation == GameLogin || operation == ChannelHandoff) && !caller.canAlwaysLogin) {
					return detail::reject(LifecycleClosing, operation, snapshot.state, lifecycleState);
				}
				break;
			case GAME_STATE_CLOSED:
				if ((operation == GameLogin || operation == ChannelHandoff) && !caller.canAlwaysLogin) {
					return detail::reject(LifecycleClosed, operation, snapshot.state, lifecycleState);
				}
				break;
			case GAME_STATE_INIT:
			case GAME_STATE_NORMAL:
				break;
			default:
				return detail::reject(UnknownLifecycleState, operation, snapshot.state, lifecycleState);
		}

		if (operation == StaffDiagnostic && !caller.staffDiagnostic) {
			return detail::reject(DiagnosticCapabilityRequired, operation, snapshot.state, lifecycleState);
		}

		switch (snapshot.state) {
			case DatabaseOutageState::Healthy:
				return detail::makeDecision(DatabaseOutageAdmissionDisposition::Allow, Allowed, operation, snapshot.state, lifecycleState);
			case DatabaseOutageState::Degraded:
				return detail::reject(OutageDegraded, operation, snapshot.state, lifecycleState);
			case DatabaseOutageState::Draining:
				return detail::reject(OutageDraining, operation, snapshot.state, lifecycleState);
			case DatabaseOutageState::Maintenance:
				if (operation == StaffDiagnostic) {
					return detail::makeDecision(DatabaseOutageAdmissionDisposition::Allow, Allowed, operation, snapshot.state, lifecycleState);
				}
				return detail::reject(OutageMaintenance, operation, snapshot.state, lifecycleState);
			default:
				return detail::reject(UnknownOutageState, operation, snapshot.state, lifecycleState);
		}
	}
} // namespace DatabaseOutageAdmissionPolicy
