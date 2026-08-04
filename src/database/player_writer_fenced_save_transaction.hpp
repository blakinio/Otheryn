#pragma once

#include "database/database.hpp"
#include "database/player_writer_fence_repository.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <functional>
	#include <limits>
	#include <utility>
#endif

class PlayerWriterFencedSaveTransaction final {
public:
	template <typename SaveCallback>
	[[nodiscard]] static PlayerWriterFenceResult execute(
		PlayerWriterFenceContext &context,
		SaveCallback &&saveCallback
	) {
		if (!PlayerWriterFenceRepository::isValidOwnedContext(context)
		    || context.stateRevision == std::numeric_limits<PlayerWriterFenceRevision>::max()) {
			return PlayerWriterFenceResult::MalformedContext;
		}

		const auto nextRevision = context.stateRevision + 1;
		PlayerWriterFenceResult fenceResult = PlayerWriterFenceResult::DatabaseFailure;
		const bool committed = DBTransaction::executeWithinTransaction([&] {
			if (!std::invoke(std::forward<SaveCallback>(saveCallback))) {
				return false;
			}

			fenceResult = PlayerWriterFenceRepository().advanceRevisionInTransaction(context, nextRevision);
			return fenceResult == PlayerWriterFenceResult::Applied;
		});
		if (!committed) {
			return fenceResult == PlayerWriterFenceResult::Applied
				? PlayerWriterFenceResult::DatabaseFailure
				: fenceResult;
		}

		context.stateRevision = nextRevision;
		return PlayerWriterFenceResult::Applied;
	}
};
