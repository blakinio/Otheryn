/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "lib/thread/thread_pool.hpp"
#include "game/scheduling/player_checkpoint_attempt.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <map>
	#include <memory>
	#include <mutex>
	#include <vector>
#endif

class KVStore;
class Logger;
class Game;
class Player;
class Guild;

class SaveManager {
public:
	explicit SaveManager(ThreadPool &threadPool, KVStore &kvStore, Logger &logger, Game &game);

	SaveManager(const SaveManager &) = delete;
	void operator=(const SaveManager &) = delete;

	static SaveManager &getInstance();

	bool saveAll();
	void scheduleAll();

	bool savePlayer(std::shared_ptr<Player> player);

	/**
	 * Performs the bounded synchronous final save for an exact Player object.
	 *
	 * The method marks the post-logout state dirty, waits only a fixed interval
	 * for older checkpoint ownership, and executes at most a finite number of
	 * exact-generation attempts. It never detaches work or steals an in-flight
	 * generation.
	 */
	bool savePlayerFinal(std::shared_ptr<Player> player);
	bool saveGuild(std::shared_ptr<Guild> guild);

	/**
	 * Marks a persistence-relevant mutation on the exact live Player object.
	 *
	 * This static marker advances the shared exact-owner dirty generation and
	 * publishes only bounded process-level dirty gauges when a new dirty interval
	 * begins. It does not schedule a save or change checkpoint ownership.
	 */
	static void markPlayerDirty(const std::shared_ptr<Player> &player);

private:
	bool saveMap();
	bool saveKV();

	/**
	 * Schedules saving the current online player object.
	 *
	 * The weak pointer is intentional: GUID or player runtime ID re-resolution
	 * can point at a later session for the same character, while the save must
	 * target the object that requested it or skip if that object is gone.
	 */
	bool schedulePlayer(std::weak_ptr<Player> player);
	bool scheduleDirtyPlayer(std::weak_ptr<Player> player, std::shared_ptr<PlayerPersistenceState> state);
	static std::shared_ptr<PlayerPersistenceState> persistenceStateFor(const std::shared_ptr<Player> &player);
	static std::vector<std::shared_ptr<PlayerPersistenceState>> persistenceStatesSnapshot();
	static int64_t currentCheckpointTimestampSeconds();
	static void publishPlayerDirtyGauges();
	void publishPlayerCheckpointGauges();

	/**
	 * Saves a pinned player object.
	 *
	 * Keep the strong owner for the duration of serialization. Replacing this
	 * with GUID-only lookup would change which player generation is saved.
	 */
	bool doSavePlayer(std::shared_ptr<Player> player);

	std::atomic<std::chrono::steady_clock::time_point> m_scheduledAt;
	inline static std::mutex m_playerPersistenceMutex;
	inline static std::map<std::weak_ptr<Player>, std::shared_ptr<PlayerPersistenceState>, std::owner_less<std::weak_ptr<Player>>> m_playerPersistenceStates;
	inline static PlayerCheckpointTelemetry m_playerCheckpointTelemetry;
	PlayerCheckpointQueueAdmission m_playerCheckpointQueueAdmission;

	ThreadPool &threadPool;
	KVStore &kv;
	Logger &logger;
	Game &game;
};

constexpr auto g_saveManager = SaveManager::getInstance;
