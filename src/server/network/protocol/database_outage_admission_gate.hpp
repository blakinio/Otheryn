#pragma once

#include "server/network/protocol/database_outage_admission_policy.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <utility>
#endif

namespace DatabaseOutageAdmissionGate {
	template <typename SnapshotProvider>
	[[nodiscard]] DatabaseOutageSnapshot capture(SnapshotProvider &&snapshotProvider) noexcept(noexcept(std::forward<SnapshotProvider>(snapshotProvider)())) {
		return std::forward<SnapshotProvider>(snapshotProvider)();
	}

	[[nodiscard]] constexpr DatabaseOutageAdmissionDecision evaluate(
		const DatabaseOutageSnapshot &snapshot,
		DatabaseOutageAdmissionOperation operation,
		DatabaseOutageAdmissionCallerContext caller,
		GameState_t lifecycleState
	) noexcept {
		return DatabaseOutageAdmissionPolicy::evaluate(snapshot, operation, caller, lifecycleState);
	}

	/**
	 * Captures exactly one immutable snapshot from the accepted PRS-003 owner seam
	 * and evaluates the existing pure admission policy for one live boundary.
	 */
	template <typename SnapshotProvider>
	[[nodiscard]] DatabaseOutageAdmissionDecision evaluateLive(
		SnapshotProvider &&snapshotProvider,
		DatabaseOutageAdmissionOperation operation,
		DatabaseOutageAdmissionCallerContext caller,
		GameState_t lifecycleState
	) noexcept(noexcept(capture(std::forward<SnapshotProvider>(snapshotProvider)))) {
		const DatabaseOutageSnapshot snapshot = capture(std::forward<SnapshotProvider>(snapshotProvider));
		return evaluate(snapshot, operation, caller, lifecycleState);
	}
} // namespace DatabaseOutageAdmissionGate
