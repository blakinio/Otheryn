#include <gtest/gtest.h>

#ifndef USE_PRECOMPILED_HEADERS
	#include <fstream>
	#include <iterator>
	#include <string>
	#include <string_view>
#endif

namespace {
std::string readHelpChannelScript() {
	std::ifstream file(std::string(TESTS_SOURCE_DIR) + "/data/chatchannels/scripts/help.lua");
	if (!file.is_open()) {
		return {};
	}
	return { std::istreambuf_iterator<char>(file), std::istreambuf_iterator<char>() };
}

size_t countOccurrences(std::string_view haystack, std::string_view needle) {
	size_t count = 0;
	for (size_t pos = 0; (pos = haystack.find(needle, pos)) != std::string_view::npos; pos += needle.size()) {
		++count;
	}
	return count;
}
} // namespace

TEST(Oam025ChatCommunicationAdaptTest, HelpModerationUsesOneGroupPrivilegeDomain) {
	const std::string script = readHelpChannelScript();
	ASSERT_FALSE(script.empty());

	EXPECT_EQ(script.find("target:getAccountType()"), std::string::npos);
	EXPECT_EQ(countOccurrences(script, "playerGroupType > target:getGroup():getId()"), 2u);
}
