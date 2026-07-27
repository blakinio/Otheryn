#pragma once

#include "game/scheduling/player_persistence_state.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <exception>
	#include <functional>
	#include <utility>
#endif

enum class PlayerCheckpointAttemptOutcome : uint8_t {
	saved,
	saveFailed,
	saveThrew,
};

struct PlayerCheckpointAttemptResult final {
	PlayerCheckpointAttemptOutcome outcome;
	bool acknowledgementAccepted = false;
	bool followUpRequired = false;
	std::exception_ptr exception;
};

/**
 * Executes one captured player checkpoint generation against an injected save
 * attempt and records the exact success/failure acknowledgement decision.
 *
 * The helper owns no queue, timer, Player object or database behavior. It is a
 * deterministic boundary used by SaveManager so controlled failure tests can
 * prove acknowledgement and follow-up semantics without failing a real store.
 */
template <typename SaveAttempt>
[[nodiscard]] PlayerCheckpointAttemptResult executePlayerCheckpointAttempt(
	PlayerPersistenceState &state,
	PlayerPersistenceState::Generation generation,
	SaveAttempt &&saveAttempt
) {
	bool saveSuccess = false;
	try {
		saveSuccess = std::invoke(std::forward<SaveAttempt>(saveAttempt));
	} catch (...) {
		return {
			PlayerCheckpointAttemptOutcome::saveThrew,
			state.acknowledgeFailure(generation),
			false,
			std::current_exception(),
		};
	}

	if (!saveSuccess) {
		return {
			PlayerCheckpointAttemptOutcome::saveFailed,
			state.acknowledgeFailure(generation),
			false,
			{},
		};
	}

	const bool acknowledged = state.acknowledgeSuccess(generation);
	return {
		PlayerCheckpointAttemptOutcome::saved,
		acknowledged,
		acknowledged && state.isDirty(),
		{},
	};
}
