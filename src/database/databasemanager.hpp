/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include "database/database.hpp"

#include <functional>
#include <string>
#include <utility>
#include <vector>

namespace InternalDBManager {
	using Migration = std::pair<int32_t, std::string>;
	using MigrationRunner = std::function<bool(int32_t, const std::string &)>;
	using MigrationVersionPersister = std::function<bool(int32_t)>;

	int32_t extractVersionFromFilename(const std::string &filename);
	bool runMigrationChain(int32_t &currentVersion, std::vector<Migration> migrations, const MigrationRunner &runMigration, const MigrationVersionPersister &persistVersion);
}

class DatabaseManager {
public:
	static bool tableExists(const std::string &table);

	static int32_t getDatabaseVersion();
	static bool isDatabaseSetup();

	static bool optimizeTables();
	static bool updateDatabase();

	static bool getDatabaseConfig(const std::string &config, int32_t &value);
	static bool registerDatabaseConfig(const std::string &config, int32_t value);
};
