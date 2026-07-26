// Copyright 2026 Otheryn contributors. All rights reserved.
// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once

#include "modules/module_descriptor.hpp"
#include "server/network/protocol/protocol_profile.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <array>
	#include <functional>
	#include <span>
	#include <string>
	#include <vector>

	#include <fmt/format.h>
#endif

namespace module_registry_detail {
	inline constexpr std::array<ModuleId, 1> schedulerDependencies { ModuleId::EngineRuntime };
	inline constexpr std::array<ModuleId, 1> networkDependencies { ModuleId::EngineRuntime };
	inline constexpr std::array<ModuleId, 1> protocolDependencies { ModuleId::NetworkTransport };
	inline constexpr std::array<ModuleId, 2> sessionDependencies { ModuleId::Protocol, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 3> worldDependencies { ModuleId::Scheduler, ModuleId::Items, ModuleId::Creatures };
	inline constexpr std::array<ModuleId, 3> playerDependencies { ModuleId::World, ModuleId::Items, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 1> itemDependencies { ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 2> creatureDependencies { ModuleId::Scheduler, ModuleId::Items };
	inline constexpr std::array<ModuleId, 3> combatDependencies { ModuleId::Players, ModuleId::Creatures, ModuleId::Items };
	inline constexpr std::array<ModuleId, 1> persistenceDependencies { ModuleId::EngineRuntime };
	inline constexpr std::array<ModuleId, 2> luaDependencies { ModuleId::EngineRuntime, ModuleId::Scheduler };
	inline constexpr std::array<ModuleId, 1> observabilityDependencies { ModuleId::EngineRuntime };
	inline constexpr std::array<ModuleId, 3> wheelDependencies { ModuleId::Players, ModuleId::Combat, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 3> preyDependencies { ModuleId::Players, ModuleId::Creatures, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 4> charmDependencies { ModuleId::Players, ModuleId::Bestiary, ModuleId::Combat, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 3> bestiaryDependencies { ModuleId::Players, ModuleId::Creatures, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 3> bosstiaryDependencies { ModuleId::Players, ModuleId::Creatures, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 3> forgeDependencies { ModuleId::Players, ModuleId::Items, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 3> imbuementDependencies { ModuleId::Players, ModuleId::Items, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 3> marketDependencies { ModuleId::Players, ModuleId::Items, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 2> tradeDependencies { ModuleId::Players, ModuleId::Items };
	inline constexpr std::array<ModuleId, 2> bankDependencies { ModuleId::Players, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 2> guildDependencies { ModuleId::Players, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 3> houseDependencies { ModuleId::World, ModuleId::Players, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 2> achievementDependencies { ModuleId::Players, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 2> instanceDependencies { ModuleId::World, ModuleId::Creatures };
	inline constexpr std::array<ModuleId, 2> bossEncounterDependencies { ModuleId::World, ModuleId::Creatures };
	inline constexpr std::array<ModuleId, 3> raidDependencies { ModuleId::World, ModuleId::Creatures, ModuleId::LuaRuntime };
	inline constexpr std::array<ModuleId, 3> questDependencies { ModuleId::Players, ModuleId::LuaRuntime, ModuleId::Persistence };
	inline constexpr std::array<ModuleId, 2> npcDependencies { ModuleId::World, ModuleId::LuaRuntime };
	inline constexpr std::array<ModuleId, 2> spawnDependencies { ModuleId::World, ModuleId::Creatures };

	inline constexpr std::array<ModuleDescriptor, moduleIdCount()> currentDescriptors { {
		{ .id = ModuleId::EngineRuntime, .requirement = ModuleRequirement::CoreRequired },
		{ .id = ModuleId::Scheduler, .requirement = ModuleRequirement::CoreRequired, .dependencies = schedulerDependencies },
		{ .id = ModuleId::NetworkTransport, .requirement = ModuleRequirement::CoreRequired, .dependencies = networkDependencies },
		{ .id = ModuleId::Protocol, .requirement = ModuleRequirement::CoreRequired, .dependencies = protocolDependencies },
		{ .id = ModuleId::Sessions, .requirement = ModuleRequirement::CoreRequired, .dependencies = sessionDependencies },
		{ .id = ModuleId::World, .requirement = ModuleRequirement::CoreRequired, .dependencies = worldDependencies },
		{ .id = ModuleId::Players, .requirement = ModuleRequirement::CoreRequired, .dependencies = playerDependencies },
		{ .id = ModuleId::Items, .requirement = ModuleRequirement::CoreRequired, .dependencies = itemDependencies },
		{ .id = ModuleId::Creatures, .requirement = ModuleRequirement::CoreRequired, .dependencies = creatureDependencies },
		{ .id = ModuleId::Combat, .requirement = ModuleRequirement::CoreRequired, .dependencies = combatDependencies },
		{ .id = ModuleId::Persistence, .requirement = ModuleRequirement::CoreRequired, .dependencies = persistenceDependencies },
		{ .id = ModuleId::LuaRuntime, .requirement = ModuleRequirement::CoreRequired, .dependencies = luaDependencies },
		{ .id = ModuleId::Observability, .requirement = ModuleRequirement::CoreRequired, .dependencies = observabilityDependencies },
		{ .id = ModuleId::Wheel, .dependencies = wheelDependencies, .requiredCapabilities = moduleCapabilityMask(ModuleCapability::WheelProtocol) },
		{ .id = ModuleId::Prey, .dependencies = preyDependencies },
		{ .id = ModuleId::Charms, .dependencies = charmDependencies },
		{ .id = ModuleId::Bestiary, .dependencies = bestiaryDependencies },
		{ .id = ModuleId::Bosstiary, .dependencies = bosstiaryDependencies },
		{ .id = ModuleId::Forge, .dependencies = forgeDependencies },
		{ .id = ModuleId::Imbuements, .dependencies = imbuementDependencies, .requiredCapabilities = moduleCapabilityMask(ModuleCapability::ImbuementProtocol) },
		{ .id = ModuleId::Market, .dependencies = marketDependencies, .requiredCapabilities = moduleCapabilityMask(ModuleCapability::MarketProtocol) },
		{ .id = ModuleId::Trade, .dependencies = tradeDependencies },
		{ .id = ModuleId::Bank, .dependencies = bankDependencies },
		{ .id = ModuleId::Guilds, .dependencies = guildDependencies },
		{ .id = ModuleId::Houses, .dependencies = houseDependencies },
		{ .id = ModuleId::Achievements, .dependencies = achievementDependencies },
		{ .id = ModuleId::Instances, .dependencies = instanceDependencies },
		{ .id = ModuleId::BossEncounters, .dependencies = bossEncounterDependencies },
		{ .id = ModuleId::Raids, .dependencies = raidDependencies },
		{ .id = ModuleId::Quests, .dependencies = questDependencies },
		{ .id = ModuleId::Npcs, .dependencies = npcDependencies },
		{ .id = ModuleId::Spawns, .dependencies = spawnDependencies },
	} };

	inline constexpr std::array<ModuleId, moduleIdCount()> currentModuleSelection { {
		ModuleId::EngineRuntime,
		ModuleId::Scheduler,
		ModuleId::NetworkTransport,
		ModuleId::Protocol,
		ModuleId::Sessions,
		ModuleId::World,
		ModuleId::Players,
		ModuleId::Items,
		ModuleId::Creatures,
		ModuleId::Combat,
		ModuleId::Persistence,
		ModuleId::LuaRuntime,
		ModuleId::Observability,
		ModuleId::Wheel,
		ModuleId::Prey,
		ModuleId::Charms,
		ModuleId::Bestiary,
		ModuleId::Bosstiary,
		ModuleId::Forge,
		ModuleId::Imbuements,
		ModuleId::Market,
		ModuleId::Trade,
		ModuleId::Bank,
		ModuleId::Guilds,
		ModuleId::Houses,
		ModuleId::Achievements,
		ModuleId::Instances,
		ModuleId::BossEncounters,
		ModuleId::Raids,
		ModuleId::Quests,
		ModuleId::Npcs,
		ModuleId::Spawns,
	} };

	inline constexpr std::array<ModuleCapability, 3> knownCapabilities {
		ModuleCapability::MarketProtocol,
		ModuleCapability::ImbuementProtocol,
		ModuleCapability::WheelProtocol,
	};

	[[nodiscard]] constexpr size_t moduleIndex(ModuleId id) {
		return static_cast<size_t>(id);
	}

	inline void appendIssue(ModuleValidationResult &result, ModuleValidationCode code, ModuleId module, std::string message, ModuleId relatedModule = ModuleId::Count, ModuleCapability capability = ModuleCapability::None) {
		result.issues.push_back(ModuleValidationIssue {
			.code = code,
			.module = module,
			.relatedModule = relatedModule,
			.capability = capability,
			.message = std::move(message),
		});
	}
} // namespace module_registry_detail

class ModuleRegistry {
public:
	explicit ModuleRegistry(std::span<const ModuleDescriptor> descriptors) :
		registeredDescriptors(descriptors) { }

	[[nodiscard]] static const ModuleRegistry &current() {
		static const ModuleRegistry registry(module_registry_detail::currentDescriptors);
		return registry;
	}

	[[nodiscard]] static std::span<const ModuleId> currentSelection() {
		return module_registry_detail::currentModuleSelection;
	}

	[[nodiscard]] static uint64_t protocolCapabilities(const ProtocolProfile &profile) {
		uint64_t capabilities = moduleCapabilityMask(ModuleCapability::None);
		if (profile.hasFeature(ProtocolFeature::MarketPackets)) {
			capabilities |= moduleCapabilityMask(ModuleCapability::MarketProtocol);
		}
		if (profile.hasFeature(ProtocolFeature::ImbuementWindow)) {
			capabilities |= moduleCapabilityMask(ModuleCapability::ImbuementProtocol);
		}
		if (profile.hasFeature(ProtocolFeature::OfficialSkillWheelPayload)) {
			capabilities |= moduleCapabilityMask(ModuleCapability::WheelProtocol);
		}
		return capabilities;
	}

	[[nodiscard]] std::span<const ModuleDescriptor> descriptors() const {
		return registeredDescriptors;
	}

	[[nodiscard]] const ModuleDescriptor* find(ModuleId id) const {
		if (!isValidModuleId(id)) {
			return nullptr;
		}
		for (const auto &descriptor : registeredDescriptors) {
			if (descriptor.id == id) {
				return &descriptor;
			}
		}
		return nullptr;
	}

	[[nodiscard]] ModuleValidationResult validate(std::span<const ModuleId> selection, const ProtocolProfile &profile) const {
		return validate(selection, protocolCapabilities(profile));
	}

	[[nodiscard]] ModuleValidationResult validate(std::span<const ModuleId> selection, uint64_t availableCapabilities) const {
		using namespace module_registry_detail;
		ModuleValidationResult result;
		std::array<const ModuleDescriptor*, moduleIdCount()> descriptorIndex {};

		for (const auto &descriptor : registeredDescriptors) {
			if (!isValidModuleId(descriptor.id)) {
				appendIssue(result, ModuleValidationCode::InvalidModuleId, descriptor.id, fmt::format("module descriptor id {} is outside the legal module range", static_cast<unsigned int>(descriptor.id)));
				continue;
			}
			const auto index = moduleIndex(descriptor.id);
			if (descriptorIndex[index] != nullptr) {
				appendIssue(result, ModuleValidationCode::DuplicateDescriptor, descriptor.id, fmt::format("module descriptor '{}' is registered more than once", moduleIdName(descriptor.id)));
				continue;
			}
			descriptorIndex[index] = &descriptor;
		}

		for (const auto &descriptor : registeredDescriptors) {
			if (!isValidModuleId(descriptor.id) || descriptorIndex[moduleIndex(descriptor.id)] != &descriptor) {
				continue;
			}
			for (const auto dependency : descriptor.dependencies) {
				if (!isValidModuleId(dependency) || descriptorIndex[moduleIndex(dependency)] == nullptr) {
					appendIssue(result, ModuleValidationCode::UnknownDependency, descriptor.id, fmt::format("module '{}' depends on unregistered module '{}'", moduleIdName(descriptor.id), moduleIdName(dependency)), dependency);
				}
			}
		}

		if (!result.ok()) {
			return result;
		}

		std::array<uint8_t, moduleIdCount()> visitState {};
		std::function<bool(ModuleId)> visitDescriptor = [&](ModuleId id) {
			const auto index = moduleIndex(id);
			if (visitState[index] == 2) {
				return true;
			}
			if (visitState[index] == 1) {
				return false;
			}
			visitState[index] = 1;
			for (const auto dependency : descriptorIndex[index]->dependencies) {
				if (visitState[moduleIndex(dependency)] == 1) {
					appendIssue(result, ModuleValidationCode::DependencyCycle, id, fmt::format("module '{}' forms a dependency cycle through '{}'", moduleIdName(id), moduleIdName(dependency)), dependency);
					return false;
				}
				if (!visitDescriptor(dependency)) {
					return false;
				}
			}
			visitState[index] = 2;
			return true;
		};

		for (size_t index = 0; index < moduleIdCount(); ++index) {
			if (descriptorIndex[index] != nullptr && visitState[index] == 0 && !visitDescriptor(static_cast<ModuleId>(index))) {
				return result;
			}
		}

		std::array<bool, moduleIdCount()> selected {};
		for (const auto id : selection) {
			if (!isValidModuleId(id) || descriptorIndex[moduleIndex(id)] == nullptr) {
				appendIssue(result, ModuleValidationCode::UnknownSelection, id, fmt::format("profile selects unregistered module '{}'", moduleIdName(id)));
				continue;
			}
			const auto index = moduleIndex(id);
			if (selected[index]) {
				appendIssue(result, ModuleValidationCode::DuplicateSelection, id, fmt::format("profile selects module '{}' more than once", moduleIdName(id)));
				continue;
			}
			selected[index] = true;
		}

		for (size_t index = 0; index < moduleIdCount(); ++index) {
			const auto* descriptor = descriptorIndex[index];
			if (descriptor == nullptr) {
				continue;
			}
			if ((descriptor->requirement == ModuleRequirement::CoreRequired || descriptor->requirement == ModuleRequirement::ProfileRequired) && !selected[index]) {
				appendIssue(result, ModuleValidationCode::MissingRequiredModule, descriptor->id, fmt::format("required module '{}' is not selected", moduleIdName(descriptor->id)));
			}
		}

		for (size_t index = 0; index < moduleIdCount(); ++index) {
			const auto* descriptor = descriptorIndex[index];
			if (descriptor == nullptr || !selected[index]) {
				continue;
			}
			for (const auto dependency : descriptor->dependencies) {
				if (!selected[moduleIndex(dependency)]) {
					appendIssue(result, ModuleValidationCode::MissingDependency, descriptor->id, fmt::format("module '{}' requires selected dependency '{}'", moduleIdName(descriptor->id), moduleIdName(dependency)), dependency);
				}
			}
			const auto missingCapabilities = descriptor->requiredCapabilities & ~availableCapabilities;
			for (const auto capability : knownCapabilities) {
				if ((missingCapabilities & moduleCapabilityMask(capability)) != 0) {
					appendIssue(result, ModuleValidationCode::MissingCapability, descriptor->id, fmt::format("module '{}' requires protocol capability '{}'", moduleIdName(descriptor->id), moduleCapabilityName(capability)), ModuleId::Count, capability);
				}
			}
		}

		if (!result.ok()) {
			return result;
		}

		visitState.fill(0);
		std::function<void(ModuleId)> appendStartupOrder = [&](ModuleId id) {
			const auto index = moduleIndex(id);
			if (visitState[index] == 2) {
				return;
			}
			visitState[index] = 1;
			for (const auto dependency : descriptorIndex[index]->dependencies) {
				appendStartupOrder(dependency);
			}
			visitState[index] = 2;
			result.startupOrder.push_back(id);
		};

		for (size_t index = 0; index < moduleIdCount(); ++index) {
			if (selected[index]) {
				appendStartupOrder(static_cast<ModuleId>(index));
			}
		}
		return result;
	}

private:
	std::span<const ModuleDescriptor> registeredDescriptors;
};

[[nodiscard]] inline std::string formatModuleValidationIssues(const ModuleValidationResult &result) {
	std::string message;
	for (const auto &issue : result.issues) {
		if (!message.empty()) {
			message += "; ";
		}
		message += issue.message;
	}
	return message;
}
