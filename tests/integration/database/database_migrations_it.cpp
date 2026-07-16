#include "config/configmanager.hpp"
#include "database/database.hpp"
#include "database/databasemanager.hpp"
#include "lib/logging/in_memory_logger.hpp"

#include <fmt/format.h>

#include <filesystem>
#include <fstream>
#include <sstream>
#include <string_view>

namespace it_database_migrations {

	class DatabaseMigrationChainTest : public ::testing::Test {
	protected:
		static constexpr int32_t baseVersion = 900000;
		static constexpr int32_t firstVersion = baseVersion + 1;
		static constexpr int32_t secondVersion = baseVersion + 2;
		static constexpr std::string_view markerTable = "oam_004b_should_not_run";

		void SetUp() override {
			migrationDirectory = std::filesystem::path(g_configManager().getString(DATA_DIRECTORY)) / "migrations";
			ASSERT_TRUE(std::filesystem::is_directory(migrationDirectory));
			ASSERT_TRUE(DatabaseManager::getDatabaseConfig("db_version", originalVersion));
			originalVersionCaptured = true;
			cleanupMigrationFiles();
			ASSERT_TRUE(DatabaseManager::registerDatabaseConfig("db_version", baseVersion));
			ASSERT_TRUE(g_database().executeQuery(fmt::format("DROP TABLE IF EXISTS `{}`", markerTable)));
			migrationLogger().reset();
		}

		void TearDown() override {
			cleanupMigrationFiles();
			EXPECT_TRUE(g_database().executeQuery(fmt::format("DROP TABLE IF EXISTS `{}`", markerTable)));
			if (originalVersionCaptured) {
				EXPECT_TRUE(DatabaseManager::registerDatabaseConfig("db_version", originalVersion));
			}
		}

		void writeMigration(int32_t version, std::string_view body) const {
			const auto path = migrationPath(version);
			std::ofstream file(path, std::ios::out | std::ios::trunc);
			ASSERT_TRUE(file.is_open()) << "Failed to create temporary migration: " << path;
			file << body;
			file.close();
			ASSERT_TRUE(file.good()) << "Failed to write temporary migration: " << path;
		}

		int32_t readVersion() const {
			int32_t version = -1;
			EXPECT_TRUE(DatabaseManager::getDatabaseConfig("db_version", version));
			return version;
		}

		bool updateDatabaseWithDiagnostics() {
			auto &logger = migrationLogger();
			logger.reset();
			const bool success = DatabaseManager::updateDatabase();
			if (!success) {
				std::ostringstream diagnostics;
				diagnostics << "DatabaseManager::updateDatabase() failed. Captured logs:";
				for (size_t index = 0; index < logger.logCount(); ++index) {
					const auto [level, message] = logger.getLogEntry(index);
					diagnostics << "\n[" << level << "] " << message;
				}
				ADD_FAILURE() << diagnostics.str();
			}
			return success;
		}

	private:
		InMemoryLogger &migrationLogger() const {
			return dynamic_cast<InMemoryLogger &>(g_logger());
		}

		std::filesystem::path migrationPath(int32_t version) const {
			return migrationDirectory / fmt::format("{}.lua", version);
		}

		void cleanupMigrationFiles() const {
			std::error_code ec;
			std::filesystem::remove(migrationPath(firstVersion), ec);
			ec.clear();
			std::filesystem::remove(migrationPath(secondVersion), ec);
		}

		std::filesystem::path migrationDirectory;
		int32_t originalVersion = -1;
		bool originalVersionCaptured = false;
	};

	TEST_F(DatabaseMigrationChainTest, LegacyNilResultAdvancesVersion) {
		writeMigration(firstVersion, R"lua(
function onUpdateDatabase()
end
)lua");

		EXPECT_TRUE(updateDatabaseWithDiagnostics());
		EXPECT_EQ(firstVersion, readVersion());
	}

	TEST_F(DatabaseMigrationChainTest, MigrationStateDoesNotExposeAsyncDatabaseApis) {
		writeMigration(firstVersion, R"lua(
function onUpdateDatabase()
	return db.asyncQuery == nil and db.asyncStoreQuery == nil
end
)lua");

		EXPECT_TRUE(updateDatabaseWithDiagnostics());
		EXPECT_EQ(firstVersion, readVersion());
	}

	TEST_F(DatabaseMigrationChainTest, ExplicitFalseStopsChainWithoutAdvancingVersion) {
		writeMigration(firstVersion, R"lua(
function onUpdateDatabase()
	return false
end
)lua");
		writeMigration(secondVersion, R"lua(
function onUpdateDatabase()
	db.query([[CREATE TABLE `oam_004b_should_not_run` (`id` INT NOT NULL) ENGINE=InnoDB]])
	return true
end
)lua");

		EXPECT_FALSE(DatabaseManager::updateDatabase());
		EXPECT_EQ(baseVersion, readVersion());
		EXPECT_FALSE(DatabaseManager::tableExists(std::string(markerTable)));
	}

	TEST_F(DatabaseMigrationChainTest, LuaRuntimeFailureStopsWithoutAdvancingVersion) {
		writeMigration(firstVersion, R"lua(
function onUpdateDatabase()
	error("oam-004b forced runtime failure")
end
)lua");

		EXPECT_FALSE(DatabaseManager::updateDatabase());
		EXPECT_EQ(baseVersion, readVersion());
	}

} // namespace it_database_migrations
