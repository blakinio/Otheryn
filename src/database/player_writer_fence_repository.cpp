#include "database/player_writer_fence_repository.hpp"

#include "database/database.hpp"

#include <fmt/format.h>

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <limits>
	#include <string>
#endif

namespace {
	std::string tokenHex(const PlayerWriterFenceToken &token) {
		static constexpr char digits[] = "0123456789ABCDEF";
		std::string value;
		value.reserve(token.size() * 2);
		for (const auto byte : token) {
			value.push_back(digits[(byte >> 4U) & 0x0FU]);
			value.push_back(digits[byte & 0x0FU]);
		}
		return value;
	}

	std::string exactOwnerPredicate(const PlayerWriterFenceContext &context) {
		return fmt::format(
			"`player_id` = {} AND `ownership_generation` = {} AND `writer_token` = UNHEX('{}') AND `state_revision` = {}",
			context.playerId,
			context.ownershipGeneration,
			tokenHex(context.writerToken),
			context.stateRevision
		);
	}
} // namespace

bool PlayerWriterFenceRepository::validToken(const PlayerWriterFenceToken &token) noexcept {
	return std::ranges::any_of(token, [](uint8_t byte) {
		return byte != 0;
	});
}

bool PlayerWriterFenceRepository::validOwnedContext(const PlayerWriterFenceContext &context) noexcept {
	return context.playerId != 0 && context.ownershipGeneration != 0 && validToken(context.writerToken);
}

PlayerWriterFenceResult PlayerWriterFenceRepository::executeCas(const std::string &query) {
	PlayerWriterFenceResult result = PlayerWriterFenceResult::DatabaseFailure;
	const bool committed = DBTransaction::executeWithinTransaction([&] {
		if (!g_database().executeQuery(query)) {
			return false;
		}

		const auto affected = g_database().storeQuery("SELECT ROW_COUNT() AS `affected_rows`");
		if (!affected) {
			return false;
		}

		const auto affectedRows = affected->getNumber<uint64_t>("affected_rows");
		if (affectedRows > 1) {
			g_logger().error("Writer-fence CAS affected more than one authority row: {}", affectedRows);
			return false;
		}

		result = affectedRows == 1 ? PlayerWriterFenceResult::Applied : PlayerWriterFenceResult::StaleConflict;
		return true;
	});

	return committed ? result : PlayerWriterFenceResult::DatabaseFailure;
}

PlayerWriterFenceResult PlayerWriterFenceRepository::acquire(const PlayerWriterFenceContext &desired) const {
	if (!validOwnedContext(desired)) {
		return PlayerWriterFenceResult::MalformedContext;
	}

	return executeCas(fmt::format(
		"UPDATE `player_writer_fence` SET `ownership_generation` = {}, `writer_token` = UNHEX('{}') "
		"WHERE `player_id` = {} AND `writer_token` IS NULL AND `ownership_generation` < {} AND `state_revision` = {}",
		desired.ownershipGeneration,
		tokenHex(desired.writerToken),
		desired.playerId,
		desired.ownershipGeneration,
		desired.stateRevision
	));
}

PlayerWriterFenceResult PlayerWriterFenceRepository::transfer(
	const PlayerWriterFenceContext &current,
	const PlayerWriterFenceContext &desired
) const {
	if (!validOwnedContext(current) || !validOwnedContext(desired) || current.playerId != desired.playerId
	    || desired.ownershipGeneration <= current.ownershipGeneration || desired.stateRevision != current.stateRevision
	    || current.writerToken == desired.writerToken) {
		return PlayerWriterFenceResult::MalformedContext;
	}

	return executeCas(fmt::format(
		"UPDATE `player_writer_fence` SET `ownership_generation` = {}, `writer_token` = UNHEX('{}') WHERE {}",
		desired.ownershipGeneration,
		tokenHex(desired.writerToken),
		exactOwnerPredicate(current)
	));
}

PlayerWriterFenceResult PlayerWriterFenceRepository::release(const PlayerWriterFenceContext &current) const {
	if (!validOwnedContext(current)) {
		return PlayerWriterFenceResult::MalformedContext;
	}

	return executeCas(fmt::format(
		"UPDATE `player_writer_fence` SET `writer_token` = NULL WHERE {}",
		exactOwnerPredicate(current)
	));
}

PlayerWriterFenceResult PlayerWriterFenceRepository::advanceRevision(
	const PlayerWriterFenceContext &current,
	PlayerWriterFenceRevision nextRevision
) const {
	if (!validOwnedContext(current) || current.stateRevision == std::numeric_limits<PlayerWriterFenceRevision>::max()
	    || nextRevision != current.stateRevision + 1) {
		return PlayerWriterFenceResult::MalformedContext;
	}

	return executeCas(fmt::format(
		"UPDATE `player_writer_fence` SET `state_revision` = {} WHERE {}",
		nextRevision,
		exactOwnerPredicate(current)
	));
}
