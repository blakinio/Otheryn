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
	#include <memory>
	#include <string>
	#include <string_view>
#endif

enum class GameProfileWorldType : uint8_t {
	Pvp,
	NoPvp,
	PvpEnforced,
};

struct GameProfileRules {
	GameProfileWorldType worldType = GameProfileWorldType::Pvp;

	[[nodiscard]] friend bool operator==(const GameProfileRules &, const GameProfileRules &) = default;
};

struct GameProfileContent {
	std::string coreDirectory = "data";
	std::string dataPackDirectory = "data-otservbr-global";
	std::string mapName = "canary";
	bool allowAnyDatapackFolder = false;
	bool loadCustomMaps = true;

	[[nodiscard]] friend bool operator==(const GameProfileContent &, const GameProfileContent &) = default;
};

struct GameProfileNetwork {
	uint16_t loginPort = 7171;
	uint16_t statusPort = 7171;
	uint16_t modernGamePort = 7172;
	uint16_t legacy1100GamePort = 7173;
	uint16_t legacy860GamePort = 7174;

	[[nodiscard]] friend bool operator==(const GameProfileNetwork &, const GameProfileNetwork &) = default;
};

struct GameProfile {
	std::string id = "current";
	ProtocolProfileId protocolProfile = ProtocolProfileId::Current;
	bool allowOldProtocolProfiles = true;
	GameProfileRules rules;
	GameProfileContent content;
	GameProfileNetwork network;

	[[nodiscard]] friend bool operator==(const GameProfile &, const GameProfile &) = default;
};

using GameProfileSnapshot = std::shared_ptr<const GameProfile>;

[[nodiscard]] constexpr std::string_view gameProfileWorldTypeName(GameProfileWorldType type) {
	switch (type) {
		case GameProfileWorldType::NoPvp:
			return "no-pvp";
		case GameProfileWorldType::PvpEnforced:
			return "pvp-enforced";
		case GameProfileWorldType::Pvp:
		default:
			return "pvp";
	}
}
