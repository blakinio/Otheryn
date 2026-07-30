/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "database/database.hpp"
#include "database/database_failure_classification.hpp"

#include "config/configmanager.hpp"
#include "creatures/players/player.hpp"
#include "game/database_outage_drain_orchestrator.hpp"
#include "game/game.hpp"
#include "game/scheduling/dispatcher.hpp"
#include "game/scheduling/save_manager.hpp"
#include "lib/di/container.hpp"
#include "lib/metrics/metrics.hpp"
#include "utils/tools.hpp"

#include <iterator>

#ifndef USE_PRECOMPILED_HEADERS
	#include <algorithm>
	#include <chrono>
	#include <fmt/format.h>
	#include <limits>
	#include <mutex>
	#include <string>
	#include <string_view>
	#include <vector>
#endif

namespace {
	constexpr uint32_t DATABASE_OUTAGE_DRAIN_TICK_DELAY_MS = SCHEDULER_MINTICKS;

	std::mutex databaseOutageDrainScheduleMutex;
	bool databaseOutageDrainTickScheduled = false;
	DatabaseOutageDrainOrchestrator databaseOutageDrainOrchestrator;

	void appendInsertBaseQuery(std::string &sql, std::string_view baseQuery, bool baseHasSpace) {
		sql += baseQuery;
		if (!baseHasSpace) {
			sql.push_back(' ');
		}
	}

	DatabaseOutageStateMachine &databaseOutageStateOwner() {
		static DatabaseOutageStateMachine owner({ std::chrono::milliseconds { 60'000 }, std::chrono::milliseconds { 60'000 } });
		return owner;
	}

	DatabaseOutageEventPublisher &databaseOutageEventPublisher() {
		static DatabaseOutageEventPublisher publisher(databaseOutageStateOwner());
		return publisher;
	}

	DatabaseOutageTimePoint databaseOutageNow() noexcept {
		return std::chrono::duration_cast<DatabaseOutageTimePoint>(std::chrono::steady_clock::now().time_since_epoch());
	}

	void enterDatabaseOutageGameMaintenance(std::string_view reason) {
		const std::string reasonCopy(reason);
		g_dispatcher().safeCall([reasonCopy] {
			if (g_game().getGameState() != GAME_STATE_SHUTDOWN && g_game().getGameState() != GAME_STATE_MAINTAIN) {
				g_game().setGameState(GAME_STATE_MAINTAIN);
			}
			g_logger().warn("Database outage runtime entered game maintenance: {}", reasonCopy);
		});
	}

	uint32_t databaseOutageDelayUntil(DatabaseOutageTimePoint deadline, DatabaseOutageTimePoint now) noexcept {
		if (deadline <= now) {
			return DATABASE_OUTAGE_DRAIN_TICK_DELAY_MS;
		}
		const auto remaining = static_cast<uint64_t>((deadline - now).count());
		return static_cast<uint32_t>(std::clamp<uint64_t>(
			remaining,
			DATABASE_OUTAGE_DRAIN_TICK_DELAY_MS,
			std::numeric_limits<uint32_t>::max()
		));
	}

	std::vector<uint32_t> captureDatabaseOutageDrainPlayerIds() {
		std::vector<uint32_t> playerIds;
		const auto &players = g_game().getPlayers();
		playerIds.reserve(players.size());
		for (const auto &[playerId, player] : players) {
			if (player && !player->isRemoved()) {
				playerIds.emplace_back(playerId);
			}
		}
		std::ranges::sort(playerIds);
		playerIds.erase(std::unique(playerIds.begin(), playerIds.end()), playerIds.end());
		return playerIds;
	}

	void observeDatabaseOutageDrainFailure(std::string_view reason) {
		g_metrics().addCounter("database_outage_drain_failures", 1, { { "reason", std::string(reason) } });
	}

