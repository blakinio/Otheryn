#include "database/database.hpp"
#include "database/player_writer_fence_repository.hpp"

#include <fmt/format.h>

#include <atomic>
#include <future>
#include <string>

namespace it_player_writer_fence_repository {

	class PlayerWriterFenceRepositoryTest : public ::testing::Test {
	protected:
		void SetUp() override {
			static std::atomic_uint64_t sequence = 0;
			playerName = fmt::format("PRS004C Subject {}", ++sequence);
			ASSERT_TRUE(g_database().executeQuery(fmt::format(
				"INSERT INTO `players` (`name`, `account_id`, `conditions`) VALUES ({}, 1, '')",
				g_database().escapeString(playerName)
			)));
			playerId = static_cast<uint32_t>(g_database().getLastInsertId());
			ASSERT_NE(0, playerId);
		}

		void TearDown() override {
			if (playerId != 0) {
				EXPECT_TRUE(g_database().executeQuery(fmt::format("DELETE FROM `players` WHERE `id` = {}", playerId)));
			}
		}

		static PlayerWriterFenceToken token(uint8_t seed) {
			PlayerWriterFenceToken value {};
			for (size_t index = 0; index < value.size(); ++index) {
				value[index] = static_cast<uint8_t>(seed + index);
			}
			return value;
		}

		PlayerWriterFenceContext context(uint64_t generation, uint8_t tokenSeed, uint64_t revision = 0) const {
			return {
				.playerId = playerId,
				.ownershipGeneration = generation,
				.writerToken = token(tokenSeed),
				.stateRevision = revision,
			};
		}

		struct Snapshot final {
			uint64_t generation = 0;
			std::string tokenHex;
			uint64_t revision = 0;
		};

		Snapshot snapshot() const {
			const auto result = g_database().storeQuery(fmt::format(
				"SELECT `ownership_generation`, COALESCE(HEX(`writer_token`), '') AS `token_hex`, `state_revision` "
				"FROM `player_writer_fence` WHERE `player_id` = {}",
				playerId
			));
			EXPECT_NE(nullptr, result);
			if (!result) {
				return {};
			}
			return {
				.generation = result->getNumber<uint64_t>("ownership_generation"),
				.tokenHex = result->getString("token_hex"),
				.revision = result->getNumber<uint64_t>("state_revision"),
			};
		}

		PlayerWriterFenceRepository repository;
		uint32_t playerId = 0;
		std::string playerName;
	};

	TEST_F(PlayerWriterFenceRepositoryTest, AcquireTransferAdvanceReleaseAndReacquirePreserveMonotonicHistory) {
		const auto first = context(10, 1);
		EXPECT_EQ(PlayerWriterFenceResult::Applied, repository.acquire(first));
		EXPECT_EQ(PlayerWriterFenceResult::StaleConflict, repository.acquire(first));

		const auto second = context(11, 33);
		EXPECT_EQ(PlayerWriterFenceResult::Applied, repository.transfer(first, second));
		EXPECT_EQ(PlayerWriterFenceResult::StaleConflict, repository.advanceRevision(first, 1));
		EXPECT_EQ(PlayerWriterFenceResult::Applied, repository.advanceRevision(second, 1));

		const auto secondRevision = context(11, 33, 1);
		EXPECT_EQ(PlayerWriterFenceResult::Applied, repository.release(secondRevision));

		const auto released = snapshot();
		EXPECT_EQ(11, released.generation);
		EXPECT_TRUE(released.tokenHex.empty());
		EXPECT_EQ(1, released.revision);

		EXPECT_EQ(PlayerWriterFenceResult::StaleConflict, repository.acquire(context(11, 65, 1)));
		const auto third = context(12, 65, 1);
		EXPECT_EQ(PlayerWriterFenceResult::Applied, repository.acquire(third));
	}

	TEST_F(PlayerWriterFenceRepositoryTest, ConcurrentAcquireProducesExactlyOneAuthority) {
		const auto first = context(20, 3);
		const auto second = context(20, 67);

		auto firstResult = std::async(std::launch::async, [&] {
			return repository.acquire(first);
		});
		auto secondResult = std::async(std::launch::async, [&] {
			return repository.acquire(second);
		});

		const auto a = firstResult.get();
		const auto b = secondResult.get();
		EXPECT_TRUE(
			(a == PlayerWriterFenceResult::Applied && b == PlayerWriterFenceResult::StaleConflict)
			|| (a == PlayerWriterFenceResult::StaleConflict && b == PlayerWriterFenceResult::Applied)
		);
	}

	TEST_F(PlayerWriterFenceRepositoryTest, MalformedAndRevisionGapFailBeforeMutation) {
		auto malformed = context(1, 1);
		malformed.playerId = 0;
		EXPECT_EQ(PlayerWriterFenceResult::MalformedContext, repository.acquire(malformed));

		const auto current = context(1, 1);
		ASSERT_EQ(PlayerWriterFenceResult::Applied, repository.acquire(current));
		EXPECT_EQ(PlayerWriterFenceResult::MalformedContext, repository.advanceRevision(current, 2));
		EXPECT_EQ(0, snapshot().revision);
	}

	TEST_F(PlayerWriterFenceRepositoryTest, TransactionRollbackPreservesAuthorityRow) {
		const auto current = context(30, 9);
		ASSERT_EQ(PlayerWriterFenceResult::Applied, repository.acquire(current));

		EXPECT_FALSE(DBTransaction::executeWithinTransaction([&] {
			EXPECT_TRUE(g_database().executeQuery(fmt::format(
				"UPDATE `player_writer_fence` SET `state_revision` = 99 WHERE `player_id` = {}",
				playerId
			)));
			return false;
		}));

		const auto after = snapshot();
		EXPECT_EQ(30, after.generation);
		EXPECT_EQ(0, after.revision);
	}

} // namespace it_player_writer_fence_repository
