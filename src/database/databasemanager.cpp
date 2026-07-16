/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "database/databasemanager.hpp"

#include "config/configmanager.hpp"
#include "lua/functions/core/libs/core_libs_functions.hpp"
#include "lua/scripts/luascript.hpp"

namespace InternalDBManager {
	int32_t extractVersionFromFilename(const std::string &filename) {
		std::regex versionRegex(R"((\d+)\.lua)");
		std::smatch match;

		if (std::regex_search(filename, match, versionRegex) && match.size() > 1) {
			return std::stoi(match.str(1));
		}

		return -1;
	}

	bool runMigrationChain(int32_t &currentVersion, std::vector<Migration> migrations, const MigrationRunner &runMigration, const MigrationVersionPersister &persistVersion) {
		std::sort(migrations.begin(), migrations.end());

		for (const auto &[fileVersion, scriptPath] : migrations) {
			if (fileVersion <= currentVersion) {
				continue;
			}

			if (!runMigration(fileVersion, scriptPath)) {
				return false;
			}

			if (!persistVersion(fileVersion)) {
				return false;
			}

			currentVersion = fileVersion;
		}

		return true;
	}
}

bool DatabaseManager::optimizeTables() {
	Database &db = Database::getInstance();
	std::ostringstream query;

	query << "SELECT `TABLE_NAME` FROM `information_schema`.`TABLES` WHERE `TABLE_SCHEMA` = " << db.escapeString(g_configManager().getString(MYSQL_DB)) << " AND `DATA_FREE` > 0";
	DBResult_ptr result = db.storeQuery(query.str());
	if (!result) {
		return false;
	}

	do {
		std::string tableName = result->getString("TABLE_NAME");

		query.str(std::string());
		query << "OPTIMIZE TABLE `" << tableName << '`';
		std::string tableResult;
		if (db.executeQuery(query.str())) {
			tableResult = "[Success]";
		} else {
			tableResult = "[Failed]";
		}

		g_logger().info("Optimizing table {}... {}", tableName, tableResult);
	} while (result->next());

	return true;
}

bool DatabaseManager::tableExists(const std::string &tableName) {
	Database &db = Database::getInstance();
	std::ostringstream query;
	query << "SELECT `TABLE_NAME` FROM `information_schema`.`tables` WHERE `TABLE_SCHEMA` = " << db.escapeString(g_configManager().getString(MYSQL_DB)) << " AND `TABLE_NAME` = " << db.escapeString(tableName) << " LIMIT 1";
	return db.storeQuery(query.str()).get() != nullptr;
}

bool DatabaseManager::isDatabaseSetup() {
	Database &db = Database::getInstance();
	std::ostringstream query;
	query << "SELECT `TABLE_NAME` FROM `information_schema`.`tables` WHERE `TABLE_SCHEMA` = " << db.escapeString(g_configManager().getString(MYSQL_DB));
	return db.storeQuery(query.str()).get() != nullptr;
}

int32_t DatabaseManager::getDatabaseVersion() {
	if (!tableExists("server_config")) {
		Database &db = Database::getInstance();
		if (!db.executeQuery("CREATE TABLE `server_config` (`config` VARCHAR(50) NOT NULL, `value` VARCHAR(256) NOT NULL DEFAULT '', UNIQUE(`config`)) ENGINE = InnoDB")) {
			return -1;
		}
		if (!db.executeQuery("INSERT INTO `server_config` VALUES ('db_version', 0)")) {
			return -1;
		}
		return 0;
	}

	int32_t version = 0;
	if (getDatabaseConfig("db_version", version)) {
		return version;
	}
	return -1;
}

