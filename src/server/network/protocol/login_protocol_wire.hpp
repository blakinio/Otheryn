/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#pragma once

#include "server/network/message/outputmessage.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <cstddef>
	#include <cstdint>
	#include <limits>
	#include <span>
	#include <string>
	#include <string_view>
#endif

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

	inline void writeSessionKey(OutputMessage &output, std::string_view sessionKey) {
		output.addByte(SESSION_KEY_OPCODE);
		output.addString(std::string(sessionKey));
	}

	inline void writeModernCharacterList(
		OutputMessage &output,
		std::span<const ModernWorld> worlds,
		std::span<const ModernCharacter> characters,
		const ModernAccountTail &account
	) {
		output.addByte(CHARACTER_LIST_OPCODE);

		const auto worldCount = static_cast<uint8_t>(std::min(worlds.size(), MAX_CHARACTER_COUNT));
		output.addByte(worldCount);
		for (size_t index = 0; index < worldCount; ++index) {
			const auto &world = worlds[index];
			output.addByte(world.id);
			output.addString(world.name);
			output.addString(world.host);
			output.add<uint16_t>(world.port);
			output.addByte(world.previewState);
		}

		const auto characterCount = static_cast<uint8_t>(std::min(characters.size(), MAX_CHARACTER_COUNT));
		output.addByte(characterCount);
		for (size_t index = 0; index < characterCount; ++index) {
			const auto &character = characters[index];
			output.addByte(character.worldId);
			output.addString(character.name);
		}

		output.addByte(static_cast<uint8_t>(account.status));
		output.addByte(static_cast<uint8_t>(account.subscription));
		output.add<uint32_t>(account.premiumExpiry);
	}

	inline void writeLegacyCharacterList(
		OutputMessage &output,
		std::span<const LegacyCharacter> characters,
		uint16_t premiumDays
	) {
		output.addByte(CHARACTER_LIST_OPCODE);

		const auto characterCount = static_cast<uint8_t>(std::min(characters.size(), MAX_CHARACTER_COUNT));
		output.addByte(characterCount);
		for (size_t index = 0; index < characterCount; ++index) {
			const auto &character = characters[index];
			output.addString(character.name);
			output.addString(character.worldName);
			output.add<uint32_t>(character.worldIp);
			output.add<uint16_t>(character.worldPort);
		}

		output.add<uint16_t>(premiumDays);
	}
}
