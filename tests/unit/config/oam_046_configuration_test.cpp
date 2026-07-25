#include "config/configmanager.hpp"

#include <algorithm>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <functional>
#include <string>
#include <string_view>
#include <system_error>
#include <thread>
#include <vector>

#include <gtest/gtest.h>

namespace {

	class TemporaryConfigFile final {
	public:
		TemporaryConfigFile() {
			const auto timestamp = std::chrono::steady_clock::now().time_since_epoch().count();
			const auto threadId = std::hash<std::thread::id> {}(std::this_thread::get_id());
			path = std::filesystem::temp_directory_path() / ("oam_046_configuration_" + std::to_string(timestamp) + "_" + std::to_string(threadId) + ".lua");
		}

		~TemporaryConfigFile() {
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

	OTCFeatures sorted(OTCFeatures features) {
		std::ranges::sort(features);
		return features;
	}

} // namespace

TEST(Oam046ConfigurationTest, SuccessfulLoadsReplaceOtcrFeatureSnapshots) {
	TemporaryConfigFile configFile;
	ConfigManager manager;
	manager.setConfigFileLua(configFile.getPath().string());

	configFile.write(R"(
OTCRFeatures = {
	enableFeature = { 101, 102 },
	disableFeature = { 201 }
}
)");
	ASSERT_TRUE(manager.load());
	EXPECT_EQ(sorted(manager.getEnabledFeaturesOTC()), (OTCFeatures { 101, 102 }));
	EXPECT_EQ(sorted(manager.getDisabledFeaturesOTC()), (OTCFeatures { 201 }));

	configFile.write(R"(
OTCRFeatures = {
	enableFeature = { 103 },
	disableFeature = { 202, 203 }
}
)");
	ASSERT_TRUE(manager.load());
	EXPECT_EQ(sorted(manager.getEnabledFeaturesOTC()), (OTCFeatures { 103 }));
	EXPECT_EQ(sorted(manager.getDisabledFeaturesOTC()), (OTCFeatures { 202, 203 }));

	configFile.write("-- OTCRFeatures intentionally omitted\n");
	ASSERT_TRUE(manager.load());
	EXPECT_EQ(sorted(manager.getEnabledFeaturesOTC()), (OTCFeatures { 101, 102, 103, 118 }));
	EXPECT_TRUE(manager.getDisabledFeaturesOTC().empty());

	ASSERT_TRUE(manager.load());
	EXPECT_EQ(sorted(manager.getEnabledFeaturesOTC()), (OTCFeatures { 101, 102, 103, 118 }));
	EXPECT_TRUE(manager.getDisabledFeaturesOTC().empty());
}
