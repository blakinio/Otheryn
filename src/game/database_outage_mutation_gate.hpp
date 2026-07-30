#pragma once

#include "game/database_outage_mutation_admission_policy.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <functional>
	#include <utility>
#endif

struct DatabaseOutageMutationExecutionResult final {
	DatabaseOutageMutationDecision decision;
	bool executed = false;
	bool mutationResult = false;
};

namespace DatabaseOutageMutationGate {
	template <typename SnapshotProvider>
	[[nodiscard]] DatabaseOutageSnapshot capture(SnapshotProvider &&snapshotProvider) noexcept(noexcept(std::forward<SnapshotProvider>(snapshotProvider)())) {
		return std::forward<SnapshotProvider>(snapshotProvider)();
	}

	[[nodiscard]] constexpr DatabaseOutageMutationDecision evaluate(
		const DatabaseOutageSnapshot &snapshot,
		DatabaseOutageMutationOperation operation,
		GameState_t lifecycleState
	) noexcept {
		return DatabaseOutageMutationAdmissionPolicy::evaluate(snapshot, operation, lifecycleState);
	}

	/**
	 * Captures one immutable snapshot, evaluates the accepted pure policy and
	 * invokes a boolean mutation at most once only when admitted.
	 */
	template <typename SnapshotProvider, typename Mutation>
	[[nodiscard]] DatabaseOutageMutationExecutionResult executeLive(
		SnapshotProvider &&snapshotProvider,
		DatabaseOutageMutationOperation operation,
		GameState_t lifecycleState,
		Mutation &&mutation
	) {
		const DatabaseOutageSnapshot snapshot = capture(std::forward<SnapshotProvider>(snapshotProvider));
		const auto decision = evaluate(snapshot, operation, lifecycleState);
		if (!decision.allowed()) {
			return DatabaseOutageMutationExecutionResult {
				.decision = decision,
			};
		}

		return DatabaseOutageMutationExecutionResult {
			.decision = decision,
			.executed = true,
			.mutationResult = static_cast<bool>(std::invoke(std::forward<Mutation>(mutation))),
		};
	}
} // namespace DatabaseOutageMutationGate
