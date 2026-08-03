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

class PlayerWriterFenceRepository final {
public:
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

private:
	[[nodiscard]] static bool validOwnedContext(const PlayerWriterFenceContext &context) noexcept;
	[[nodiscard]] static bool validToken(const PlayerWriterFenceToken &token) noexcept;
	[[nodiscard]] static PlayerWriterFenceResult executeCas(const std::string &query);
};