bool DatabaseManager::updateDatabase() {
	Benchmark bm;
	lua_State* L = luaL_newstate();
	if (!L) {
		g_logger().error("DatabaseManager::updateDatabase - Unable to create Lua state. Migration chain aborted.");
		return false;
	}

	luaL_openlibs(L);
	CoreLibsFunctions::initMigration(L);

	int32_t currentVersion = getDatabaseVersion();
	if (currentVersion < 0) {
		g_logger().error("DatabaseManager::updateDatabase - Unable to read the current database version. Migration chain aborted.");
		lua_close(L);
		return false;
	}

	std::string migrationDirectory = g_configManager().getString(DATA_DIRECTORY) + "/migrations/";
	std::vector<InternalDBManager::Migration> migrations;

	for (const auto &entry : std::filesystem::directory_iterator(migrationDirectory)) {
		if (entry.is_regular_file()) {
			std::string filename = entry.path().filename().string();
			int32_t fileVersion = InternalDBManager::extractVersionFromFilename(filename);
			migrations.emplace_back(fileVersion, entry.path().string());
		}
	}

	const auto runMigration = [L](int32_t fileVersion, const std::string &scriptPath) -> bool {
		lua_settop(L, 0);
		lua_pushnil(L);
		lua_setglobal(L, "onUpdateDatabase");

		if (luaL_dofile(L, scriptPath.c_str()) != 0) {
			const char* errorMessage = lua_tostring(L, -1);
			g_logger().error("DatabaseManager::updateDatabase - Failed to load migration version {}: {}", fileVersion, errorMessage ? errorMessage : "unknown Lua error");
			lua_settop(L, 0);
			return false;
		}

		// Discard any values returned by the migration chunk itself. The migration
		// contract is defined exclusively by the onUpdateDatabase() return value.
		lua_settop(L, 0);
		lua_getglobal(L, "onUpdateDatabase");
		if (!lua_isfunction(L, -1)) {
			g_logger().error("DatabaseManager::updateDatabase - Migration version {} does not define onUpdateDatabase(). Migration chain aborted.", fileVersion);
			lua_settop(L, 0);
			return false;
		}

		if (lua_pcall(L, 0, 1, 0) != 0) {
			const char* errorMessage = lua_tostring(L, -1);
			g_logger().error("DatabaseManager::updateDatabase - Migration version {} failed at runtime: {}", fileVersion, errorMessage ? errorMessage : "unknown Lua error");
			lua_settop(L, 0);
			return false;
		}

		bool migrationAccepted = false;
		if (lua_isnil(L, -1)) {
			// Historical shipped migrations use an implicit nil return on success.
			migrationAccepted = true;
		} else if (lua_isboolean(L, -1)) {
			migrationAccepted = lua_toboolean(L, -1) != 0;
		} else {
			g_logger().error(
				"DatabaseManager::updateDatabase - Migration version {} returned unsupported result type '{}'. Expected nil for legacy success or a boolean result. Migration chain aborted.",
				fileVersion,
				lua_typename(L, lua_type(L, -1))
			);
		}

		lua_settop(L, 0);

		if (!migrationAccepted) {
			g_logger().error("DatabaseManager::updateDatabase - Migration version {} explicitly rejected or returned an invalid result. Migration chain aborted.", fileVersion);
			return false;
		}

		return true;
	};

	const auto persistVersion = [](int32_t fileVersion) -> bool {
		if (!DatabaseManager::registerDatabaseConfig("db_version", fileVersion)) {
			g_logger().error("DatabaseManager::updateDatabase - Migration version {} completed, but persisting db_version failed. Migration chain aborted.", fileVersion);
			return false;
		}

		g_logger().info("Database has been updated to version {}", fileVersion);
		return true;
	};

	const bool migrationSucceeded = InternalDBManager::runMigrationChain(currentVersion, std::move(migrations), runMigration, persistVersion);

	double duration = bm.duration();
	if (duration < 1000.0) {
		g_logger().debug("Database update {} in {:.2f} ms", migrationSucceeded ? "completed" : "aborted", duration);
	} else {
		g_logger().debug("Database update {} in {:.2f} seconds", migrationSucceeded ? "completed" : "aborted", duration / 1000.0);
	}

	lua_close(L);
	return migrationSucceeded;
}

bool DatabaseManager::getDatabaseConfig(const std::string &config, int32_t &value) {
	Database &db = Database::getInstance();
	std::ostringstream query;
	query << "SELECT `value` FROM `server_config` WHERE `config` = " << db.escapeString(config);

	DBResult_ptr result = db.storeQuery(query.str());
	if (!result) {
		return false;
	}

	value = result->getNumber<int32_t>("value");
	return true;
}

bool DatabaseManager::registerDatabaseConfig(const std::string &config, int32_t value) {
	Database &db = Database::getInstance();
	std::ostringstream query;

	int32_t tmp;
	if (!getDatabaseConfig(config, tmp)) {
		query << "INSERT INTO `server_config` VALUES (" << db.escapeString(config) << ", '" << value << "')";
	} else {
		query << "UPDATE `server_config` SET `value` = '" << value << "' WHERE `config` = " << db.escapeString(config);
	}

	return db.executeQuery(query.str());
}
