#include "server/network/protocol/protocol_session_hint.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <chrono>
	#include <string>
	#include <vector>
#endif

namespace {
	constexpr uint32_t currentIp = 0x0A000001;
	constexpr uint32_t reusableIp = 0x0A000002;
	constexpr uint32_t replacementIp = 0x0A000003;
	constexpr uint32_t ambiguousIp = 0x0A000004;
	constexpr uint32_t blockedIp = 0x0A000005;
}

TEST(Oam045ProtocolSessionHandoffTest, CurrentHintIsOneShotAndRequiresExactSessionCharacterAndVersion) {
	ProtocolSessionHintStore store;
	store.registerHint(currentIp, ProtocolProfileId::Current, "current-session", { "Knight One" });

	const auto lease = store.claimByIp(currentIp);
	ASSERT_TRUE(lease.has_value());
	ASSERT_EQ(1U, lease->candidateIds.size());

	EXPECT_FALSE(store.consumeIfMatches(*lease, "wrong-session", "Knight One", CLIENT_VERSION));
	EXPECT_FALSE(store.consumeIfMatches(*lease, "current-session", "Wrong Knight", CLIENT_VERSION));
	EXPECT_FALSE(store.consumeIfMatches(*lease, "current-session", "Knight One", 1100));

	EXPECT_TRUE(store.consumeIfMatches(*lease, "current-session", "kNiGhT oNe", CLIENT_VERSION));
	EXPECT_FALSE(store.consumeIfMatches(*lease, "current-session", "Knight One", CLIENT_VERSION));
	EXPECT_FALSE(store.claimByIp(currentIp).has_value());
}

TEST(Oam045ProtocolSessionHandoffTest, ReusableHintCanBeReclaimedAndClearedByWireBehavior) {
	ProtocolSessionHintStore store;
	const auto* tibia1100 = ProtocolProfileRegistry::getProfile(ProtocolProfileId::Tibia1100);
	ASSERT_NE(nullptr, tibia1100);

	store.registerHint(reusableIp, ProtocolProfileId::Tibia1100, "legacy-session", { "Legacy Knight" });

	const auto firstLease = store.claimByIp(reusableIp, tibia1100->initialBehavior);
	ASSERT_TRUE(firstLease.has_value());
	EXPECT_EQ(ProtocolProfileId::Tibia1100, store.consumeAndResolveProfile(*firstLease, "legacy-session", "Legacy Knight", 1100));

	const auto secondLease = store.claimByIp(reusableIp, tibia1100->initialBehavior);
	ASSERT_TRUE(secondLease.has_value());
	EXPECT_EQ(ProtocolProfileId::Tibia1100, store.consumeAndResolveProfile(*secondLease, "legacy-session", "Legacy Knight", 1100));

	store.clearReusableHintsByIp(reusableIp, tibia1100->initialBehavior);
	EXPECT_FALSE(store.claimByIp(reusableIp).has_value());
}

TEST(Oam045ProtocolSessionHandoffTest, ExpiredLeaseCannotConsumeAStillValidReusableHint) {
	ProtocolSessionHintStore store;
	store.registerHint(reusableIp, ProtocolProfileId::Tibia1100, "lease-session", { "Lease Knight" });

	const auto lease = store.claimByIp(reusableIp);
	ASSERT_TRUE(lease.has_value());

	auto expiredLease = *lease;
	expiredLease.expiresAt = std::chrono::steady_clock::now() - std::chrono::seconds(1);
	EXPECT_FALSE(store.consumeAndResolveProfile(expiredLease, "lease-session", "Lease Knight", 1100).has_value());

	const auto freshLease = store.claimByIp(reusableIp);
	ASSERT_TRUE(freshLease.has_value());
	EXPECT_EQ(ProtocolProfileId::Tibia1100, store.consumeAndResolveProfile(*freshLease, "lease-session", "Lease Knight", 1100));
}

TEST(Oam045ProtocolSessionHandoffTest, RegisteringAnOverlappingCharacterReplacesTheOlderHint) {
	ProtocolSessionHintStore store;
	store.registerHint(replacementIp, ProtocolProfileId::Current, "old-session", { "Replacement Knight" });
	store.registerHint(replacementIp, ProtocolProfileId::Current, "new-session", { "replacement knight" });

	const auto lease = store.claimByIp(replacementIp);
	ASSERT_TRUE(lease.has_value());
	ASSERT_EQ(1U, lease->candidateIds.size());
	EXPECT_FALSE(store.consumeIfMatches(*lease, "old-session", "Replacement Knight", CLIENT_VERSION));
	EXPECT_TRUE(store.consumeIfMatches(*lease, "new-session", "Replacement Knight", CLIENT_VERSION));
}

TEST(Oam045ProtocolSessionHandoffTest, MixedWireBehaviorsRequireAnExplicitBehaviorFilter) {
	ProtocolSessionHintStore store;
	const auto* current = ProtocolProfileRegistry::getProfile(ProtocolProfileId::Current);
	const auto* tibia1100 = ProtocolProfileRegistry::getProfile(ProtocolProfileId::Tibia1100);
	ASSERT_NE(nullptr, current);
	ASSERT_NE(nullptr, tibia1100);

	store.registerHint(ambiguousIp, ProtocolProfileId::Current, "modern-session", { "Modern Knight" });
	store.registerHint(ambiguousIp, ProtocolProfileId::Tibia1100, "legacy-session", { "Legacy Knight" });

	EXPECT_FALSE(store.claimByIp(ambiguousIp).has_value());

	const auto currentLease = store.claimByIp(ambiguousIp, current->initialBehavior);
	ASSERT_TRUE(currentLease.has_value());
	EXPECT_EQ(ProtocolProfileId::Current, store.consumeAndResolveProfile(*currentLease, "modern-session", "Modern Knight", CLIENT_VERSION));

	const auto legacyLease = store.claimByIp(ambiguousIp, tibia1100->initialBehavior);
	ASSERT_TRUE(legacyLease.has_value());
	EXPECT_EQ(ProtocolProfileId::Tibia1100, store.consumeAndResolveProfile(*legacyLease, "legacy-session", "Legacy Knight", 1100));
}

TEST(Oam045ProtocolSessionHandoffTest, BlockedProfilesAreNotRegistered) {
	ProtocolSessionHintStore store;
	store.registerHint(blockedIp, ProtocolProfileId::OTCv8Extended860, "blocked-session", { "Blocked Knight" });
	EXPECT_FALSE(store.claimByIp(blockedIp).has_value());
}

TEST(Oam045ProtocolSessionHandoffTest, CapacityEvictsTheOldestHint) {
	ProtocolSessionHintStore store;
	constexpr uint32_t firstIp = 0x0B000000;
	constexpr size_t capacity = 512;

	for (size_t index = 0; index <= capacity; ++index) {
		store.registerHint(
			firstIp + static_cast<uint32_t>(index),
			ProtocolProfileId::Current,
			"capacity-session-" + std::to_string(index),
			{ "Capacity Knight " + std::to_string(index) }
		);
	}

	EXPECT_FALSE(store.claimByIp(firstIp).has_value());
	EXPECT_TRUE(store.claimByIp(firstIp + static_cast<uint32_t>(capacity)).has_value());
}