	DatabaseOutageDrainPlayerAttemptResult attemptDatabaseOutageDrainPlayer(uint32_t playerId) {
		g_metrics().addCounter("database_outage_drain_player_attempts", 1);
		const auto &player = g_game().getPlayerByID(playerId);
		if (!player || player->isRemoved()) {
			observeDatabaseOutageDrainFailure("player_missing");
			g_logger().error("Database outage drain player {} is no longer available.", playerId);
			return {};
		}

		const auto removal = g_saveManager().removePlayerForDatabaseOutageDrain(player);
		DatabaseOutageDrainPlayerAttemptResult result {
			.playerFound = true,
			.removed = removal.removed,
			.finalSaveObserved = removal.finalSaveObserved,
			.finalSaveSucceeded = removal.finalSaveSucceeded,
		};
		if (!result.removed) {
			observeDatabaseOutageDrainFailure("removal_failed");
		}
		if (!result.finalSaveObserved) {
			observeDatabaseOutageDrainFailure("final_save_not_observed");
		} else if (!result.finalSaveSucceeded) {
			observeDatabaseOutageDrainFailure("final_save_failed");
		}
		return result;
	}

	void logDatabaseOutageDrainSummary(std::string_view disposition) {
		const auto summary = databaseOutageDrainOrchestrator.summary();
		g_logger().warn(
			"Database outage drain {}: transition={}, captured={}, attempts={}/{}, missing={}, removal_failures={}, final_save_not_observed={}, final_save_failures={}, deadline_expired={}, fail_closed={}",
			disposition,
			summary.transitionCount,
			summary.capturedPlayers,
			summary.attempts,
			summary.attemptLimit,
			summary.missingPlayers,
			summary.removalFailures,
			summary.finalSaveNotObserved,
			summary.finalSaveFailures,
			summary.deadlineExpired,
			summary.failClosed
		);
	}

	void runDatabaseOutageDrainTick();

	void scheduleDatabaseOutageDrainTick(uint32_t delay = DATABASE_OUTAGE_DRAIN_TICK_DELAY_MS) {
		{
			std::lock_guard lock(databaseOutageDrainScheduleMutex);
			if (databaseOutageDrainTickScheduled) {
				return;
			}
			databaseOutageDrainTickScheduled = true;
		}

		const auto eventId = g_dispatcher().scheduleEvent(
			std::max(delay, DATABASE_OUTAGE_DRAIN_TICK_DELAY_MS),
			[] {
				{
					std::lock_guard lock(databaseOutageDrainScheduleMutex);
					databaseOutageDrainTickScheduled = false;
				}
				runDatabaseOutageDrainTick();
			},
			"DatabaseOutageDrain",
			DispatcherLane::Maintenance
		);
		if (eventId != 0) {
			return;
		}

		{
			std::lock_guard lock(databaseOutageDrainScheduleMutex);
			databaseOutageDrainTickScheduled = false;
		}
		observeDatabaseOutageDrainFailure("schedule_rejected");
		g_logger().error("Database outage drain scheduling was rejected; failing closed to game maintenance.");
		enterDatabaseOutageGameMaintenance("drain scheduler rejected");
	}

