/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "server/network/protocol/protocol_profile.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <optional>
	#include <string_view>
#endif

class NetworkMessage;
class OutputMessage;
class Protocol;

enum class InboundTransportStatus : uint8_t {
	Accepted,
	ZeroSequence,
	SequenceMismatch,
	ChecksumMismatch,
	DecryptFailure,
	MalformedFrame,
};

struct InboundTransportResult {
	InboundTransportStatus status = InboundTransportStatus::MalformedFrame;
	std::optional<uint32_t> receivedSequence;
	std::optional<uint32_t> expectedSequence;

	[[nodiscard]] bool accepted() const {
		return status == InboundTransportStatus::Accepted;
	}

	[[nodiscard]] explicit operator bool() const {
		return accepted();
	}
};

[[nodiscard]] constexpr uint32_t nextInboundSequence(uint32_t acceptedSequence) {
	return acceptedSequence + 1;
}

[[nodiscard]] constexpr uint32_t storedInboundSequence(uint32_t acceptedSequence) {
	return acceptedSequence >= 0x7FFFFFFF ? 0 : acceptedSequence;
}

[[nodiscard]] std::string_view getInboundTransportStatusName(InboundTransportStatus status);

#ifdef BUILD_TESTS
static_assert(nextInboundSequence(0) == 1);
static_assert(nextInboundSequence(1) == 2);
static_assert(storedInboundSequence(1) == 1);
static_assert(storedInboundSequence(0x7FFFFFFF) == 0);
#endif

class TransportCodec {
public:
	explicit constexpr TransportCodec(const TransportProfile &initProfile) :
		profile(initProfile) { }

	[[nodiscard]] const TransportProfile &getProfile() const {
		return profile;
	}

	[[nodiscard]] std::optional<uint16_t> decodeBodySize(uint16_t rawLengthHeader) const;
	/**
	 * @brief Encodes an outbound message using the complete active transport contract.
	 *
	 * @details Framing, encrypted payload layout, checksum, sequence and compression
	 * are all selected by the bound TransportProfile. Protocol only owns per-session
	 * crypto keys and sequence counters.
	 */
	void encodeOutbound(Protocol &protocol, OutputMessage &msg) const;
	/**
	 * @brief Validates and unwraps an inbound message using the complete active transport contract.
	 */
	[[nodiscard]] InboundTransportResult prepareInbound(Protocol &protocol, NetworkMessage &msg) const;

private:
	[[nodiscard]] InboundTransportStatus decryptXtea(Protocol &protocol, NetworkMessage &msg) const;
	void encryptXtea(Protocol &protocol, OutputMessage &msg) const;

	const TransportProfile &profile;
};

class TransportCodecs {
public:
	[[nodiscard]] static const TransportCodec &get(TransportProfileId id);
	[[nodiscard]] static const TransportCodec &rawClientFirst();
	[[nodiscard]] static const TransportCodec &currentLogin();
	[[nodiscard]] static const TransportCodec &currentGameSequence();
	[[nodiscard]] static const TransportCodec &currentGamePlain();
	[[nodiscard]] static const TransportCodec &legacyRawWithLoginHeader();
	[[nodiscard]] static const TransportCodec &legacyClassic();
};
