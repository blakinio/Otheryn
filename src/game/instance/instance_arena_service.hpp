/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "game/instance/instance_creature_binder.hpp"
#include "game/instance/instance_manager.hpp"
#include "game/movement/position.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <cstddef>
	#include <cstdint>
	#include <functional>
	#include <memory>
	#include <mutex>
	#include <optional>
	#include <string>
	#include <unordered_map>
	#include <vector>
#endif

class Monster;

// Bounded consumer of InstanceManager. It is deliberately not a generic
// dungeon framework and does not own a second instance registry or manager.
class InstanceArenaService {
public:
	using MonsterFactory = std::function<std::shared_ptr<Monster>(const Position &position)>;
	using CreatureRemover = std::function<void(uint32_t creatureId)>;
	using DelayedEventScheduler = std::function<void(uint32_t delayMs, std::function<void()> callback)>;
	using MessageNotifier = std::function<void(uint32_t playerId, const std::string &message)>;
	using PlayerEvacuator = std::function<void(uint32_t playerId, const Position &returnPosition)>;

	explicit InstanceArenaService(InstanceManager &manager);
	InstanceArenaService(
		InstanceManager &manager,
		MonsterFactory monsterFactory,
		CreatureRemover creatureRemover,
		DelayedEventScheduler eventScheduler,
		MessageNotifier messageNotifier,
		PlayerEvacuator playerEvacuator
	);

	InstanceArenaService(const InstanceArenaService &) = delete;
	InstanceArenaService &operator=(const InstanceArenaService &) = delete;

	// OAM-039 intentionally does not import legacy data-canary coordinates.
	// Map-owned integration may provide concrete regions later; the clean target
	// remains fail-closed with no configured arena regions by default.
	[[nodiscard]] static std::vector<InstanceMapRegion> configuredRegions();

	struct CreateResult {
		bool ok = false;
		InstanceId id = InstanceId::Invalid;
		std::string error;
	};

	[[nodiscard]] CreateResult createArena();
	bool closeArena(InstanceId id);
	[[nodiscard]] std::optional<InstanceState> getState(InstanceId id) const;
	[[nodiscard]] std::optional<InstanceMapRegion> getRegion(InstanceId id) const;

	[[nodiscard]] InstanceManager &getManager() noexcept {
		return manager;
	}

	[[nodiscard]] InstanceCreatureBinder &getBinder() noexcept {
		return binder;
	}

	[[nodiscard]] std::size_t activeArenaCount() const;

	struct EnterResult {
		bool ok = false;
		Position entryPosition;
		uint32_t monsterId = 0;
		std::string error;
	};

	static constexpr const char* MonsterName = "Cave Rat";
	static constexpr std::chrono::seconds ArenaTimeout { 15 * 60 };
	static constexpr std::chrono::seconds ArenaClosingWarningLeadTime { 2 * 60 };
	static_assert(ArenaClosingWarningLeadTime < ArenaTimeout, "the closing warning must fire before the arena times out");

	[[nodiscard]] EnterResult enterArena(uint32_t playerId, const Position &returnPosition);

	struct LeaveResult {
		bool ok = false;
		Position returnPosition;
		std::string error;
	};

	[[nodiscard]] LeaveResult leaveArena(uint32_t playerId);

	struct CloseResult {
		bool ok = false;
		Position evacuationPosition;
		std::string error;
	};

	[[nodiscard]] CloseResult closeArenaForPlayer(uint32_t playerId);
	[[nodiscard]] bool hasActiveSession(uint32_t playerId) const;
	void reapExpiredSessions();

private:
	struct PlayerSession {
		InstanceId instanceId = InstanceId::Invalid;
		Position returnPosition;
	};

	InstanceManager &manager;
	InstanceCreatureBinder binder;
	MonsterFactory monsterFactory;
	CreatureRemover creatureRemover;
	DelayedEventScheduler eventScheduler;
	MessageNotifier messageNotifier;
	PlayerEvacuator playerEvacuator;

	mutable std::mutex sessionMutex;
	std::unordered_map<uint32_t, PlayerSession> sessions;
};
