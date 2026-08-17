/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "database/player_writer_fence_repository.hpp"
#include "lib/thread/thread_pool.hpp"
#include "game/scheduling/player_checkpoint_attempt.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstdint>
	#include <map>
	#include <memory>
	#include <mutex>
	#include <optional>
	#include <vector>
#endif

class KVStore;
class Logger;
class Game;
class Player;
class Guild;

struct DatabaseOutageDrainPlayerRemovalResult final {
	bool removed = false;
	bool finalSaveObserved = false;
	bool finalSaveSucceeded = false;
};

class SaveManager {
public:
	explicit SaveManager(ThreadPool &threadPool, KVStore &kvStore, Logger &logger, Game &game);

	SaveManager(const SaveManager &) = delete;
	void operator=(const SaveManager &) = delete;

	static SaveManager &getInstance();

	bool saveAll();
	void scheduleAll();

	bool savePlayer(std::shared_ptr<Player> player);

	[[nodiscard]] bool acquirePlayerWriterFence(const std::shared_ptr<Player> &player);
	[[nodiscard]] bool releasePlayerWriterFence(const std::shared_ptr<Player> &player);

	bool savePlayerFinal(std::shared_ptr<Player> player);

	DatabaseOutageDrainPlayerRemovalResult removePlayerForDatabaseOutageDrain(const std::shared_ptr<Player> &player);

	bool saveGuild(std::shared_ptr<Guild> guild);

	static void markPlayerDirty(const std::shared_ptr<Player> &player);

private:
	struct DatabaseOutageDrainSaveObservation final {
		const Player* player;
		bool observed;
		bool succeeded;
	};

	bool saveMap();
	bool saveKV();

	bool schedulePlayer(std::weak_ptr<Player> player);
	bool scheduleDirtyPlayer(std::weak_ptr<Player> player, std::shared_ptr<PlayerPersistenceState> state);
	static std::shared_ptr<PlayerPersistenceState> persistenceStateFor(const std::shared_ptr<Player> &player);
	static std::vector<std::shared_ptr<PlayerPersistenceState>> persistenceStatesSnapshot();
	static std::optional<PlayerWriterFenceContext> writerFenceContextFor(const std::shared_ptr<Player> &player);
	static void storeWriterFenceContext(const std::shared_ptr<Player> &player, const PlayerWriterFenceContext &context);
	static void eraseWriterFenceContext(const std::shared_ptr<Player> &player);
	static int64_t currentCheckpointTimestampSeconds();
	static void publishPlayerDirtyGauges();
	void publishPlayerCheckpointGauges();

	bool doSavePlayer(std::shared_ptr<Player> player, bool releaseWriterFence = false);

	std::atomic<std::chrono::steady_clock::time_point> m_scheduledAt;
	inline static std::mutex m_playerPersistenceMutex;
	inline static std::map<std::weak_ptr<Player>, std::shared_ptr<PlayerPersistenceState>, std::owner_less<std::weak_ptr<Player>>> m_playerPersistenceStates;
	inline static std::map<std::weak_ptr<Player>, PlayerWriterFenceContext, std::owner_less<std::weak_ptr<Player>>> m_playerWriterFenceContexts;
	inline static PlayerCheckpointTelemetry m_playerCheckpointTelemetry;
	inline static thread_local DatabaseOutageDrainSaveObservation m_databaseOutageDrainSaveObservation { nullptr, false, false };
	PlayerCheckpointQueueAdmission m_playerCheckpointQueueAdmission;

	ThreadPool &threadPool;
	KVStore &kv;
	Logger &logger;
	Game &game;
};

constexpr auto g_saveManager = SaveManager::getInstance;
