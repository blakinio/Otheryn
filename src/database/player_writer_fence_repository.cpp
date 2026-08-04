#include "database/player_writer_fence_repository.hpp"

#include "database/database.hpp"

#include <fmt/format.h>

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <limits>
	#include <optional>
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

	std::optional<uint8_t> hexNibble(char value) {
		if (value >= '0' && value <= '9') {
			return static_cast<uint8_t>(value - '0');
		}
		if (value >= 'A' && value <= 'F') {
			return static_cast<uint8_t>(value - 'A' + 10);
		}
		if (value >= 'a' && value <= 'f') {
			return static_cast<uint8_t>(value - 'a' + 10);
		}
		return std::nullopt;
	}

	std::optional<PlayerWriterFenceToken> parseTokenHex(const std::string &value) {
		PlayerWriterFenceToken token {};
		if (value.empty()) {
			return token;
		}
		if (value.size() != token.size() * 2) {
			return std::nullopt;
		}
		for (size_t index = 0; index < token.size(); ++index) {
			const auto high = hexNibble(value[index * 2]);
			const auto low = hexNibble(value[index * 2 + 1]);
			if (!high.has_value() || !low.has_value()) {
				return std::nullopt;
			}
			token[index] = static_cast<uint8_t>((*high << 4U) | *low);
		}
		return token;
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

bool PlayerWriterFenceRepository::isValidToken(const PlayerWriterFenceToken &token) noexcept {
	return std::ranges::any_of(token, [](uint8_t byte) {
		return byte != 0;
	});
}

bool PlayerWriterFenceRepository::isValidOwnedContext(const PlayerWriterFenceContext &context) noexcept {
	return context.playerId != 0 && context.ownershipGeneration != 0 && isValidToken(context.writerToken);
}

PlayerWriterFenceLoadResult PlayerWriterFenceRepository::load(PlayerWriterFenceSubjectId playerId) const {
	if (playerId == 0) {
		return { PlayerWriterFenceResult::MalformedContext, {} };
	}

	const auto result = g_database().storeQuery(fmt::format(
		"SELECT `ownership_generation`, COALESCE(HEX(`writer_token`), '') AS `writer_token_hex`, `state_revision` "
		"FROM `player_writer_fence` WHERE `player_id` = {}",
		playerId
	));
	if (!result) {
		return { PlayerWriterFenceResult::DatabaseFailure, {} };
	}

	const auto parsedToken = parseTokenHex(result->getString("writer_token_hex"));
	if (!parsedToken.has_value()) {
		g_logger().error("Writer-fence row {} contains a malformed token representation.", playerId);
		return { PlayerWriterFenceResult::DatabaseFailure, {} };
	}

	return {
		PlayerWriterFenceResult::Applied,
		{
			.playerId = playerId,
			.ownershipGeneration = result->getNumber<PlayerWriterFenceGeneration>("ownership_generation"),
			.writerToken = *parsedToken,
			.stateRevision = result->getNumber<PlayerWriterFenceRevision>("state_revision"),
		},
	};
}

PlayerWriterFenceResult PlayerWriterFenceRepository::executeCasInCurrentTransaction(const std::string &query) {
	if (!g_database().executeQuery(query)) {
		return PlayerWriterFenceResult::DatabaseFailure;
	}

	const auto affected = g_database().storeQuery("SELECT ROW_COUNT() AS `affected_rows`");
	if (!affected) {
		return PlayerWriterFenceResult::DatabaseFailure;
	}

	const auto affectedRows = affected->getNumber<uint64_t>("affected_rows");
	if (affectedRows > 1) {
		g_logger().error("Writer-fence CAS affected more than one authority row: {}", affectedRows);
		return PlayerWriterFenceResult::DatabaseFailure;
	}

	return affectedRows == 1 ? PlayerWriterFenceResult::Applied : PlayerWriterFenceResult::StaleConflict;
}

PlayerWriterFenceResult PlayerWriterFenceRepository::executeCas(const std::string &query) {
	PlayerWriterFenceResult result = PlayerWriterFenceResult::DatabaseFailure;
	const bool committed = DBTransaction::executeWithinTransaction([&] {
		result = executeCasInCurrentTransaction(query);
		return result == PlayerWriterFenceResult::Applied || result == PlayerWriterFenceResult::StaleConflict;
	});

	return committed ? result : PlayerWriterFenceResult::DatabaseFailure;
}

PlayerWriterFenceResult PlayerWriterFenceRepository::acquire(const PlayerWriterFenceContext &desired) const {
	if (!isValidOwnedContext(desired)) {
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
	if (!isValidOwnedContext(current) || !isValidOwnedContext(desired) || current.playerId != desired.playerId
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
	if (!isValidOwnedContext(current)) {
		return PlayerWriterFenceResult::MalformedContext;
	}

	return executeCas(fmt::format(
		"UPDATE `player_writer_fence` SET `writer_token` = NULL WHERE {}",
		exactOwnerPredicate(current)
	));
}

PlayerWriterFenceResult PlayerWriterFenceRepository::advanceRevisionInTransaction(
	const PlayerWriterFenceContext &current,
	PlayerWriterFenceRevision nextRevision
) const {
	if (!isValidOwnedContext(current) || current.stateRevision == std::numeric_limits<PlayerWriterFenceRevision>::max()
	    || nextRevision != current.stateRevision + 1) {
		return PlayerWriterFenceResult::MalformedContext;
	}

	return executeCasInCurrentTransaction(fmt::format(
		"UPDATE `player_writer_fence` SET `state_revision` = {} WHERE {}",
		nextRevision,
		exactOwnerPredicate(current)
	));
}

PlayerWriterFenceResult PlayerWriterFenceRepository::advanceRevision(
	const PlayerWriterFenceContext &current,
	PlayerWriterFenceRevision nextRevision
) const {
	if (!isValidOwnedContext(current) || current.stateRevision == std::numeric_limits<PlayerWriterFenceRevision>::max()
	    || nextRevision != current.stateRevision + 1) {
		return PlayerWriterFenceResult::MalformedContext;
	}

	return executeCas(fmt::format(
		"UPDATE `player_writer_fence` SET `state_revision` = {} WHERE {}",
		nextRevision,
		exactOwnerPredicate(current)
	));
}
