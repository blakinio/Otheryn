#include "database/databasemanager.hpp"

TEST(DatabaseMigrationChainTest, AppliesPendingMigrationsInAscendingOrder) {
	int32_t currentVersion = 1;
	std::vector<InternalDBManager::Migration> migrations {
		{ 3, "3.lua" },
		{ 1, "1.lua" },
		{ 2, "2.lua" },
	};
	std::vector<int32_t> executedVersions;
	std::vector<int32_t> persistedVersions;

	const bool result = InternalDBManager::runMigrationChain(
		currentVersion,
		migrations,
		[&executedVersions](int32_t version, const std::string &) {
			executedVersions.push_back(version);
			return true;
		},
		[&persistedVersions](int32_t version) {
			persistedVersions.push_back(version);
			return true;
		}
	);

	const std::vector<int32_t> expectedVersions { 2, 3 };
	EXPECT_TRUE(result);
	EXPECT_EQ(executedVersions, expectedVersions);
	EXPECT_EQ(persistedVersions, expectedVersions);
	EXPECT_EQ(currentVersion, 3);
}

TEST(DatabaseMigrationChainTest, StopsAtFirstMigrationFailure) {
	int32_t currentVersion = 0;
	std::vector<InternalDBManager::Migration> migrations {
		{ 1, "1.lua" },
		{ 2, "2.lua" },
		{ 3, "3.lua" },
	};
	std::vector<int32_t> executedVersions;
	std::vector<int32_t> persistedVersions;

	const bool result = InternalDBManager::runMigrationChain(
		currentVersion,
		migrations,
		[&executedVersions](int32_t version, const std::string &) {
			executedVersions.push_back(version);
			return version != 2;
		},
		[&persistedVersions](int32_t version) {
			persistedVersions.push_back(version);
			return true;
		}
	);

	const std::vector<int32_t> expectedExecuted { 1, 2 };
	const std::vector<int32_t> expectedPersisted { 1 };
	EXPECT_FALSE(result);
	EXPECT_EQ(executedVersions, expectedExecuted);
	EXPECT_EQ(persistedVersions, expectedPersisted);
	EXPECT_EQ(currentVersion, 1);
}

TEST(DatabaseMigrationChainTest, StopsWhenVersionPersistenceFails) {
	int32_t currentVersion = 0;
	std::vector<InternalDBManager::Migration> migrations {
		{ 1, "1.lua" },
		{ 2, "2.lua" },
		{ 3, "3.lua" },
	};
	std::vector<int32_t> executedVersions;
	std::vector<int32_t> persistedVersions;

	const bool result = InternalDBManager::runMigrationChain(
		currentVersion,
		migrations,
		[&executedVersions](int32_t version, const std::string &) {
			executedVersions.push_back(version);
			return true;
		},
		[&persistedVersions](int32_t version) {
			persistedVersions.push_back(version);
			return version != 2;
		}
	);

	const std::vector<int32_t> expectedVersions { 1, 2 };
	EXPECT_FALSE(result);
	EXPECT_EQ(executedVersions, expectedVersions);
	EXPECT_EQ(persistedVersions, expectedVersions);
	EXPECT_EQ(currentVersion, 1);
}
