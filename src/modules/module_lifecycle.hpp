// Copyright 2026 Otheryn contributors. All rights reserved.
// SPDX-License-Identifier: GPL-3.0-or-later

#pragma once

#include "config/game_profile.hpp"
#include "modules/module_registry.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <array>
	#include <functional>
	#include <optional>
	#include <span>
	#include <stdexcept>
	#include <string>
	#include <string_view>
	#include <vector>

	#include <fmt/format.h>
#endif

enum class ModuleLifecycleState : uint8_t {
	Configuring,
	Starting,
	Ready,
	Failed,
	Stopping,
	Stopped,
};

struct ModuleLifecycleParticipant {
	ModuleId id = ModuleId::EngineRuntime;
	std::string name;
	std::function<void()> start;
	std::function<void()> stop;
};

class ModuleCompositionRoot {
public:
	explicit ModuleCompositionRoot(const GameProfile &profile, const ModuleRegistry &registry = ModuleRegistry::current()) :
		ModuleCompositionRoot(
			profile.enabledModules,
			resolveProtocolCapabilities(profile),
			registry
		) { }

	ModuleCompositionRoot(std::span<const ModuleId> selection, uint64_t availableCapabilities, const ModuleRegistry &registry) :
		selectedModules(selection.begin(), selection.end()) {
		const auto validation = registry.validate(selectedModules, availableCapabilities);
		if (!validation.ok()) {
			throw std::invalid_argument("module composition graph is invalid: " + formatModuleValidationIssues(validation));
		}
		startupOrder = validation.startupOrder;
		for (const auto id : selectedModules) {
			selected[moduleIndex(id)] = true;
		}
	}

	ModuleCompositionRoot(const ModuleCompositionRoot &) = delete;
	ModuleCompositionRoot &operator=(const ModuleCompositionRoot &) = delete;
	ModuleCompositionRoot(ModuleCompositionRoot &&) = delete;
	ModuleCompositionRoot &operator=(ModuleCompositionRoot &&) = delete;

	~ModuleCompositionRoot() {
		stop();
	}

	[[nodiscard]] bool registerParticipant(ModuleLifecycleParticipant participant, std::string &error) {
		if (state != ModuleLifecycleState::Configuring) {
			error = "module lifecycle registration is closed";
			return false;
		}
		if (!isValidModuleId(participant.id) || !selected[moduleIndex(participant.id)]) {
			error = fmt::format("module '{}' is not selected by the game profile", moduleIdName(participant.id));
			return false;
		}
		if (participants[moduleIndex(participant.id)].has_value()) {
			error = fmt::format("module '{}' already has a lifecycle participant", moduleIdName(participant.id));
			return false;
		}
		if (participant.name.empty()) {
			error = fmt::format("module '{}' lifecycle participant has no name", moduleIdName(participant.id));
			return false;
		}
		if (!participant.start || !participant.stop) {
			error = fmt::format("module '{}' lifecycle participant requires start and stop callbacks", moduleIdName(participant.id));
			return false;
		}

		participants[moduleIndex(participant.id)] = std::move(participant);
		error.clear();
		return true;
	}

	[[nodiscard]] bool start(std::string &error) {
		if (state != ModuleLifecycleState::Configuring) {
			error = "module composition root can only be started once";
			return false;
		}

		state = ModuleLifecycleState::Starting;
		for (const auto id : startupOrder) {
			auto &participant = participants[moduleIndex(id)];
			if (!participant.has_value()) {
				continue;
			}

			try {
				participant->start();
				startedModules.push_back(id);
			} catch (const std::exception &exception) {
				error = fmt::format("module '{}' participant '{}' failed to start: {}", moduleIdName(id), participant->name, exception.what());
				rollbackStartedParticipants();
				state = ModuleLifecycleState::Failed;
				return false;
			} catch (...) {
				error = fmt::format("module '{}' participant '{}' failed to start with an unknown exception", moduleIdName(id), participant->name);
				rollbackStartedParticipants();
				state = ModuleLifecycleState::Failed;
				return false;
			}
		}

		state = ModuleLifecycleState::Ready;
		error.clear();
		return true;
	}

	void stop() noexcept {
		if (state == ModuleLifecycleState::Stopped || state == ModuleLifecycleState::Stopping) {
			return;
		}
		if (startedModules.empty()) {
			if (state != ModuleLifecycleState::Failed) {
				state = ModuleLifecycleState::Stopped;
			}
			return;
		}

		state = ModuleLifecycleState::Stopping;
		stopStartedParticipants();
		state = ModuleLifecycleState::Stopped;
	}

	[[nodiscard]] ModuleLifecycleState getState() const noexcept {
		return state;
	}

	[[nodiscard]] bool isReady() const noexcept {
		return state == ModuleLifecycleState::Ready;
	}

	[[nodiscard]] std::span<const ModuleId> getStartupOrder() const noexcept {
		return startupOrder;
	}

	[[nodiscard]] std::span<const ModuleId> getStartedModules() const noexcept {
		return startedModules;
	}

	[[nodiscard]] const std::vector<std::string> &getShutdownErrors() const noexcept {
		return shutdownErrors;
	}

private:
	[[nodiscard]] static size_t moduleIndex(ModuleId id) {
		return static_cast<size_t>(id);
	}

	[[nodiscard]] static uint64_t resolveProtocolCapabilities(const GameProfile &profile) {
		const auto* protocolProfile = ProtocolProfileRegistry::getProfile(profile.protocolProfile);
		if (protocolProfile == nullptr) {
			throw std::invalid_argument(fmt::format("game profile '{}' selects an unknown protocol profile", profile.id));
		}
		return ModuleRegistry::protocolCapabilities(*protocolProfile);
	}

	void rollbackStartedParticipants() noexcept {
		stopStartedParticipants();
	}

	void stopStartedParticipants() noexcept {
		for (auto iterator = startedModules.rbegin(); iterator != startedModules.rend(); ++iterator) {
			auto &participant = participants[moduleIndex(*iterator)];
			if (!participant.has_value()) {
				continue;
			}
			try {
				participant->stop();
			} catch (const std::exception &exception) {
				shutdownErrors.emplace_back(fmt::format("module '{}' participant '{}' failed to stop: {}", moduleIdName(*iterator), participant->name, exception.what()));
			} catch (...) {
				shutdownErrors.emplace_back(fmt::format("module '{}' participant '{}' failed to stop with an unknown exception", moduleIdName(*iterator), participant->name));
			}
		}
		startedModules.clear();
	}

	ModuleLifecycleState state = ModuleLifecycleState::Configuring;
	std::vector<ModuleId> selectedModules;
	std::vector<ModuleId> startupOrder;
	std::vector<ModuleId> startedModules;
	std::array<bool, moduleIdCount()> selected {};
	std::array<std::optional<ModuleLifecycleParticipant>, moduleIdCount()> participants;
	std::vector<std::string> shutdownErrors;
};
