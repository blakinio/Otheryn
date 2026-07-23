/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/instance/instance_arena_service.hpp"

#include "creatures/monsters/monster.hpp"
#include "creatures/players/player.hpp"
#include "game/game.hpp"
#include "game/instance/instance_scoped_event.hpp"
#include "game/scheduling/dispatcher.hpp"

namespace {
	std::shared_ptr<Monster> createAndPlaceArenaMonster(const Position &position) {
		const auto &monster = Monster::createMonster(InstanceArenaService::MonsterName);
		if (!monster || !g_game().placeCreature(monster, position, false, true)) {
			return nullptr;
		}
		return monster;
	}

	void removeArenaCreature(uint32_t creatureId) {
		if (const auto &creature = g_game().getCreatureByID(creatureId)) {
			g_game().removeCreature(creature);
		}
	}

	void scheduleViaDispatcher(uint32_t delayMs, std::function<void()> callback) {
		g_dispatcher().scheduleEvent(delayMs, std::move(callback), "InstanceArenaService::closingWarning");
	}

	void notifyPlayerViaGame(uint32_t playerId, const std::string &message) {
		if (const auto &player = g_game().getPlayerByID(playerId)) {
			player->sendTextMessage(MESSAGE_EVENT_ADVANCE, message);
		}
	}

	void evacuatePlayerViaGame(uint32_t playerId, const Position &returnPosition) {
		if (const auto &player = g_game().getPlayerByID(playerId)) {
			g_game().internalTeleport(player, returnPosition, false);
		}
	}
} // namespace

InstanceArenaService::InstanceArenaService(InstanceManager &manager) :
	InstanceArenaService(manager, &createAndPlaceArenaMonster, &removeArenaCreature, &scheduleViaDispatcher, &notifyPlayerViaGame, &evacuatePlayerViaGame) { }

InstanceArenaService::InstanceArenaService(
	InstanceManager &manager,
	MonsterFactory monsterFactory,
	CreatureRemover creatureRemover,
	DelayedEventScheduler eventScheduler,
	MessageNotifier messageNotifier,
	PlayerEvacuator playerEvacuator
) :
	manager(manager),
	binder(manager), monsterFactory(std::move(monsterFactory)), creatureRemover(std::move(creatureRemover)),
	eventScheduler(std::move(eventScheduler)), messageNotifier(std::move(messageNotifier)), playerEvacuator(std::move(playerEvacuator)) { }

std::vector<InstanceMapRegion> InstanceArenaService::configuredRegions() {
	// Clean Otheryn intentionally does not inherit coordinates from the legacy
	// data-canary map. Map-owned integration must provide evidence-backed target
	// regions explicitly before a runtime owner constructs InstanceManager from
	// them. Returning no regions keeps the default bounded consumer fail-closed.
	return {};
}

InstanceArenaService::CreateResult InstanceArenaService::createArena() {
	auto result = manager.createInstance({ .name = "instance-test-arena", .timeout = ArenaTimeout });
	if (!result.ok) {
		return { .ok = false, .id = InstanceId::Invalid, .error = result.error };
	}

	if (!manager.activate(result.id)) {
		manager.close(result.id);
		return { .ok = false, .id = InstanceId::Invalid, .error = "failed to activate arena instance" };
	}

	return { .ok = true, .id = result.id, .error = {} };
}

bool InstanceArenaService::closeArena(InstanceId id) {
	return manager.close(id);
}

std::optional<InstanceState> InstanceArenaService::getState(InstanceId id) const {
	return manager.getState(id);
}

std::optional<InstanceMapRegion> InstanceArenaService::getRegion(InstanceId id) const {
	return manager.getRegion(id);
}

std::size_t InstanceArenaService::activeArenaCount() const {
	return manager.activeInstanceCount();
}

