#include "pch.hpp"

#include <gtest/gtest.h>

#include "creatures/players/imbuements/imbuement_storage_policy.hpp"

TEST(ImbuementStoragePolicyTest, ReadsTheConfiguredStorageId) {
	uint32_t requestedStorage = 0;
	const bool hidden = ImbuementStoragePolicy::shouldHide(true, 30059, 3, [&requestedStorage](uint32_t storageId) {
		requestedStorage = storageId;
		return -1;
	});

	EXPECT_TRUE(hidden);
	EXPECT_EQ(30059, requestedStorage);
}
