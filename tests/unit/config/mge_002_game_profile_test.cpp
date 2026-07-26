#include "config/configmanager.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <array>
	#include <chrono>
	#include <filesystem>
	#include <fstream>
	#include <functional>
	#include <string>
	#include <string_view>
	#include <system_error>
	#include <thread>
#endif

#include <gtest/gtest.h>

namespace {
	class TemporaryProfileConfig final {
	public:
		TemporaryProfileConfig() {
			const auto timestamp = std::chrono::steady_clock::now().time_since_epoch().count();
			const auto threadId = std::hash<std::thread::id> {}(std::this_thread::get_id());
			path = std::filesystem::temp_directory_path() / ("mge_002_game_profile_" + std::to_string(timestamp) + "_" + std::to_string(threadId) + ".lua");
		}

		~TemporaryProfileConfig() {
			std::error_code error;
			std::filesystem::remove(path, error);
		}

		void write(std::string_view content) const {
			std::ofstream output(path, std::ios::trunc);
			ASSERT_TRUE(output.is_open());
			output << content;
			ASSERT_TRUE(output.good());
		}

		[[nodiscard]] const std::filesystem::path &getPath() const {
			return path;
		}

	private:
		std::filesystem::path path;
	};
}

TEST(Mge002GameProfileTest, MissingProfileFieldsUseBackwardCompatibleDefaults) {
	TemporaryProfileConfig configFile;
	configFile.write("-- defaults\n");

	ConfigManager manager;
	manager.setConfigFileLua(configFile.getPath().string());
	ASSERT_TRUE(manager.load());

	const auto profile = manager.getGameProfile();
	ASSERT_NE(profile, nullptr);
	EXPECT_EQ(profile->id, "current");
	EXPECT_EQ(profile->protocolProfile, ProtocolProfileId::Current);
	EXPECT_TRUE(profile->allowOldProtocolProfiles);
	EXPECT_EQ(profile->rules.worldType, GameProfileWorldType::Pvp);
	EXPECT_EQ(profile->content.coreDirectory, "data");
	EXPECT_EQ(profile->content.dataPackDirectory, "data-otservbr-global");
	EXPECT_EQ(profile->content.mapName, "canary");
	EXPECT_EQ(profile->network.loginPort, 7171);
	EXPECT_EQ(profile->network.statusPort, 7171);
	EXPECT_EQ(profile->network.modernGamePort, 7172);
	EXPECT_EQ(profile->network.legacy1100GamePort, 7173);
	EXPECT_EQ(profile->network.legacy860GamePort, 7174);
}

TEST(Mge002GameProfileTest, ValidProfileCopiesRulesContentAndEffectivePorts) {
	TemporaryProfileConfig configFile;
	configFile.write(R"(
gameProfileId = "custom-current"
gameProtocolProfile = "CURRENT"
allowOldProtocol = true
worldType = "NO-PVP"
coreDirectory = "engine-data"
dataPackDirectory = "custom-pack"
mapName = "custom-world"
useAnyDatapackFolder = true
toggleMapCustom = false
loginProtocolPort = 8100
statusProtocolPort = 8100
gameProtocolPort = 8200
legacy1100GameProtocolPort = 0
legacy860GameProtocolPort = 8300
)");

	ConfigManager manager;
	manager.setConfigFileLua(configFile.getPath().string());
	ASSERT_TRUE(manager.load());

	const auto profile = manager.getGameProfile();
	ASSERT_NE(profile, nullptr);
	EXPECT_EQ(profile->id, "custom-current");
	EXPECT_EQ(profile->rules.worldType, GameProfileWorldType::NoPvp);
	EXPECT_EQ(profile->content.coreDirectory, "engine-data");
	EXPECT_EQ(profile->content.dataPackDirectory, "custom-pack");
	EXPECT_EQ(profile->content.mapName, "custom-world");
	EXPECT_TRUE(profile->content.allowAnyDatapackFolder);
	EXPECT_FALSE(profile->content.loadCustomMaps);
	EXPECT_EQ(profile->network.loginPort, 8100);
	EXPECT_EQ(profile->network.statusPort, 8100);
	EXPECT_EQ(profile->network.modernGamePort, 8200);
	EXPECT_EQ(profile->network.legacy1100GamePort, 8201);
	EXPECT_EQ(profile->network.legacy860GamePort, 8300);
}

