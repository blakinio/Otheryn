/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 */

#include "server/network/protocol/login_protocol_wire.hpp"

#include "server/network/message/outputmessage.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
#endif

namespace login_protocol_wire {
	void writeSessionKey(OutputMessage &output, std::string_view sessionKey) {
		output.addByte(SESSION_KEY_OPCODE);
		output.addString(std::string(sessionKey));
	}

	void writeModernCharacterList(
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

	void writeLegacyCharacterList(
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