	void handleDatabaseOutageDrainDecision(
		const DatabaseOutageDrainDecision &decision,
		DatabaseOutageTimePoint now
	) {
		switch (decision.action) {
			case DatabaseOutageDrainAction::AttemptPlayer: {
				if (!decision.playerId.has_value()) {
					observeDatabaseOutageDrainFailure("missing_attempt_id");
					enterDatabaseOutageGameMaintenance("drain decision omitted player ID");
					return;
				}
				const auto result = attemptDatabaseOutageDrainPlayer(*decision.playerId);
				if (!databaseOutageDrainOrchestrator.recordAttempt(*decision.playerId, result)) {
					observeDatabaseOutageDrainFailure("attempt_result_rejected");
					enterDatabaseOutageGameMaintenance("drain attempt result rejected");
					return;
				}
				scheduleDatabaseOutageDrainTick();
				return;
			}
			case DatabaseOutageDrainAction::CompleteDrain: {
				const auto event = databaseOutageEventPublisher().drainCompleted(now);
				if (event.disposition != DatabaseOutageEventDisposition::Applied || event.after.state != DatabaseOutageState::Maintenance) {
					observeDatabaseOutageDrainFailure("completion_event_rejected");
					enterDatabaseOutageGameMaintenance("drain completion event rejected");
					return;
				}
				enterDatabaseOutageGameMaintenance("drain completed");
				logDatabaseOutageDrainSummary("completed");
				return;
			}
			case DatabaseOutageDrainAction::ExpireDrain: {
				const auto event = databaseOutageEventPublisher().drainDeadlineExpired(now);
				if (event.disposition != DatabaseOutageEventDisposition::Applied || event.after.state != DatabaseOutageState::Maintenance) {
					observeDatabaseOutageDrainFailure("deadline_event_rejected");
					enterDatabaseOutageGameMaintenance("drain deadline event rejected");
					return;
				}
				enterDatabaseOutageGameMaintenance("drain deadline expired");
				logDatabaseOutageDrainSummary("deadline expired; finite cleanup continues");
				scheduleDatabaseOutageDrainTick();
				return;
			}
			case DatabaseOutageDrainAction::CleanupComplete:
				enterDatabaseOutageGameMaintenance("post-deadline cleanup completed");
				logDatabaseOutageDrainSummary("cleanup completed");
				return;
			case DatabaseOutageDrainAction::FailClosedMaintenance:
				observeDatabaseOutageDrainFailure("orchestrator_fail_closed");
				enterDatabaseOutageGameMaintenance("orchestrator failed closed");
				logDatabaseOutageDrainSummary("failed closed");
				return;
			case DatabaseOutageDrainAction::None:
				observeDatabaseOutageDrainFailure("unexpected_empty_decision");
				enterDatabaseOutageGameMaintenance("orchestrator returned no bounded action");
				return;
		}

		observeDatabaseOutageDrainFailure("unknown_decision");
		enterDatabaseOutageGameMaintenance("unknown drain decision");
	}

	void runDatabaseOutageDrainTick() {
		const auto now = databaseOutageNow();
		const auto snapshot = databaseOutageEventPublisher().snapshot();
		switch (snapshot.state) {
			case DatabaseOutageState::Healthy:
				databaseOutageDrainOrchestrator.reset();
				return;
			case DatabaseOutageState::Degraded: {
				if (!snapshot.degradedDeadline.has_value()) {
					observeDatabaseOutageDrainFailure("missing_degraded_deadline");
					enterDatabaseOutageGameMaintenance("degraded snapshot omitted deadline");
					return;
				}
				if (now < *snapshot.degradedDeadline) {
					scheduleDatabaseOutageDrainTick(databaseOutageDelayUntil(*snapshot.degradedDeadline, now));
					return;
				}
				const auto event = databaseOutageEventPublisher().degradedDeadlineExpired(now);
				if (event.disposition != DatabaseOutageEventDisposition::Applied || event.after.state != DatabaseOutageState::Draining) {
					observeDatabaseOutageDrainFailure("degraded_deadline_event_rejected");
					enterDatabaseOutageGameMaintenance("degraded deadline event rejected");
					return;
				}
				scheduleDatabaseOutageDrainTick();
				return;
			}
			case DatabaseOutageState::Draining: {
				if (!databaseOutageDrainOrchestrator.matches(snapshot)) {
					const auto playerIds = captureDatabaseOutageDrainPlayerIds();
					if (!databaseOutageDrainOrchestrator.begin(snapshot, playerIds)) {
						observeDatabaseOutageDrainFailure("generation_rejected");
						enterDatabaseOutageGameMaintenance("drain generation rejected outage snapshot");
						return;
					}
					g_logger().warn(
						"Database outage drain captured {} players for transition {} with a finite deadline.",
						playerIds.size(),
						snapshot.transitionCount
					);
				}
				handleDatabaseOutageDrainDecision(databaseOutageDrainOrchestrator.next(snapshot, now), now);
				return;
			}
			case DatabaseOutageState::Maintenance: {
				enterDatabaseOutageGameMaintenance("outage state is maintenance");
				if (!databaseOutageDrainOrchestrator.hasPendingCleanup()) {
					return;
				}
				handleDatabaseOutageDrainDecision(databaseOutageDrainOrchestrator.next(snapshot, now), now);
				return;
			}
		}

		observeDatabaseOutageDrainFailure("unknown_outage_state");
		enterDatabaseOutageGameMaintenance("unknown outage state");
	}

