#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <array>
	#include <cstdint>
	#include <string>
#endif

using PlayerWriterFenceSubjectId = uint32_t;
using PlayerWriterFenceGeneration = uint64_t;
using PlayerWriterFenceRevision = uint64_t;
using PlayerWriterFenceToken = std::array<uint8_t, 16>;

enum class PlayerWriterFenceResult : uint8_t {
	Applied,
	StaleConflict,
	MalformedContext,
	DatabaseFailure,
};

struct PlayerWriterFenceContext final {
	PlayerWriterFenceSubjectId playerId = 0;
	PlayerWriterFenceGeneration ownershipGeneration = 0;
	PlayerWriterFenceToken writerToken {};
	PlayerWriterFenceRevision stateRevision = 0;
};

struct PlayerWriterFenceLoadResult final {
	PlayerWriterFenceResult result = PlayerWriterFenceResult::DatabaseFailure;
	PlayerWriterFenceContext context {};
};

class PlayerWriterFenceRepository final {
public:
	[[nodiscard]] PlayerWriterFenceLoadResult load(PlayerWriterFenceSubjectId playerId) const;

	[[nodiscard]] PlayerWriterFenceResult acquire(const PlayerWriterFenceContext &desired) const;

	[[nodiscard]] PlayerWriterFenceResult transfer(
		const PlayerWriterFenceContext &current,
		const PlayerWriterFenceContext &desired
	) const;

	[[nodiscard]] PlayerWriterFenceResult release(const PlayerWriterFenceContext &current) const;

	[[nodiscard]] PlayerWriterFenceResult advanceRevision(
		const PlayerWriterFenceContext &current,
		PlayerWriterFenceRevision nextRevision
	) const;

	/**
	 * Executes only the exact-next revision CAS on the caller-owned transaction.
	 * The caller must already own the shared database connection lock through
	 * DBTransaction. This method never starts, commits or retries a transaction.
	 */
	[[nodiscard]] PlayerWriterFenceResult advanceRevisionInTransaction(
		const PlayerWriterFenceContext &current,
		PlayerWriterFenceRevision nextRevision
	) const;

	[[nodiscard]] static bool isValidOwnedContext(const PlayerWriterFenceContext &context) noexcept;
	[[nodiscard]] static bool isValidToken(const PlayerWriterFenceToken &token) noexcept;

private:
	[[nodiscard]] static PlayerWriterFenceResult executeCas(const std::string &query);
	[[nodiscard]] static PlayerWriterFenceResult executeCasInCurrentTransaction(const std::string &query);
};