TEST(Mge002GameProfileTest, DisabledLegacyProtocolsPublishZeroLegacyPorts) {
	TemporaryProfileConfig configFile;
	configFile.write(R"(
allowOldProtocol = false
legacy1100GameProtocolPort = 9000
legacy860GameProtocolPort = 9001
)");

	ConfigManager manager;
	manager.setConfigFileLua(configFile.getPath().string());
	ASSERT_TRUE(manager.load());

	const auto profile = manager.getGameProfile();
	ASSERT_NE(profile, nullptr);
	EXPECT_FALSE(profile->allowOldProtocolProfiles);
	EXPECT_EQ(profile->network.legacy1100GamePort, 0);
	EXPECT_EQ(profile->network.legacy860GamePort, 0);
}

TEST(Mge002GameProfileTest, InvalidProfileInputFailsWithoutPublishingSnapshot) {
	const std::array<std::string_view, 13> invalidConfigs {
		"gameProfileId = 'Invalid Profile'\n",
		"gameProfileId = 123\n",
		"gameProtocolProfile = 'missing'\n",
		"gameProtocolProfile = 'tibia1100'\n",
		"worldType = 'open-pvp'\n",
		"dataPackDirectory = 'unregistered-pack'\n",
		"coreDirectory = ''\n",
		"gameProtocolPort = 0\n",
		"legacy1100GameProtocolPort = 70000\n",
		"loginProtocolPort = 7172\ngameProtocolPort = 7172\n",
		"legacy1100GameProtocolPort = 7172\n",
		"legacy860GameProtocolPort = 7173\n",
		"gameProtocolPort = 65535\n",
	};

	for (const auto invalidConfig : invalidConfigs) {
		TemporaryProfileConfig configFile;
		configFile.write(invalidConfig);
		ConfigManager manager;
		manager.setConfigFileLua(configFile.getPath().string());
		EXPECT_FALSE(manager.load()) << invalidConfig;
		EXPECT_EQ(manager.getGameProfile(), nullptr) << invalidConfig;
	}
}

TEST(Mge002GameProfileTest, FailedLoadCanRecoverAndPublishValidatedSnapshot) {
	TemporaryProfileConfig configFile;
	ConfigManager manager;
	manager.setConfigFileLua(configFile.getPath().string());

	configFile.write("gameProfileId = 'INVALID'\n");
	ASSERT_FALSE(manager.load());
	ASSERT_EQ(manager.getGameProfile(), nullptr);

	configFile.write("gameProfileId = 'recovered'\n");
	ASSERT_TRUE(manager.load());
	const auto recovered = manager.getGameProfile();
	ASSERT_NE(recovered, nullptr);
	EXPECT_EQ(recovered->id, "recovered");
}

TEST(Mge002GameProfileTest, ReloadDoesNotReplaceStartupOnlySnapshot) {
	TemporaryProfileConfig configFile;
	ConfigManager manager;
	manager.setConfigFileLua(configFile.getPath().string());

	configFile.write(R"(
gameProfileId = "initial"
worldType = "pvp"
dataPackDirectory = "data-canary"
mapName = "initial-map"
gameProtocolPort = 7200
)");
	ASSERT_TRUE(manager.load());
	const auto initial = manager.getGameProfile();
	ASSERT_NE(initial, nullptr);

	configFile.write(R"(
gameProfileId = "changed"
worldType = "no-pvp"
dataPackDirectory = "data-otservbr-global"
mapName = "changed-map"
gameProtocolPort = 7300
)");
	ASSERT_TRUE(manager.reload());
	const auto afterReload = manager.getGameProfile();
	ASSERT_NE(afterReload, nullptr);
	EXPECT_EQ(afterReload, initial);
	EXPECT_EQ(afterReload->id, "initial");
	EXPECT_EQ(afterReload->rules.worldType, GameProfileWorldType::Pvp);
	EXPECT_EQ(afterReload->network.modernGamePort, 7200);
	EXPECT_EQ(manager.getString(WORLD_TYPE), "pvp");
	EXPECT_EQ(manager.getString(DATA_DIRECTORY), "data-canary");
	EXPECT_EQ(manager.getString(MAP_NAME), "initial-map");
	EXPECT_EQ(manager.getNumber(GAME_PORT), 7200);
}
