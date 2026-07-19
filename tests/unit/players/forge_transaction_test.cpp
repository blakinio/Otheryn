/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include <gtest/gtest.h>

#include <stdexcept>
#include <vector>

#include "game/functions/forge_transaction.hpp"

TEST(ForgeTransactionTest, CommitsAllStepsWithoutRollback) {
	std::vector<int> events;
	ForgeTransaction transaction;
	transaction.stage(
		[&events] {
			events.push_back(1);
			return true;
		},
		[&events] { events.push_back(-1); }
	);
	transaction.stage(
		[&events] {
			events.push_back(2);
			return true;
		},
		[&events] { events.push_back(-2); }
	);

	EXPECT_TRUE(transaction.commit());
	EXPECT_TRUE(transaction.isCommitted());
	EXPECT_EQ((std::vector<int> { 1, 2 }), events);
}

TEST(ForgeTransactionTest, RollsBackFailedStepAndPriorStepsInReverseOrder) {
	std::vector<int> events;
	ForgeTransaction transaction;
	transaction.stage(
		[&events] {
			events.push_back(1);
			return true;
		},
		[&events] { events.push_back(-1); }
	);
	transaction.stage(
		[&events] {
			events.push_back(2);
			return false;
		},
		[&events] { events.push_back(-2); }
	);
	transaction.stage(
		[&events] {
			events.push_back(3);
			return true;
		},
		[&events] { events.push_back(-3); }
	);

	EXPECT_FALSE(transaction.commit());
	EXPECT_FALSE(transaction.isCommitted());
	EXPECT_EQ((std::vector<int> { 1, 2, -2, -1 }), events);
}

TEST(ForgeTransactionTest, RestoresResourcesWhenFailedStepMutatesBeforeReturningFalse) {
	int firstItemCount = 1;
	int secondItemCount = 1;
	int coreCount = 4;
	int gold = 100;

	ForgeTransaction transaction;
	transaction.stage(
		[&firstItemCount] {
			--firstItemCount;
			return true;
		},
		[&firstItemCount] { ++firstItemCount; }
	);
	transaction.stage(
		[&secondItemCount] {
			--secondItemCount;
			return true;
		},
		[&secondItemCount] { ++secondItemCount; }
	);
	transaction.stage(
		[&coreCount] {
			coreCount -= 2;
			return true;
		},
		[&coreCount] { coreCount = 4; }
	);
	transaction.stage(
		[&gold] {
			gold -= 60;
			return false;
		},
		[&gold] { gold = 100; }
	);

	EXPECT_FALSE(transaction.commit());
	EXPECT_EQ(1, firstItemCount);
	EXPECT_EQ(1, secondItemCount);
	EXPECT_EQ(4, coreCount);
	EXPECT_EQ(100, gold);
}

TEST(ForgeTransactionTest, RollsBackWhenCommitStepThrows) {
	std::vector<int> events;
	ForgeTransaction transaction;
	transaction.stage(
		[&events] {
			events.push_back(1);
			return true;
		},
		[&events] { events.push_back(-1); }
	);
	transaction.stage(
		[&events]() -> bool {
			events.push_back(2);
			throw std::runtime_error("commit failure");
		},
		[&events] { events.push_back(-2); }
	);

	EXPECT_FALSE(transaction.commit());
	EXPECT_FALSE(transaction.isCommitted());
	EXPECT_EQ((std::vector<int> { 1, 2, -2, -1 }), events);
}

TEST(ForgeTransactionTest, CannotCommitTwice) {
	ForgeTransaction transaction;
	transaction.stage([] { return true; }, [] {});

	EXPECT_TRUE(transaction.commit());
	EXPECT_FALSE(transaction.commit());
}