	DatabaseNativeErrorKind classifyDatabaseNativeError(unsigned int error) noexcept {
		if (error == 0) {
			return DatabaseNativeErrorKind::None;
		}
		if (error == CR_SERVER_LOST || error == CR_CONN_HOST_ERROR || error == CR_CONNECTION_ERROR) {
			return DatabaseNativeErrorKind::ConnectionLost;
		}
		if (error == CR_SERVER_GONE_ERROR || error == 1053 /* ER_SERVER_SHUTDOWN */) {
			return DatabaseNativeErrorKind::ServerGone;
		}
		return DatabaseNativeErrorKind::Other;
	}

	void publishDatabaseRuntimeResult(DatabaseRuntimeOperation operation, bool succeeded, unsigned int error) {
		const auto classification = classifyDatabaseRuntimeResult(operation, succeeded, classifyDatabaseNativeError(error));
		if (classification.succeeded()) {
			return;
		}
		(void)databaseOutageEventPublisher().publish(classification, databaseOutageNow());
		scheduleDatabaseOutageDrainTick();
	}

	bool executeRuntimeQueryOnce(MYSQL* handle, std::string_view query, DatabaseRuntimeOperation operation) {
		if (!handle) {
			g_logger().error("Database not initialized!");
			publishDatabaseRuntimeResult(operation, false, 0);
			return false;
		}
		if (mysql_query(handle, query.data()) != 0) {
			const auto error = mysql_errno(handle);
			g_logger().error("Query: {}", query.substr(0, 256));
			g_logger().error("MySQL error [{}]: {}", error, mysql_error(handle));
			publishDatabaseRuntimeResult(operation, false, error);
			return false;
		}
		return true;
	}

}

DatabaseOutageSnapshot getDatabaseOutageSnapshot() {
	return databaseOutageEventPublisher().snapshot();
}

DatabaseOutageEventResult publishDatabaseOutageDegradedDeadlineExpired(DatabaseOutageTimePoint now) {
	return databaseOutageEventPublisher().degradedDeadlineExpired(now);
}

DatabaseOutageEventResult publishDatabaseOutageDrainCompleted(DatabaseOutageTimePoint now) {
	return databaseOutageEventPublisher().drainCompleted(now);
}

DatabaseOutageEventResult publishDatabaseOutageDrainDeadlineExpired(DatabaseOutageTimePoint now) {
	return databaseOutageEventPublisher().drainDeadlineExpired(now);
}

Database::~Database() {
	if (handle != nullptr) {
		mysql_close(handle);
	}
}

Database &Database::getInstance() {
	return inject<Database>();
}

bool Database::connect() {
	return connect(&g_configManager().getString(MYSQL_HOST), &g_configManager().getString(MYSQL_USER), &g_configManager().getString(MYSQL_PASS), &g_configManager().getString(MYSQL_DB), g_configManager().getNumber(SQL_PORT), &g_configManager().getString(MYSQL_SOCK));
}

