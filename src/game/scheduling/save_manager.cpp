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
#include "database/player_writer_fence_repository.hpp"
#include "creatures/players/grouping/guild.hpp"
#include "game/game.hpp"
#include "game/scheduling/player_checkpoint_attempt.hpp"
#include "game/scheduling/player_persistence_state.hpp"
#include "io/ioguild.hpp"
#include "io/iologindata.hpp"
#include "kv/kv.hpp"
#include "lib/di/container.hpp"
#include "lib/metrics/metrics.hpp"
#include "creatures/players/player.hpp"

#include <mbedtls/ctr_drbg.h>
#include <mbedtls/entropy.h>

namespace {
	constexpr auto PLAYER_FINAL_SAVE_WAIT_TIMEOUT = std::chrono::seconds(5);
	constexpr uint8_t PLAYER_FINAL_SAVE_MAX_ATTEMPTS = 2;
	constexpr std::array<unsigned char, 24> PLAYER_WRITER_FENCE_PERSONALIZATION = {
		'o', 't', 'h', 'e', 'r', 'y', 'n', '-', 'w', 'r', 'i', 't', 'e', 'r', '-',
		'f', 'e', 'n', 'c', 'e', '-', '0', '0', '4'
	};

	class PlayerWriterFenceTokenSource final {
	public:
		PlayerWriterFenceTokenSource() {
			mbedtls_entropy_init(&entropy_);
			mbedtls_ctr_drbg_init(&drbg_);
			seeded_ = mbedtls_ctr_drbg_seed(
						  &drbg_,
						  mbedtls_entropy_func,
						  &entropy_,
						  PLAYER_WRITER_FENCE_PERSONALIZATION.data(),
						  PLAYER_WRITER_FENCE_PERSONALIZATION.size()
					  )
				== 0;
			if (!seeded_) {
				g_logger().error("Failed to seed player writer-fence CSPRNG; acquisition will fail closed.");
			}
		}

		~PlayerWriterFenceTokenSource() {
			mbedtls_ctr_drbg_free(&drbg_);
			mbedtls_entropy_free(&entropy_);
		}

		[[nodiscard]] std::optional<PlayerWriterFenceToken> next() {
			std::scoped_lock lock(mutex_);
			if (!seeded_) {
				return std::nullopt;
			}

			PlayerWriterFenceToken token {};
			if (mbedtls_ctr_drbg_random(&drbg_, token.data(), token.size()) != 0
			    || !PlayerWriterFenceRepository::isValidToken(token)) {
				return std::nullopt;
			}
			return token;
		}

	private:
		std::mutex mutex_;
		mbedtls_entropy_context entropy_ {};
		mbedtls_ctr_drbg_context drbg_ {};
		bool seeded_ = false;
	};

	PlayerWriterFenceTokenSource &playerWriterFenceTokenSource() {
		static PlayerWriterFenceTokenSource source;
		return source;
	}
}

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

