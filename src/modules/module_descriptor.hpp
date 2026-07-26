// Copyright 2026 Otheryn contributors. All rights reserved.
// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstddef>
	#include <cstdint>
	#include <span>
	#include <string>
	#include <string_view>
	#include <vector>
#endif

enum class ModuleId : uint8_t {
	EngineRuntime,
	Scheduler,
	NetworkTransport,
	Protocol,
	Sessions,
	World,
	Players,
	Items,
	Creatures,
	Combat,
	Persistence,
	LuaRuntime,
	Observability,
	Wheel,
	Prey,
	Charms,
	Bestiary,
	Bosstiary,
	Forge,
	Imbuements,
	Market,
	Trade,
	Bank,
	Guilds,
	Houses,
	Achievements,
	Instances,
	BossEncounters,
	Raids,
	Quests,
	Npcs,
	Spawns,
	Count,
};

enum class ModuleRequirement : uint8_t {
	CoreRequired,
	ProfileRequired,
	Optional,
};

enum class ModuleCapability : uint64_t {
	None = 0,
	MarketProtocol = 1ULL << 0,
	ImbuementProtocol = 1ULL << 1,
	WheelProtocol = 1ULL << 2,
};

[[nodiscard]] constexpr ModuleCapability operator|(ModuleCapability left, ModuleCapability right) {
	return static_cast<ModuleCapability>(static_cast<uint64_t>(left) | static_cast<uint64_t>(right));
}

[[nodiscard]] constexpr uint64_t moduleCapabilityMask(ModuleCapability capability) {
	return static_cast<uint64_t>(capability);
}

[[nodiscard]] constexpr size_t moduleIdCount() {
	return static_cast<size_t>(ModuleId::Count);
}

[[nodiscard]] constexpr bool isValidModuleId(ModuleId id) {
	return static_cast<size_t>(id) < moduleIdCount();
}

[[nodiscard]] constexpr std::string_view moduleIdName(ModuleId id) {
	switch (id) {
		case ModuleId::EngineRuntime:
			return "engine-runtime";
		case ModuleId::Scheduler:
			return "scheduler";
		case ModuleId::NetworkTransport:
			return "network-transport";
		case ModuleId::Protocol:
			return "protocol";
		case ModuleId::Sessions:
			return "sessions";
		case ModuleId::World:
			return "world";
		case ModuleId::Players:
			return "players";
		case ModuleId::Items:
			return "items";
		case ModuleId::Creatures:
			return "creatures";
		case ModuleId::Combat:
			return "combat";
		case ModuleId::Persistence:
			return "persistence";
		case ModuleId::LuaRuntime:
			return "lua-runtime";
		case ModuleId::Observability:
			return "observability";
		case ModuleId::Wheel:
			return "wheel";
		case ModuleId::Prey:
			return "prey";
		case ModuleId::Charms:
			return "charms";
		case ModuleId::Bestiary:
			return "bestiary";
		case ModuleId::Bosstiary:
			return "bosstiary";
		case ModuleId::Forge:
			return "forge";
		case ModuleId::Imbuements:
			return "imbuements";
		case ModuleId::Market:
			return "market";
		case ModuleId::Trade:
			return "trade";
		case ModuleId::Bank:
			return "bank";
		case ModuleId::Guilds:
			return "guilds";
		case ModuleId::Houses:
			return "houses";
		case ModuleId::Achievements:
			return "achievements";
		case ModuleId::Instances:
			return "instances";
		case ModuleId::BossEncounters:
			return "boss-encounters";
		case ModuleId::Raids:
			return "raids";
		case ModuleId::Quests:
			return "quests";
		case ModuleId::Npcs:
			return "npcs";
		case ModuleId::Spawns:
			return "spawns";
		case ModuleId::Count:
			break;
	}
	return "invalid-module";
}

[[nodiscard]] constexpr std::string_view moduleCapabilityName(ModuleCapability capability) {
	switch (capability) {
		case ModuleCapability::MarketProtocol:
			return "market-protocol";
		case ModuleCapability::ImbuementProtocol:
			return "imbuement-protocol";
		case ModuleCapability::WheelProtocol:
			return "wheel-protocol";
		case ModuleCapability::None:
			break;
	}
	return "none";
}

struct ModuleDescriptor {
	ModuleId id = ModuleId::EngineRuntime;
	ModuleRequirement requirement = ModuleRequirement::Optional;
	std::span<const ModuleId> dependencies;
	uint64_t requiredCapabilities = moduleCapabilityMask(ModuleCapability::None);
};

enum class ModuleValidationCode : uint8_t {
	InvalidModuleId,
	DuplicateDescriptor,
	UnknownDependency,
	DependencyCycle,
	UnknownSelection,
	DuplicateSelection,
	MissingRequiredModule,
	MissingDependency,
	MissingCapability,
};

struct ModuleValidationIssue {
	ModuleValidationCode code = ModuleValidationCode::InvalidModuleId;
	ModuleId module = ModuleId::EngineRuntime;
	ModuleId relatedModule = ModuleId::Count;
	ModuleCapability capability = ModuleCapability::None;
	std::string message;

	[[nodiscard]] friend bool operator==(const ModuleValidationIssue &, const ModuleValidationIssue &) = default;
};

struct ModuleValidationResult {
	std::vector<ModuleValidationIssue> issues;
	std::vector<ModuleId> startupOrder;

	[[nodiscard]] bool ok() const {
		return issues.empty();
	}
};