bool Database::connect(const std::string* host, const std::string* user, const std::string* password, const std::string* database, uint32_t port, const std::string* sock) {
	// connection handle initialization
	handle = mysql_init(nullptr);
	if (!handle) {
		g_logger().error("Failed to initialize MySQL connection handle.");
		return false;
	}

	if (host->empty() || user->empty() || password->empty() || database->empty() || port <= 0) {
		g_logger().warn("MySQL host, user, password, database or port not provided");
	}

	// Oteryn persistence is fail-closed: an implicit reconnect resets server-side
	// session state and rolls back active transactions without notifying callers.
	bool reconnect = false;
	mysql_options(handle, MYSQL_OPT_RECONNECT, &reconnect);

	// Remove ssl verification
	bool ssl_enabled = false;
	mysql_options(handle, MYSQL_OPT_SSL_VERIFY_SERVER_CERT, &ssl_enabled);

	// connects to database
	if (!mysql_real_connect(handle, host->c_str(), user->c_str(), password->c_str(), database->c_str(), port, sock->c_str(), 0)) {
		g_logger().error("MySQL Error Message: {}", mysql_error(handle));
		return false;
	}

	DBResult_ptr result = storeQuery("SHOW VARIABLES LIKE 'max_allowed_packet'");
	if (result) {
		maxPacketSize = result->getNumber<uint64_t>("Value");
	}
	return true;
}

void Database::createDatabaseBackup(bool compress) const {
	if (!g_configManager().getBoolean(MYSQL_DB_BACKUP)) {
		return;
	}

	// Get current time for formatting
	auto now = std::chrono::system_clock::now();
	std::string formattedDate = fmt::format("{:%Y-%m-%d}", now);
	std::string formattedTime = fmt::format("{:%H-%M-%S}", now);

	// Create a backup directory based on the current date
	std::string backupDir = fmt::format("database_backup/{}/", formattedDate);
	std::filesystem::create_directories(backupDir);
	std::string backupFileName = fmt::format("{}backup_{}.sql", backupDir, formattedTime);

	// Create a temporary configuration file for MySQL credentials
	std::string tempConfigFile = "database_backup.cnf";
	std::ofstream configFile(tempConfigFile);
	if (configFile.is_open()) {
		configFile << "[client]\n";
		configFile << "user=\"" << g_configManager().getString(MYSQL_USER) << "\"\n";
		configFile << "password=\"" << g_configManager().getString(MYSQL_PASS) << "\"\n";
		configFile << "host=" << g_configManager().getString(MYSQL_HOST) << "\n";
		configFile << "port=" << g_configManager().getNumber(SQL_PORT) << "\n";
		configFile.close();
	} else {
		g_logger().error("Failed to create temporary MySQL configuration file.");
		return;
	}

	// Execute mysqldump command to create backup
	std::string command = fmt::format(
		"mysqldump --defaults-extra-file={} {} > {}",
		tempConfigFile, g_configManager().getString(MYSQL_DB), backupFileName
	);

	int result = std::system(command.c_str());
	std::filesystem::remove(tempConfigFile);

	if (result != 0) {
		g_logger().error("Failed to create database backup using mysqldump.");
		return;
	}

	// Compress the backup file if requested
	std::string compressedFileName;
	compressedFileName = backupFileName + ".gz";
	gzFile gzFile = gzopen(compressedFileName.c_str(), "wb9");
	if (!gzFile) {
		g_logger().error("Failed to open gzip file for compression.");
		return;
	}

	std::ifstream backupFile(backupFileName, std::ios::binary);
	if (!backupFile.is_open()) {
		g_logger().error("Failed to open backup file for compression: {}", backupFileName);
		gzclose(gzFile);
		return;
	}

	std::string buffer(8192, '\0');
	while (backupFile.read(&buffer[0], buffer.size()) || backupFile.gcount() > 0) {
		gzwrite(gzFile, buffer.data(), backupFile.gcount());
	}

	backupFile.close();
	gzclose(gzFile);
	std::filesystem::remove(backupFileName);

	g_logger().info("Database backup successfully compressed to: {}", compressedFileName);

	// Delete backups older than 7 days
	auto nowTime = std::chrono::system_clock::now();
	auto sevenDaysAgo = nowTime - std::chrono::hours(7 * 24); // 7 days in hours
	for (const auto &entry : std::filesystem::directory_iterator("database_backup")) {
		if (entry.is_directory()) {
			try {
				for (const auto &file : std::filesystem::directory_iterator(entry)) {
					if (file.path().extension() == ".gz") {
						auto fileTime = std::filesystem::last_write_time(file);
						auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(fileTime - std::filesystem::file_time_type::clock::now() + std::chrono::system_clock::now());
						auto fileTimeSystemClock = std::chrono::system_clock::time_point { sctp.time_since_epoch() };

						if (fileTimeSystemClock < sevenDaysAgo) {
							std::filesystem::remove(file);
							g_logger().info("Deleted old backup file: {}", file.path().string());
						}
					}
				}
			} catch (const std::filesystem::filesystem_error &e) {
				g_logger().error("Failed to check or delete files in backup directory: {}. Error: {}", entry.path().string(), e.what());
			}
		}
	}
}

