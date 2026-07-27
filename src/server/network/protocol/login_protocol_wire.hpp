/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <span>
	#include <string>
	#include <string_view>
#endif

class OutputMessage;

namespace login_protocol_wire {
	inline constexpr uint8_t SESSION_KEY_OPCODE = 0x28;
	inline constexpr uint8_t CHARACTER_LIST_OPCODE = 0x64;
	inline constexpr size_t MAX_CHARACTER_COUNT = std::numeric_limits<uint8_t>::max();

	enum class AccountStatus : uint8_t {
		Ok = 0,
	};

	enum class SubscriptionStatus : uint8_t {
		Free = 0,
		Premium = 1,
	};

	struct ModernWorld {
		uint8_t id = 0;
		std::string name;
		std::string host;
		uint16_t port = 0;
		uint8_t previewState = 0;
	};

	struct ModernCharacter {
		uint8_t worldId = 0;
		std::string name;
	};

	struct LegacyCharacter {
		std::string name;
		std::string worldName;
		uint32_t worldIp = 0;
		uint16_t worldPort = 0;
	};

	struct ModernAccountTail {
		AccountStatus status = AccountStatus::Ok;
		SubscriptionStatus subscription = SubscriptionStatus::Free;
		uint32_t premiumExpiry = 0;
	};

	[[nodiscard]] constexpr ModernAccountTail makeModernAccountTail(bool premium, uint32_t premiumExpiry) {
		return {
			.status = AccountStatus::Ok,
			.subscription = premium ? SubscriptionStatus::Premium : SubscriptionStatus::Free,
			.premiumExpiry = premiumExpiry,
		};
	}

	void writeSessionKey(OutputMessage &output, std::string_view sessionKey);
	void writeModernCharacterList(
		OutputMessage &output,
		std::span<const ModernWorld> worlds,
		std::span<const ModernCharacter> characters,
		const ModernAccountTail &account
	);
	void writeLegacyCharacterList(
		OutputMessage &output,
		std::span<const LegacyCharacter> characters,
		uint16_t premiumDays
	);
}
