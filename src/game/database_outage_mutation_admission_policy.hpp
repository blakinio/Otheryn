#pragma once

#include "database/database_outage_state.hpp"
#include "game/game_definitions.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
#endif

enum class DatabaseOutageMutationOperation : uint8_t {
	CriticalDurable,
	OrdinaryDurable,
	EphemeralNonDurable,
};

enum class DatabaseOutageMutationDisposition : uint8_t {
	Allow,
	Reject,
};

enum class DatabaseOutageMutationReason : uint8_t {
	Allowed,
	UnknownOperation,
	LifecycleStartup,
	LifecycleClosing,
	LifecycleClosed,
	LifecycleShutdown,
	LifecycleMaintenance,
	UnknownLifecycleState,
	OutageDegradedDurableMutation,
	OutageDraining,
	OutageMaintenance,
	UnknownOutageState,
};

struct DatabaseOutageMutationDecision final {
	DatabaseOutageMutationDisposition disposition = DatabaseOutageMutationDisposition::Reject;
	DatabaseOutageMutationReason reason = DatabaseOutageMutationReason::UnknownOperation;
	DatabaseOutageMutationOperation operation = DatabaseOutageMutationOperation::CriticalDurable;
	DatabaseOutageState outageState = DatabaseOutageState::Healthy;
	GameState_t lifecycleState = GAME_STATE_STARTUP;

	[[nodiscard]] constexpr bool allowed() const noexcept {
		return disposition == DatabaseOutageMutationDisposition::Allow;
	}

	friend constexpr bool operator==(const DatabaseOutageMutationDecision &, const DatabaseOutageMutationDecision &) = default;
};

namespace DatabaseOutageMutationAdmissionPolicy {
	namespace detail {
		[[nodiscard]] constexpr DatabaseOutageMutationDecision makeDecision(
			DatabaseOutageMutationDisposition disposition,
			DatabaseOutageMutationReason reason,
			DatabaseOutageMutationOperation operation,
			DatabaseOutageState outageState,
			GameState_t lifecycleState
		) noexcept {
			return DatabaseOutageMutationDecision {
				.disposition = disposition,
				.reason = reason,
				.operation = operation,
				.outageState = outageState,
				.lifecycleState = lifecycleState,
			};
		}

		[[nodiscard]] constexpr DatabaseOutageMutationDecision reject(
			DatabaseOutageMutationReason reason,
			DatabaseOutageMutationOperation operation,
			DatabaseOutageState outageState,
			GameState_t lifecycleState
		) noexcept {
			return makeDecision(DatabaseOutageMutationDisposition::Reject, reason, operation, outageState, lifecycleState);
		}

		[[nodiscard]] constexpr bool isKnownOperation(DatabaseOutageMutationOperation operation) noexcept {
			switch (operation) {
				case DatabaseOutageMutationOperation::CriticalDurable:
				case DatabaseOutageMutationOperation::OrdinaryDurable:
				case DatabaseOutageMutationOperation::EphemeralNonDurable:
					return true;
				default:
					return false;
			}
		}
	} // namespace detail

	/**
	 * Evaluates mutation admission from immutable caller-supplied values only.
	 *
	 * The policy owns no database, gameplay object, lifecycle state, scheduler,
	 * checkpoint or mutable outage state. It performs no I/O and returns one fixed
	 * decision suitable for a later runtime adapter.
	 */
	[[nodiscard]] constexpr DatabaseOutageMutationDecision evaluate(
		const DatabaseOutageSnapshot &snapshot,
		DatabaseOutageMutationOperation operation,
		GameState_t lifecycleState
	) noexcept {
		using enum DatabaseOutageMutationOperation;
		using enum DatabaseOutageMutationReason;

		if (!detail::isKnownOperation(operation)) {
			return detail::reject(UnknownOperation, operation, snapshot.state, lifecycleState);
		}

		switch (lifecycleState) {
			case GAME_STATE_INIT:
			case GAME_STATE_NORMAL:
				break;
			case GAME_STATE_STARTUP:
				return detail::reject(LifecycleStartup, operation, snapshot.state, lifecycleState);
			case GAME_STATE_CLOSING:
				return detail::reject(LifecycleClosing, operation, snapshot.state, lifecycleState);
			case GAME_STATE_CLOSED:
				return detail::reject(LifecycleClosed, operation, snapshot.state, lifecycleState);
			case GAME_STATE_SHUTDOWN:
				return detail::reject(LifecycleShutdown, operation, snapshot.state, lifecycleState);
			case GAME_STATE_MAINTAIN:
				return detail::reject(LifecycleMaintenance, operation, snapshot.state, lifecycleState);
			default:
				return detail::reject(UnknownLifecycleState, operation, snapshot.state, lifecycleState);
		}

		switch (snapshot.state) {
			case DatabaseOutageState::Healthy:
				return detail::makeDecision(DatabaseOutageMutationDisposition::Allow, Allowed, operation, snapshot.state, lifecycleState);
			case DatabaseOutageState::Degraded:
				if (operation == EphemeralNonDurable) {
					return detail::makeDecision(DatabaseOutageMutationDisposition::Allow, Allowed, operation, snapshot.state, lifecycleState);
				}
				return detail::reject(OutageDegradedDurableMutation, operation, snapshot.state, lifecycleState);
			case DatabaseOutageState::Draining:
				return detail::reject(OutageDraining, operation, snapshot.state, lifecycleState);
			case DatabaseOutageState::Maintenance:
				return detail::reject(OutageMaintenance, operation, snapshot.state, lifecycleState);
			default:
				return detail::reject(UnknownOutageState, operation, snapshot.state, lifecycleState);
		}
	}
} // namespace DatabaseOutageMutationAdmissionPolicy