bool Database::beginTransaction() {
	// Hold the connection lock before BEGIN so no other thread can execute a
	// statement on the shared MYSQL handle between BEGIN and transaction ownership.
	metrics::lock_latency measureLock("database");
	databaseLock.lock();
	measureLock.stop();

	g_logger().trace("Executing Query: BEGIN");
	metrics::query_latency measure("BEGIN");
	const bool success = executeRuntimeQueryOnce(handle, "BEGIN", DatabaseRuntimeOperation::TransactionBegin);
	if (!success) {
		databaseLock.unlock();
		return false;
	}
	mysql_free_result(mysql_store_result(handle));

	return true;
}

bool Database::rollback() {
	if (!handle) {
		g_logger().error("Database not initialized!");
		publishDatabaseRuntimeResult(DatabaseRuntimeOperation::TransactionRollback, false, 0);
		return false;
	}

	if (mysql_rollback(handle) != 0) {
		const auto error = mysql_errno(handle);
		g_logger().error("Message: {}", mysql_error(handle));
		publishDatabaseRuntimeResult(DatabaseRuntimeOperation::TransactionRollback, false, error);
		databaseLock.unlock();
		return false;
	}

	databaseLock.unlock();
	return true;
}

bool Database::commit() {
	if (!handle) {
		g_logger().error("Database not initialized!");
		publishDatabaseRuntimeResult(DatabaseRuntimeOperation::TransactionCommit, false, 0);
		return false;
	}
	if (mysql_commit(handle) != 0) {
		const auto error = mysql_errno(handle);
		g_logger().error("Message: {}", mysql_error(handle));
		publishDatabaseRuntimeResult(DatabaseRuntimeOperation::TransactionCommit, false, error);
		databaseLock.unlock();
		return false;
	}

	databaseLock.unlock();
	return true;
}

bool Database::isRecoverableError(unsigned int error) {
	return error == CR_SERVER_LOST || error == CR_SERVER_GONE_ERROR || error == CR_CONN_HOST_ERROR || error == 1053 /*ER_SERVER_SHUTDOWN*/ || error == CR_CONNECTION_ERROR;
}

bool Database::retryQuery(std::string_view query, int retries) {
	// Compatibility wrapper for existing callers. Arbitrary SQL statements are
	// intentionally not resent after connection loss because their server-side
	// execution state may be unknown and an implicit reconnect destroys transaction state.
	(void)retries;
	if (mysql_query(handle, query.data()) != 0) {
		const auto error = mysql_errno(handle);
		g_logger().error("Query: {}", query.substr(0, 256));
		g_logger().error("MySQL error [{}]: {}", error, mysql_error(handle));
		publishDatabaseRuntimeResult(DatabaseRuntimeOperation::Query, false, error);
		return false;
	}
	return true;
}

bool Database::executeQuery(std::string_view query) {
	if (!handle) {
		g_logger().error("Database not initialized!");
		publishDatabaseRuntimeResult(DatabaseRuntimeOperation::Query, false, 0);
		return false;
	}

	g_logger().trace("Executing Query: {}", query);

	metrics::lock_latency measureLock("database");
	std::scoped_lock lock { databaseLock };
	measureLock.stop();

	metrics::query_latency measure(query.substr(0, 50));
	bool success = retryQuery(query, 10);
	mysql_free_result(mysql_store_result(handle));

	return success;
}