InstanceArenaService::EnterResult InstanceArenaService::enterArena(uint32_t playerId, const Position &returnPosition) {
	std::scoped_lock lock(sessionMutex);
	if (sessions.contains(playerId)) {
		return { .ok = false, .entryPosition = {}, .error = "You already have an active instance arena. Close it first." };
	}

	const auto created = createArena();
	if (!created.ok) {
		return { .ok = false, .entryPosition = {}, .error = created.error };
	}

	manager.setCleanupCallback(created.id, [this](InstanceId instanceId, const InstanceMapRegion &) {
		for (const auto creatureId : manager.getRegisteredCreatureIds(instanceId)) {
			creatureRemover(creatureId);
		}
	});

	const auto region = manager.getRegion(created.id);
	if (!region) {
		manager.close(created.id);
		return { .ok = false, .entryPosition = {}, .error = "internal error: created arena has no region" };
	}

	const Position entryPosition { region->minX, region->minY, region->minZ };
	const Position monsterPosition {
		static_cast<uint16_t>(region->minX + 4),
		static_cast<uint16_t>(region->minY + 3),
		region->minZ,
	};

	const auto &monster = monsterFactory(monsterPosition);
	if (!monster) {
		manager.close(created.id);
		return { .ok = false, .entryPosition = {}, .error = "failed to spawn the arena monster" };
	}

	if (!binder.bind(created.id, *monster)) {
		creatureRemover(monster->getID());
		manager.close(created.id);
		return { .ok = false, .entryPosition = {}, .error = "failed to register the arena monster" };
	}

	sessions.emplace(playerId, PlayerSession { .instanceId = created.id, .returnPosition = returnPosition });

	const InstanceScopedEvent scopedEvent(manager, created.id);
	const auto warningDelay = std::chrono::duration_cast<std::chrono::milliseconds>(ArenaTimeout - ArenaClosingWarningLeadTime);
	eventScheduler(static_cast<uint32_t>(warningDelay.count()), [this, scopedEvent, playerId] {
		scopedEvent.runIfLive([this, playerId] {
			messageNotifier(playerId, "Your instance arena will close automatically soon due to inactivity. Use /instancearena close to leave safely.");
		});
	});

	return { .ok = true, .entryPosition = entryPosition, .monsterId = monster->getID(), .error = {} };
}

InstanceArenaService::LeaveResult InstanceArenaService::leaveArena(uint32_t playerId) {
	std::scoped_lock lock(sessionMutex);
	const auto it = sessions.find(playerId);
	if (it == sessions.end()) {
		return { .ok = false, .returnPosition = {}, .error = "You do not have an active instance arena." };
	}
	return { .ok = true, .returnPosition = it->second.returnPosition, .error = {} };
}

InstanceArenaService::CloseResult InstanceArenaService::closeArenaForPlayer(uint32_t playerId) {
	std::scoped_lock lock(sessionMutex);
	const auto it = sessions.find(playerId);
	if (it == sessions.end()) {
		return { .ok = false, .evacuationPosition = {}, .error = "You do not have an active instance arena." };
	}

	const auto session = it->second;
	manager.close(session.instanceId);
	sessions.erase(it);
	return { .ok = true, .evacuationPosition = session.returnPosition, .error = {} };
}

bool InstanceArenaService::hasActiveSession(uint32_t playerId) const {
	std::scoped_lock lock(sessionMutex);
	return sessions.contains(playerId);
}

void InstanceArenaService::reapExpiredSessions() {
	std::vector<std::pair<uint32_t, Position>> evacuations;
	{
		std::scoped_lock lock(sessionMutex);
		for (auto it = sessions.begin(); it != sessions.end();) {
			const auto state = manager.getState(it->second.instanceId);
			if (!state || *state != InstanceState::Active) {
				evacuations.emplace_back(it->first, it->second.returnPosition);
				it = sessions.erase(it);
			} else {
				++it;
			}
		}
	}

	for (const auto &[playerId, returnPosition] : evacuations) {
		playerEvacuator(playerId, returnPosition);
	}
}
