/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "game/scheduling/save_manager.hpp"

#include "config/configmanager.hpp"
#include "creatures/players/grouping/guild.hpp"
#include "game/game.hpp"
#include "game/scheduling/player_persistence_state.hpp"
#include "io/ioguild.hpp"
#include "io/iologindata.hpp"
#include "kv/kv.hpp"
#include "lib/di/container.hpp"
#include "creatures/players/player.hpp"

SaveManager::SaveManager(ThreadPool &threadPool, KVStore &kvStore, Logger &logger, Game &game) :
	threadPool(threadPool), kv(kvStore), logger(logger), game(game) { }

SaveManager &SaveManager::getInstance() {
	return inject<SaveManager>();
}

bool SaveManager::saveAll() {
	Benchmark bm_saveAll;
	bool allSucceeded = true;
	logger.info("Saving server...");
	Benchmark bm_players;
	const auto &players = game.getPlayers();
	const bool savePlayersInParallel = threadPool.get_thread_count() > 1 && players.size() > 1;
	std::vector<std::pair<std::future<bool>, std::string>> pending;
	logger.info("Saving {} players...", players.size());
	if (savePlayersInParallel) {
		pending.reserve(players.size());
	}

	for (const auto &[_, player] : players) {
		if (player->isDead()) {
			player->loginPosition = player->getTemplePosition();
		} else if (player->loginPosition != player->getTemplePosition()) {
			player->loginPosition = player->getPosition();
		}

		if (savePlayersInParallel) {
			auto fut = threadPool.submit_task([this, player] {
				return doSavePlayer(player);
			});
			pending.emplace_back(std::move(fut), player->getName());
		} else {
			try {
				if (!doSavePlayer(player)) {
					allSucceeded = false;
				}
			} catch (const std::exception &e) {
				allSucceeded = false;
				logger.error("Failed to save player {}: {}", player->getName(), e.what());
			}
		}
	}

	for (auto &[future, name] : pending) {
		try {
			if (!future.get()) {
				allSucceeded = false;
			}
		} catch (const std::exception &e) {
			allSucceeded = false;
			logger.error("Failed to save player {}: {}", name, e.what());
		}
	}

	double duration_players = bm_players.duration();
	if (duration_players > 1000.0) {
		logger.info("Players saved in {:.2f} seconds.", duration_players / 1000.0);
	} else {
		logger.info("Players saved in {} milliseconds.", duration_players);
	}

	Benchmark bm_guilds;
	const auto &guilds = game.getGuilds();
	for (const auto &[_, guild] : guilds) {
		if (!saveGuild(guild)) {
			allSucceeded = false;
		}
	}
	double duration_guilds = bm_guilds.duration();
	if (duration_guilds > 1000.0) {
		logger.info("Guilds saved in {:.2f} seconds.", duration_guilds / 1000.0);
	} else {
		logger.info("Guilds saved in {} milliseconds.", duration_guilds);
	}

	if (!saveMap()) {
		allSucceeded = false;
	}
	if (!saveKV()) {
		allSucceeded = false;
	}

	double duration_saveAll = bm_saveAll.duration();
	if (duration_saveAll > 1000.0) {
		logger.info("Server saved in {:.2f} seconds.", duration_saveAll / 1000.0);
	} else {
		logger.info("Server saved in {} milliseconds.", duration_saveAll);
	}

	return allSucceeded;
}

void SaveManager::scheduleAll() {
	auto scheduledAt = std::chrono::steady_clock::now();
	m_scheduledAt = scheduledAt;

	// Disable save async if the config is set to false
	if (!g_configManager().getBoolean(TOGGLE_SAVE_ASYNC)) {
		if (!saveAll()) {
			logger.error("Scheduled server save completed with one or more failures.");
		}
		return;
	}

	threadPool.detach_task([this, scheduledAt]() {
		if (m_scheduledAt.load() != scheduledAt) {
			logger.warn("Skipping save for server because another save has been scheduled.");
			return;
		}
		if (!saveAll()) {
			logger.error("Scheduled server save completed with one or more failures.");
		}
	});
}

std::shared_ptr<PlayerPersistenceState> SaveManager::persistenceStateFor(const std::shared_ptr<Player> &player) {
	std::lock_guard lock(m_playerPersistenceMutex);
	for (auto it = m_playerPersistenceStates.begin(); it != m_playerPersistenceStates.end();) {
		if (it->first.expired()) {
			it = m_playerPersistenceStates.erase(it);
		} else {
			++it;
		}
	}

	const std::weak_ptr<Player> owner = player;
	if (const auto it = m_playerPersistenceStates.find(owner); it != m_playerPersistenceStates.end()) {
		return it->second;
	}

	auto state = std::make_shared<PlayerPersistenceState>();
	m_playerPersistenceStates.emplace(owner, state);
	return state;
}