DBResult_ptr Database::storeQuery(std::string_view query) {
	if (!handle) {
		g_logger().error("Database not initialized!");
		publishDatabaseRuntimeResult(DatabaseRuntimeOperation::StoreQuery, false, 0);
		return nullptr;
	}
	g_logger().trace("Storing Query: {}", query);

	metrics::lock_latency measureLock("database");
	std::scoped_lock lock { databaseLock };
	measureLock.stop();

	metrics::query_latency measure(query.substr(0, 50));
	if (mysql_query(handle, query.data()) != 0) {
		const auto error = mysql_errno(handle);
		g_logger().error("Query: {}", query);
		g_logger().error("MySQL error [{}]: {}", error, mysql_error(handle));
		publishDatabaseRuntimeResult(DatabaseRuntimeOperation::StoreQuery, false, error);
		return nullptr;
	}

	// Retrieving results of query
	MYSQL_RES* res = mysql_store_result(handle);
	if (res != nullptr) {
		DBResult_ptr result = std::make_shared<DBResult>(res);
		if (!result->hasNext()) {
			return nullptr;
		}
		return result;
	}

	if (mysql_field_count(handle) != 0 && mysql_errno(handle) != 0) {
		const auto error = mysql_errno(handle);
		g_logger().error("MySQL error [{}]: {}", error, mysql_error(handle));
		publishDatabaseRuntimeResult(DatabaseRuntimeOperation::StoreQuery, false, error);
	}
	return nullptr;
}

std::string Database::escapeString(const std::string &s) const {
	std::string::size_type len = s.length();
	auto length = static_cast<uint32_t>(len);
	std::string escaped = escapeBlob(s.c_str(), length);
	if (escaped.empty()) {
		g_logger().warn("Error escaping string");
	}
	return escaped;
}

std::string Database::escapeBlob(const char* s, uint32_t length) const {
	metrics::lock_latency measureLock("database");
	std::scoped_lock lock { databaseLock };
	measureLock.stop();

	size_t maxLength = (length * 2) + 1;

	std::string escaped;
	escaped.reserve(maxLength + 2);
	escaped.push_back('\'');

	if (length != 0) {
		std::string output(maxLength, '\0');
		size_t escapedLength = mysql_real_escape_string(handle, &output[0], s, length);
		output.resize(escapedLength);
		escaped.append(output);
	}

	escaped.push_back('\'');
	return escaped;
}

DBResult::DBResult(MYSQL_RES* res) {
	handle = res;

	int num_fields = mysql_num_fields(handle);

	const MYSQL_FIELD* fields = mysql_fetch_fields(handle);
	for (size_t i = 0; i < num_fields; i++) {
		listNames[fields[i].name] = i;
	}
	row = mysql_fetch_row(handle);
}

DBResult::~DBResult() {
	mysql_free_result(handle);
}

std::string DBResult::getString(const std::string &s) const {
	auto it = listNames.find(s);
	if (it == listNames.end()) {
		g_logger().error("Column '{}' does not exist in result set", s);
		return {};
	}
	if (row[it->second] == nullptr) {
		return {};
	}
	return std::string(row[it->second]);
}

const char* DBResult::getStream(const std::string &s, unsigned long &size) const {
	auto it = listNames.find(s);
	if (it == listNames.end()) {
		g_logger().error("Column '{}' doesn't exist in the result set", s);
		size = 0;
		return nullptr;
	}
	if (row[it->second] == nullptr) {
		size = 0;
		return nullptr;
	}

	size = mysql_fetch_lengths(handle)[it->second];
	return row[it->second];
}

uint8_t DBResult::getU8FromString(const std::string &string, const std::string &function) {
	auto result = static_cast<uint8_t>(std::atoi(string.c_str()));
	if (result > std::numeric_limits<uint8_t>::max()) {
		g_logger().error("[{}] Failed to get number value {} for tier table result, on function call: {}", __FUNCTION__, result, function);
		return 0;
	}

	return result;
}