int64_t SaveManager::currentCheckpointTimestampSeconds() {
	return std::chrono::duration_cast<std::chrono::seconds>(std::chrono::system_clock::now().time_since_epoch()).count();
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

std::vector<std::shared_ptr<PlayerPersistenceState>> SaveManager::persistenceStatesSnapshot() {
	std::vector<std::shared_ptr<PlayerPersistenceState>> states;
	std::lock_guard lock(m_playerPersistenceMutex);
	states.reserve(m_playerPersistenceStates.size());
	for (auto it = m_playerPersistenceStates.begin(); it != m_playerPersistenceStates.end();) {
		if (it->first.expired()) {
			it = m_playerPersistenceStates.erase(it);
			continue;
		}

		states.emplace_back(it->second);
		++it;
	}
	return states;
}

std::optional<PlayerWriterFenceContext> SaveManager::writerFenceContextFor(const std::shared_ptr<Player> &player) {
	if (!player) {
		return std::nullopt;
	}

	std::lock_guard lock(m_playerPersistenceMutex);
	const std::weak_ptr<Player> owner = player;
	const auto it = m_playerWriterFenceContexts.find(owner);
	return it == m_playerWriterFenceContexts.end() ? std::nullopt : std::optional<PlayerWriterFenceContext> { it->second };
}

void SaveManager::storeWriterFenceContext(
	const std::shared_ptr<Player> &player,
	const PlayerWriterFenceContext &context
) {
	if (!player) {
		return;
	}

	std::lock_guard lock(m_playerPersistenceMutex);
	m_playerWriterFenceContexts[std::weak_ptr<Player> { player }] = context;
}

void SaveManager::eraseWriterFenceContext(const std::shared_ptr<Player> &player) {
	if (!player) {
		return;
	}

	std::lock_guard lock(m_playerPersistenceMutex);
	m_playerWriterFenceContexts.erase(std::weak_ptr<Player> { player });
}

bool SaveManager::acquirePlayerWriterFence(const std::shared_ptr<Player> &player) {
	if (!player || player->getGUID() == 0) {
		logger.error("Player writer-fence acquisition failed because the player subject is missing.");
		return false;
	}
	if (writerFenceContextFor(player).has_value()) {
		logger.error("Player {} already owns a process-local writer-fence context.", player->getName());
		return false;
	}

	PlayerWriterFenceRepository repository;
	const auto loaded = repository.load(player->getGUID());
	if (loaded.result != PlayerWriterFenceResult::Applied
	    || PlayerWriterFenceRepository::isValidToken(loaded.context.writerToken)
	    || loaded.context.ownershipGeneration == std::numeric_limits<PlayerWriterFenceGeneration>::max()) {
		logger.error("Player {} durable writer-fence is unavailable for a new initial owner.", player->getName());
		return false;
	}

	const auto token = playerWriterFenceTokenSource().next();
	if (!token.has_value()) {
		logger.error("Player {} writer-fence token generation failed closed.", player->getName());
		return false;
	}

	PlayerWriterFenceContext desired {
		.playerId = player->getGUID(),
		.ownershipGeneration = loaded.context.ownershipGeneration + 1,
		.writerToken = *token,
		.stateRevision = loaded.context.stateRevision,
	};
	if (repository.acquire(desired) != PlayerWriterFenceResult::Applied) {
		logger.error("Player {} durable writer-fence acquisition was rejected.", player->getName());
		return false;
	}

	storeWriterFenceContext(player, desired);
	return true;
}

bool SaveManager::releasePlayerWriterFence(const std::shared_ptr<Player> &player) {
	const auto context = writerFenceContextFor(player);
	if (!context.has_value()) {
		logger.error("Player writer-fence release failed because no exact owner context exists.");
		return false;
	}

	if (PlayerWriterFenceRepository().release(*context) != PlayerWriterFenceResult::Applied) {
		logger.error("Player {} durable writer-fence release was rejected.", player->getName());
		return false;
	}

	eraseWriterFenceContext(player);
	return true;
}

void SaveManager::publishPlayerDirtyGauges() {
	const auto gauges = summarizePlayerCheckpointGauges(0, 0, persistenceStatesSnapshot());
	g_metrics().setGauge("player_checkpoint_dirty_owners", static_cast<int64_t>(gauges.dirtyOwners));
	g_metrics().setGauge("player_checkpoint_oldest_dirty_timestamp_seconds", gauges.oldestDirtyTimestampSeconds);
}

void SaveManager::publishPlayerCheckpointGauges() {
	const auto gauges = summarizePlayerCheckpointGauges(
		m_playerCheckpointQueueAdmission.capacity(),
		m_playerCheckpointQueueAdmission.outstanding(),
		persistenceStatesSnapshot()
	);
	g_metrics().setGauge("player_checkpoint_queue_capacity", static_cast<int64_t>(gauges.queueCapacity));
	g_metrics().setGauge("player_checkpoint_queue_outstanding", static_cast<int64_t>(gauges.queueOutstanding));
	g_metrics().setGauge("player_checkpoint_dirty_owners", static_cast<int64_t>(gauges.dirtyOwners));
	g_metrics().setGauge("player_checkpoint_oldest_dirty_timestamp_seconds", gauges.oldestDirtyTimestampSeconds);
}

void SaveManager::markPlayerDirty(const std::shared_ptr<Player> &player) {
	if (!player) {
		return;
	}

	auto state = persistenceStateFor(player);
	const bool hadDirtyTimestamp = state->dirtySinceTimestampSeconds().has_value();
	(void)state->markDirty(currentCheckpointTimestampSeconds());
	if (!hadDirtyTimestamp && state->dirtySinceTimestampSeconds().has_value()) {
		publishPlayerDirtyGauges();
	}
}

bool SaveManager::schedulePlayer(std::weak_ptr<Player> playerPtr) {
	auto playerToSave = playerPtr.lock();
	if (!playerToSave) {
		logger.debug("Skipping save for player because player is no longer online.");
		return false;
	}

	// Disable save async if the config is set to false
	if (!g_configManager().getBoolean(TOGGLE_SAVE_ASYNC)) {
		if (g_game().getGameState() == GAME_STATE_NORMAL) {
			logger.debug("Saving player {}.", playerToSave->getName());
		}
		doSavePlayer(playerToSave);
		return true;
	}

	auto state = persistenceStateFor(playerToSave);
	const bool hadDirtyTimestamp = state->dirtySinceTimestampSeconds().has_value();
	(void)state->markDirty(currentCheckpointTimestampSeconds());
	if (!hadDirtyTimestamp && state->dirtySinceTimestampSeconds().has_value()) {
		publishPlayerDirtyGauges();
	}
	return scheduleDirtyPlayer(playerPtr, std::move(state));
}

bool SaveManager::scheduleDirtyPlayer(std::weak_ptr<Player> playerPtr, std::shared_ptr<PlayerPersistenceState> state) {
	m_playerCheckpointTelemetry.recordRequest();
	g_metrics().addCounter("player_checkpoint_requests", 1);
	publishPlayerCheckpointGauges();

	const auto generation = state->beginCheckpoint();
	if (!generation.has_value()) {
		logger.debug("Coalescing player save because a checkpoint is already in flight or no dirty generation exists.");
		return true;
	}

	auto playerToSave = playerPtr.lock();
	if (!playerToSave) {
		(void)state->acknowledgeFailure(*generation);
		m_playerCheckpointTelemetry.recordFailure();
		g_metrics().addCounter("player_checkpoint_failures", 1, { { "reason", "owner_unavailable" } });
		publishPlayerCheckpointGauges();
		logger.debug("Skipping save for player because player is no longer online.");
		return false;
	}

	const auto admission = tryAdmitPlayerCheckpoint(m_playerCheckpointQueueAdmission, *state, *generation);
	if (admission.outcome == PlayerCheckpointQueueAdmissionOutcome::queueFull) {
		m_playerCheckpointTelemetry.recordQueueRejection();
		g_metrics().addCounter("player_checkpoint_queue_rejections", 1);
		publishPlayerCheckpointGauges();
		if (!admission.checkpointReleased) {
			logger.error("Failed to release player {} generation {} after checkpoint queue rejection.", playerToSave->getName(), *generation);
		}
		logger.warn(
			"Rejecting player {} generation {} checkpoint because the bounded queue is full ({}/{}); the generation remains dirty and requires a later explicit schedule.",
			playerToSave->getName(),
			*generation,
			m_playerCheckpointQueueAdmission.outstanding(),
			m_playerCheckpointQueueAdmission.capacity()
		);
		return false;
	}

	publishPlayerCheckpointGauges();
	logger.debug("Scheduling player {} generation {} for saving.", playerToSave->getName(), *generation);
	try {
		threadPool.detach_task([this, playerPtr, state, generation = *generation]() {
			PlayerCheckpointQueueSlot queueSlot(m_playerCheckpointQueueAdmission, [this] {
				publishPlayerCheckpointGauges();
			});
			auto player = playerPtr.lock();
			if (!player) {
				(void)state->acknowledgeFailure(generation);
				m_playerCheckpointTelemetry.recordFailure();
				g_metrics().addCounter("player_checkpoint_failures", 1, { { "reason", "owner_unavailable" } });
				publishPlayerCheckpointGauges();
				logger.debug("Skipping save for player because player is no longer online.");
				return;
			}

			m_playerCheckpointTelemetry.recordAttempt();
			g_metrics().addCounter("player_checkpoint_attempts", 1);
			metrics::method_latency checkpointLatency("player_checkpoint_save");
			const auto attempt = executePlayerCheckpointAttempt(*state, generation, [this, &player] {
				return doSavePlayer(player);
			});

			if (attempt.outcome == PlayerCheckpointAttemptOutcome::saved) {
				if (!attempt.acknowledgementAccepted) {
					m_playerCheckpointTelemetry.recordFailure();
					g_metrics().addCounter("player_checkpoint_failures", 1, { { "reason", "acknowledgement_rejected" } });
					publishPlayerCheckpointGauges();
					logger.error("Failed to acknowledge player {} generation {} save success.", player->getName(), generation);
					return;
				}

				m_playerCheckpointTelemetry.recordSuccess();
				g_metrics().addCounter("player_checkpoint_successes", 1);
				publishPlayerCheckpointGauges();
				if (attempt.followUpRequired && player->isOnline() && game.getGameState() != GAME_STATE_SHUTDOWN) {
					if (!queueSlot.release()) {
						logger.error("Failed to release player {} generation {} checkpoint queue slot before follow-up.", player->getName(), generation);
						return;
					}
					(void)scheduleDirtyPlayer(player, state);
				}
				return;
			}

			if (attempt.outcome == PlayerCheckpointAttemptOutcome::saveThrew) {
				m_playerCheckpointTelemetry.recordThrownAttempt();
				g_metrics().addCounter("player_checkpoint_failures", 1, { { "reason", "save_threw" } });
				g_metrics().addCounter("player_checkpoint_thrown_attempts", 1);
			} else {
				m_playerCheckpointTelemetry.recordFailure();
				g_metrics().addCounter("player_checkpoint_failures", 1, { { "reason", "save_failed" } });
			}
			publishPlayerCheckpointGauges();

			if (!attempt.acknowledgementAccepted) {
				logger.error("Failed to acknowledge player {} generation {} save failure.", player->getName(), generation);
			}

			if (attempt.outcome == PlayerCheckpointAttemptOutcome::saveThrew) {
				try {
					std::rethrow_exception(attempt.exception);
				} catch (const std::exception &e) {
					logger.error("Failed to save player {} generation {}: {}", player->getName(), generation, e.what());
				} catch (...) {
					logger.error("Failed to save player {} generation {} because of an unknown exception.", player->getName(), generation);
				}
			}
		});
		return true;
	} catch (const std::exception &e) {
		const bool queueReleased = m_playerCheckpointQueueAdmission.release();
		const bool checkpointReleased = state->abandonCheckpoint(*generation);
		m_playerCheckpointTelemetry.recordSubmissionFailure();
		g_metrics().addCounter("player_checkpoint_submission_failures", 1);
		publishPlayerCheckpointGauges();
		if (!queueReleased || !checkpointReleased) {
			logger.error("Failed to fully roll back player {} generation {} checkpoint admission after scheduling exception.", playerToSave->getName(), *generation);
		}
		logger.error("Failed to schedule player {} generation {} checkpoint: {}", playerToSave->getName(), *generation, e.what());
		return false;
	} catch (...) {
		const bool queueReleased = m_playerCheckpointQueueAdmission.release();
		const bool checkpointReleased = state->abandonCheckpoint(*generation);
		m_playerCheckpointTelemetry.recordSubmissionFailure();
		g_metrics().addCounter("player_checkpoint_submission_failures", 1);
		publishPlayerCheckpointGauges();
		if (!queueReleased || !checkpointReleased) {
			logger.error("Failed to fully roll back player {} generation {} checkpoint admission after unknown scheduling exception.", playerToSave->getName(), *generation);
		}
		logger.error("Failed to schedule player {} generation {} checkpoint because of an unknown exception.", playerToSave->getName(), *generation);
		return false;
	}
}

bool SaveManager::doSavePlayer(std::shared_ptr<Player> player, bool releaseWriterFence) {
	if (!player) {
		logger.debug("Failed to save player because player is null.");
		return false;
	}

	Benchmark bm_savePlayer;
	Player::PlayerLock lock(player);
	if (g_game().getGameState() == GAME_STATE_NORMAL) {
		logger.debug("Saving player {}.", player->getName());
	}

	auto writerFenceContext = writerFenceContextFor(player);
	if (!writerFenceContext.has_value()) {
		logger.error("Refusing player {} save because the durable writer-fence context is missing.", player->getName());
		return false;
	}

	bool saveSuccess = IOLoginData::savePlayer(player, *writerFenceContext);
	storeWriterFenceContext(player, *writerFenceContext);

	if (saveSuccess && releaseWriterFence) {
		const auto releaseResult = PlayerWriterFenceRepository().release(*writerFenceContext);
		if (releaseResult != PlayerWriterFenceResult::Applied) {
			logger.error("Failed to release player {} durable writer fence after protected save.", player->getName());
			saveSuccess = false;
		} else {
			eraseWriterFenceContext(player);
		}
	}

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

	const Player* const playerIdentity = player.get();
	const auto dispatchSave = [this, &player]() -> bool {
		const bool logoutStateFinalized = player->isOnline()
			&& player->getLastLogout() != 0
			&& player->getLastLogout() >= player->getLastLoginSaved();
		if (logoutStateFinalized) {
			return savePlayerFinal(std::move(player));
		}
		if (player->isOnline() && g_game().getGameState() != GAME_STATE_SHUTDOWN) {
			return schedulePlayer(player);
		}
		return doSavePlayer(player, true);
	};

	const bool saveSucceeded = dispatchSave();
	if (m_databaseOutageDrainSaveObservation.player == playerIdentity) {
		m_databaseOutageDrainSaveObservation.observed = true;
		m_databaseOutageDrainSaveObservation.succeeded = saveSucceeded;
	}
	return saveSucceeded;
}

DatabaseOutageDrainPlayerRemovalResult SaveManager::removePlayerForDatabaseOutageDrain(const std::shared_ptr<Player> &player) {
	DatabaseOutageDrainPlayerRemovalResult result;
	if (!player) {
		logger.error("Database outage drain removal failed because player is null.");
		return result;
	}
	if (m_databaseOutageDrainSaveObservation.player != nullptr) {
		logger.error("Database outage drain removal rejected nested save observation for player {}.", player->getName());
		return result;
	}

	m_databaseOutageDrainSaveObservation = {
		.player = player.get(),
		.observed = false,
		.succeeded = false,
	};

	try {
		player->removePlayer(true, true);
		result.removed = player->isRemoved();
		result.finalSaveObserved = m_databaseOutageDrainSaveObservation.observed;
		result.finalSaveSucceeded = result.finalSaveObserved && m_databaseOutageDrainSaveObservation.succeeded;
	} catch (const std::exception &e) {
		logger.error("Database outage drain removal for player {} threw: {}", player->getName(), e.what());
	} catch (...) {
		logger.error("Database outage drain removal for player {} threw an unknown exception.", player->getName());
	}

	m_databaseOutageDrainSaveObservation = {};
	if (!result.removed) {
		logger.error("Database outage drain failed to remove player {}.", player->getName());
	}
	if (!result.finalSaveObserved) {
		logger.error("Database outage drain observed no final save for player {}.", player->getName());
	} else if (!result.finalSaveSucceeded) {
		logger.error("Database outage drain final save failed for player {}.", player->getName());
	}
	return result;
}

bool SaveManager::savePlayerFinal(std::shared_ptr<Player> player) {
	if (!player) {
		logger.error("Final player save failed because player is null.");
		return false;
	}

	auto state = persistenceStateFor(player);
	const bool hadDirtyTimestamp = state->dirtySinceTimestampSeconds().has_value();
	(void)state->markDirty(currentCheckpointTimestampSeconds());
	if (!hadDirtyTimestamp && state->dirtySinceTimestampSeconds().has_value()) {
		publishPlayerDirtyGauges();
	}

	m_playerCheckpointTelemetry.recordRequest();
	g_metrics().addCounter("player_checkpoint_requests", 1);
	publishPlayerCheckpointGauges();

	for (uint8_t attemptIndex = 0; attemptIndex < PLAYER_FINAL_SAVE_MAX_ATTEMPTS; ++attemptIndex) {
		const auto generation = state->beginFinalCheckpoint(PLAYER_FINAL_SAVE_WAIT_TIMEOUT);
		if (!generation.has_value()) {
			publishPlayerCheckpointGauges();
			logger.error(
				"Final save for player {} timed out waiting {} seconds for existing checkpoint ownership.",
				player->getName(),
				PLAYER_FINAL_SAVE_WAIT_TIMEOUT.count()
			);
			return false;
		}

		m_playerCheckpointTelemetry.recordAttempt();
		g_metrics().addCounter("player_checkpoint_attempts", 1);
		metrics::method_latency checkpointLatency("player_checkpoint_save");
		const auto attempt = executePlayerCheckpointAttempt(*state, *generation, [this, &player] {
			return doSavePlayer(player, false);
		});

		if (attempt.outcome != PlayerCheckpointAttemptOutcome::saved) {
			if (attempt.outcome == PlayerCheckpointAttemptOutcome::saveThrew) {
				m_playerCheckpointTelemetry.recordThrownAttempt();
				g_metrics().addCounter("player_checkpoint_failures", 1, { { "reason", "save_threw" } });
				g_metrics().addCounter("player_checkpoint_thrown_attempts", 1);
				try {
					std::rethrow_exception(attempt.exception);
				} catch (const std::exception &e) {
					logger.error("Final save for player {} generation {} threw: {}", player->getName(), *generation, e.what());
				} catch (...) {
					logger.error("Final save for player {} generation {} threw an unknown exception.", player->getName(), *generation);
				}
			} else {
				m_playerCheckpointTelemetry.recordFailure();
				g_metrics().addCounter("player_checkpoint_failures", 1, { { "reason", "save_failed" } });
				logger.error("Final save for player {} generation {} failed.", player->getName(), *generation);
			}
			publishPlayerCheckpointGauges();
			if (!attempt.acknowledgementAccepted) {
				logger.error("Failed to acknowledge player {} generation {} final-save failure.", player->getName(), *generation);
			}
			return false;
		}

		if (!attempt.acknowledgementAccepted) {
			m_playerCheckpointTelemetry.recordFailure();
			g_metrics().addCounter("player_checkpoint_failures", 1, { { "reason", "acknowledgement_rejected" } });
			publishPlayerCheckpointGauges();
			logger.error("Failed to acknowledge player {} generation {} final-save success.", player->getName(), *generation);
			return false;
		}

		m_playerCheckpointTelemetry.recordSuccess();
		g_metrics().addCounter("player_checkpoint_successes", 1);
		publishPlayerCheckpointGauges();
		if (!attempt.followUpRequired && !state->isDirty()) {
			if (!releasePlayerWriterFence(player)) {
				logger.error("Final save for player {} committed but durable writer-fence release failed.", player->getName());
				return false;
			}
			return true;
		}
	}

	logger.error(
		"Final save for player {} exhausted {} bounded attempts while a newer dirty generation remained.",
		player->getName(),
		PLAYER_FINAL_SAVE_MAX_ATTEMPTS
	);
	return false;
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
	logger.debug("Saving key-value store took {} milliseconds.", duration);
	return saveSuccess;
}