void SaveManager::schedulePlayer(std::weak_ptr<Player> playerPtr) {
	auto playerToSave = playerPtr.lock();
	if (!playerToSave) {
		logger.debug("Skipping save for player because player is no longer online.");
		return;
	}

	// Disable save async if the config is set to false
	if (!g_configManager().getBoolean(TOGGLE_SAVE_ASYNC)) {
		if (g_game().getGameState() == GAME_STATE_NORMAL) {
			logger.debug("Saving player {}.", playerToSave->getName());
		}
		doSavePlayer(playerToSave);
		return;
	}

	auto state = persistenceStateFor(playerToSave);
	state->markDirty();
	scheduleDirtyPlayer(playerPtr, std::move(state));
}

void SaveManager::scheduleDirtyPlayer(std::weak_ptr<Player> playerPtr, std::shared_ptr<PlayerPersistenceState> state) {
	const auto generation = state->beginCheckpoint();
	if (!generation.has_value()) {
		logger.debug("Coalescing player save because a checkpoint is already in flight or no dirty generation exists.");
		return;
	}

	auto playerToSave = playerPtr.lock();
	if (!playerToSave) {
		state->acknowledgeFailure(*generation);
		logger.debug("Skipping save for player because player is no longer online.");
		return;
	}

	logger.debug("Scheduling player {} generation {} for saving.", playerToSave->getName(), *generation);
	threadPool.detach_task([this, playerPtr, state = std::move(state), generation = *generation]() {
		auto player = playerPtr.lock();
		if (!player) {
			state->acknowledgeFailure(generation);
			logger.debug("Skipping save for player because player is no longer online.");
			return;
		}

		bool saveSuccess = false;
		try {
			saveSuccess = doSavePlayer(player);
		} catch (const std::exception &e) {
			state->acknowledgeFailure(generation);
			logger.error("Failed to save player {} generation {}: {}", player->getName(), generation, e.what());
			return;
		} catch (...) {
			state->acknowledgeFailure(generation);
			logger.error("Failed to save player {} generation {} because of an unknown exception.", player->getName(), generation);
			return;
		}

		if (!saveSuccess) {
			if (!state->acknowledgeFailure(generation)) {
				logger.error("Failed to acknowledge player {} generation {} save failure.", player->getName(), generation);
			}
			return;
		}

		if (!state->acknowledgeSuccess(generation)) {
			logger.error("Failed to acknowledge player {} generation {} save success.", player->getName(), generation);
			return;
		}

		if (state->isDirty() && player->isOnline() && game.getGameState() != GAME_STATE_SHUTDOWN) {
			scheduleDirtyPlayer(player, state);
		}
	});
}

bool SaveManager::doSavePlayer(std::shared_ptr<Player> player) {
	if (!player) {
		logger.debug("Failed to save player because player is null.");
		return false;
	}

	Benchmark bm_savePlayer;
	Player::PlayerLock lock(player);
	if (g_game().getGameState() == GAME_STATE_NORMAL) {
		logger.debug("Saving player {}.", player->getName());
	}

	bool saveSuccess = IOLoginData::savePlayer(player);
	if (!saveSuccess) {
		logger.error("Failed to save player {}.", player->getName());
	}

	auto duration = bm_savePlayer.duration();
	logger.debug("Saving player {} took {} milliseconds.", player->getName(), duration);
	return saveSuccess;
}

bool SaveManager::savePlayer(std::shared_ptr<Player> player) {
	if (!player) {
		logger.debug("Failed to save player because player is null.");
		return false;
	}
	if (player->isOnline() && g_game().getGameState() != GAME_STATE_SHUTDOWN) {
		schedulePlayer(player);
		return true;
	}
	return doSavePlayer(player);
}

bool SaveManager::saveGuild(std::shared_ptr<Guild> guild) {
	if (!guild) {
		logger.debug("Failed to save guild because guild is null.");
		return false;
	}

	Benchmark bm_saveGuild;
	logger.debug("Saving guild {}...", guild->getName());
	const bool saveSuccess = IOGuild::saveGuild(guild);
	if (!saveSuccess) {
		logger.error("Failed to save guild {}.", guild->getName());
	}

	auto duration = bm_saveGuild.duration();
	logger.debug("Saving guild {} took {} milliseconds.", guild->getName(), duration);
	return saveSuccess;
}

bool SaveManager::saveMap() {
	Benchmark bm_saveMap;
	logger.debug("Saving map...");
	const bool saveSuccess = Map::save();
	if (!saveSuccess) {
		logger.error("Failed to save map.");
	}

	auto duration = bm_saveMap.duration();
	logger.debug("Map saved in {} milliseconds.", duration);
	return saveSuccess;
}

bool SaveManager::saveKV() {
	Benchmark bm_saveKV;
	logger.debug("Saving key-value store...");
	const bool saveSuccess = kv.saveAll();
	if (!saveSuccess) {
		logger.error("Failed to save key-value store.");
	}

	auto duration = bm_saveKV.duration();
	logger.debug("Key-value store saved in {} milliseconds.", duration);
	return saveSuccess;
}