int8_t DBResult::getInt8FromString(const std::string &string, const std::string &function) {
	auto result = static_cast<int8_t>(std::atoi(string.c_str()));
	if (result > std::numeric_limits<int8_t>::max()) {
		g_logger().error("[{}] Failed to get number value {} for tier table result, on function call: {}", __FUNCTION__, result, function);
		return 0;
	}

	return result;
}

size_t DBResult::countResults() const {
	return static_cast<size_t>(mysql_num_rows(handle));
}

bool DBResult::hasNext() const {
	return row != nullptr;
}

bool DBResult::next() {
	if (!handle) {
		g_logger().error("Database not initialized!");
		return false;
	}
	row = mysql_fetch_row(handle);
	return row != nullptr;
}

DBInsert::DBInsert(std::string insertQuery) :
	query(std::move(insertQuery)) {
	this->length = this->query.length();
}

bool DBInsert::addRow(std::string_view row) {
	const size_t rowLength = row.length();
	auto max_packet_size = Database::getInstance().getMaxPacketSize();
	size_t addedLength = values.empty() ? rowLength + 2 : rowLength + 3;

	if (length + addedLength > max_packet_size) {
		if (values.empty() || !execute()) {
			return false;
		}

		addedLength = rowLength + 2;
		if (length + addedLength > max_packet_size) {
			return false;
		}
	}

	length += addedLength;
	if (values.empty()) {
		values.reserve(rowLength + 2);
		values.push_back('(');
		values.append(row);
		values.push_back(')');
	} else {
		values.reserve(values.length() + rowLength + 3);
		values.push_back(',');
		values.push_back('(');
		values.append(row);
		values.push_back(')');
	}
	return true;
}

bool DBInsert::addRow(std::ostringstream &row) {
	bool ret = addRow(row.str());
	row.str(std::string());
	return ret;
}

void DBInsert::upsert(const std::vector<std::string> &columns) {
	upsertColumns = columns;
}

bool DBInsert::execute() {
	if (values.empty()) {
		return true;
	}

	const std::string &baseQuery = this->query;
	std::string upsertQuery;

	if (!upsertColumns.empty()) {
		size_t estimatedSize = 32;
		for (const auto &column : upsertColumns) {
			estimatedSize += (column.size() * 2) + 16;
		}

		upsertQuery.reserve(estimatedSize);
		upsertQuery += " ON DUPLICATE KEY UPDATE ";
		auto upsertOutput = std::back_inserter(upsertQuery);
		for (size_t i = 0; i < upsertColumns.size(); ++i) {
			upsertOutput = fmt::format_to(upsertOutput, "`{0}` = VALUES(`{0}`)", upsertColumns[i]);
			if (i + 1 < upsertColumns.size()) {
				upsertQuery.push_back(',');
				upsertQuery.push_back(' ');
			}
		}
	}

	std::string currentBatch = values;
	const bool baseHasSpace = !baseQuery.empty() && baseQuery.back() == ' ';
	const size_t separatorSize = baseHasSpace ? 0U : 1U;
	const size_t queryPrefixSize = baseQuery.size() + separatorSize + upsertQuery.size();
	if (queryPrefixSize >= Database::MAX_QUERY_SIZE) {
		return false;
	}

	while (!currentBatch.empty()) {
		size_t cutPos = Database::MAX_QUERY_SIZE - queryPrefixSize;
		if (cutPos < currentBatch.size()) {
			cutPos = currentBatch.rfind("),(", cutPos);
			if (cutPos == std::string::npos) {
				return false;
			}
			cutPos += 2;
		} else {
			cutPos = currentBatch.size();
		}

		std::string batchValues = currentBatch.substr(0, cutPos);
		if (!batchValues.empty() && batchValues.back() == ',') {
			batchValues.pop_back();
		}
		currentBatch = currentBatch.substr(cutPos);

		std::string sql;
		sql.reserve(queryPrefixSize + batchValues.size());
		appendInsertBaseQuery(sql, baseQuery, baseHasSpace);
		sql += batchValues;
		sql += upsertQuery;

		if (!g_database().executeQuery(sql)) {
			return false;
		}
	}

	values.clear();
	length = this->query.length();
	return true;
}
