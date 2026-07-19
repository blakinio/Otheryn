/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include <gtest/gtest.h>

#include <fstream>
#include <iterator>
#include <regex>
#include <string>

#include "config/forge_config_defaults.hpp"

namespace {
	std::string readRepositoryFile(const std::string &relativePath) {
		std::ifstream input(std::string(TESTS_SOURCE_DIR) + "/" + relativePath);
		if (!input.is_open()) {
			return {};
		}
		return { std::istreambuf_iterator<char>(input), std::istreambuf_iterator<char>() };
	}

	bool hasLuaIntegerAssignment(const std::string &content, const std::string &name, int32_t value) {
		const std::regex expression("(^|\\n)[\\t ]*" + name + "[\\t ]*=[\\t ]*" + std::to_string(value) + "[\\t ]*[,;]?[\\t ]*(\\r?\\n|$)");
		return std::regex_search(content, expression);
	}
} // namespace

TEST(ForgeConfigTest, RetailDefaultsArePinnedInCpp) {
	EXPECT_EQ(325, ForgeConfigDefaults::maxDust);
	EXPECT_EQ(4, ForgeConfigDefaults::fiendishCreaturesLimit);
}

TEST(ForgeConfigTest, DistributedLuaConfigMatchesCppDefaults) {
	const std::string config = readRepositoryFile("config.lua.dist");
	ASSERT_FALSE(config.empty());
	EXPECT_TRUE(hasLuaIntegerAssignment(config, "forgeMaxDust", ForgeConfigDefaults::maxDust));
	EXPECT_TRUE(hasLuaIntegerAssignment(config, "forgeFiendishLimit", ForgeConfigDefaults::fiendishCreaturesLimit));
}

TEST(ForgeConfigTest, ForgeLuaLibraryMatchesFiendishDefault) {
	const std::string forgeLibrary = readRepositoryFile("data/libs/systems/exaltation_forge.lua");
	ASSERT_FALSE(forgeLibrary.empty());
	EXPECT_TRUE(hasLuaIntegerAssignment(forgeLibrary, "maxFiendish", ForgeConfigDefaults::fiendishCreaturesLimit));
}
