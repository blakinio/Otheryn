/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "server/network/protocol/protocol_profile.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <array>
	#include <cstdint>
#endif

namespace {
	struct ExpectedProfile {
		ProtocolProfileId id;
		uint16_t version;
		ProtocolSupportState support;
		ItemMapperPolicy mapper;
		bool oldProtocol;
	};

	struct ReviewedClientGate {
		ProtocolFeature serverFeature;
		uint16_t firstClientVersion;
	};

	constexpr std::array expectedProfiles {
		ExpectedProfile { ProtocolProfileId::Current, CLIENT_VERSION, ProtocolSupportState::Enabled, ItemMapperPolicy::NotRequired, false },
		ExpectedProfile { ProtocolProfileId::Tibia1100, 1100, ProtocolSupportState::Enabled, ItemMapperPolicy::NotRequired, true },
		ExpectedProfile { ProtocolProfileId::Cipsoft860Vanilla, 860, ProtocolSupportState::Enabled, ItemMapperPolicy::RequiredBeforeWorldEnter, true },
		ExpectedProfile { ProtocolProfileId::Cipsoft860ExtendedAssets, 860, ProtocolSupportState::Enabled, ItemMapperPolicy::NotRequired, true },
		ExpectedProfile { ProtocolProfileId::Cipsoft860CanaryExtended, 860, ProtocolSupportState::Enabled, ItemMapperPolicy::NotRequired, true },
		ExpectedProfile { ProtocolProfileId::OTCv8Extended860, 860, ProtocolSupportState::BlockedPendingFixture, ItemMapperPolicy::RequiredBeforeWorldEnter, true },
	};

	// Exact maintained-client source at the reviewed blob enables the corresponding
	// GameFeature gates at these versions. The test deliberately covers only
	// semantically reviewed pairs and does not infer one-to-one name equivalence.
	constexpr std::array reviewedCurrentClientGates {
		ReviewedClientGate { ProtocolFeature::MarketPackets, 940 },
		ReviewedClientGate { ProtocolFeature::CustomMonkPackets, 1500 },
		ReviewedClientGate { ProtocolFeature::OfficialWeaponProficiencyPayload, 1510 },
		ReviewedClientGate { ProtocolFeature::GraphicalEffectSourceByte, 1514 },
		ReviewedClientGate { ProtocolFeature::PlayerDataLevelPercentU16, 1520 },
		ReviewedClientGate { ProtocolFeature::OfficialTaskboardPackets, 1520 },
	};
}

TEST(Oam044ProtocolCompatibilityTest, RegistryMatchesReviewedProfileManifest) {
	for (const auto &expected : expectedProfiles) {
		const auto* profile = ProtocolProfileRegistry::getProfile(expected.id);
		ASSERT_NE(nullptr, profile);
		EXPECT_EQ(expected.version, profile->clientVersion);
		EXPECT_EQ(expected.support, profile->supportState);
		EXPECT_EQ(expected.mapper, profile->itemMapperPolicy);
		EXPECT_EQ(expected.oldProtocol, profile->hasFeature(ProtocolFeature::OldProtocolCompat));
		EXPECT_EQ(expected.support == ProtocolSupportState::Enabled, ProtocolProfileRegistry::isProfileAllowed(expected.id));
	}

	EXPECT_EQ(nullptr, ProtocolProfileRegistry::resolveByClientVersion(859));
	EXPECT_EQ(nullptr, ProtocolProfileRegistry::resolveByClientVersion(861));
	EXPECT_EQ(nullptr, ProtocolProfileRegistry::resolveByClientVersion(1099));
	EXPECT_EQ(nullptr, ProtocolProfileRegistry::resolveByClientVersion(1101));

	EXPECT_EQ("15.25, 10x and 8.6", ProtocolProfileRegistry::getAllowedClientProtocolDescription(true));
}

TEST(Oam044ProtocolCompatibilityTest, CurrentProfileMatchesReviewedMaintainedClientGates) {
	const auto &current = ProtocolProfileRegistry::getCurrentProfile();
	EXPECT_EQ(CLIENT_VERSION, current.clientVersion);
	EXPECT_EQ(ProtocolProfileId::Current, current.id);
	EXPECT_EQ(ClientWireFamily::CipsoftVanilla, current.wireFamily);
	EXPECT_EQ(ProtocolSupportState::Enabled, current.supportState);

	for (const auto &gate : reviewedCurrentClientGates) {
		EXPECT_GE(current.clientVersion, gate.firstClientVersion);
		EXPECT_TRUE(current.hasFeature(gate.serverFeature));
	}

	const auto* accountLayout = ProtocolProfileRegistry::resolveAccountLoginLayout(ProtocolProfileId::Current);
	const auto* gameLayout = ProtocolProfileRegistry::resolveGameLoginLayout(ProtocolProfileId::Current);
	ASSERT_NE(nullptr, accountLayout);
	ASSERT_NE(nullptr, gameLayout);
	EXPECT_EQ(AccountCharacterListLayout::WorldListWithSessionKey, accountLayout->characterListLayout);
	EXPECT_TRUE(accountLayout->sendsSessionKey);
	EXPECT_EQ(GameLoginAuthenticationLayout::SessionKey, gameLayout->authenticationLayout);
	EXPECT_TRUE(gameLayout->hasClientVersionU32);
	EXPECT_TRUE(gameLayout->hasClientVersionString);
	EXPECT_TRUE(gameLayout->hasAssetHashString);
	EXPECT_TRUE(gameLayout->hasPreviewState);
}

TEST(Oam044ProtocolCompatibilityTest, LegacyLayoutsRemainExplicitAndFailClosed) {
	const auto* tibia1100 = ProtocolProfileRegistry::getProfile(ProtocolProfileId::Tibia1100);
	const auto* tibia1100Account = ProtocolProfileRegistry::resolveAccountLoginLayout(ProtocolProfileId::Tibia1100);
	const auto* tibia1100Game = ProtocolProfileRegistry::resolveGameLoginLayout(ProtocolProfileId::Tibia1100);
	ASSERT_NE(nullptr, tibia1100);
	ASSERT_NE(nullptr, tibia1100Account);
	ASSERT_NE(nullptr, tibia1100Game);
	EXPECT_TRUE(tibia1100->hasFeature(ProtocolFeature::OldProtocolCompat));
	EXPECT_TRUE(tibia1100->hasFeature(ProtocolFeature::MarketPackets));
	EXPECT_TRUE(tibia1100->hasFeature(ProtocolFeature::ImbuementWindow));
	EXPECT_FALSE(tibia1100->hasFeature(ProtocolFeature::CurrentPayload));
	EXPECT_EQ(AccountCharacterListLayout::WorldListWithSessionKey, tibia1100Account->characterListLayout);
	EXPECT_TRUE(tibia1100Account->sendsSessionKey);
	EXPECT_EQ(GameLoginAuthenticationLayout::SessionKey, tibia1100Game->authenticationLayout);
	EXPECT_TRUE(tibia1100Game->hasContentRevisionU16);
	EXPECT_FALSE(tibia1100Game->hasClientVersionString);

	const auto* shippedExtended = ProtocolProfileRegistry::resolveByClientVersionAndAssets(
		860,
		ClientAssetSignatures {
			.dat = 0x4C2C7993,
			.spr = 0x4C220594,
			.pic = 0x4AE5C3D3,
		},
		ClientWireFamily::CipsoftVanilla
	);
	ASSERT_NE(nullptr, shippedExtended);
	EXPECT_EQ(ProtocolProfileId::Cipsoft860CanaryExtended, shippedExtended->id);
	EXPECT_TRUE(shippedExtended->hasFeature(ProtocolFeature::ExtendedSpriteFiles));
	EXPECT_TRUE(shippedExtended->hasFeature(ProtocolFeature::MagicEffectU16));
	EXPECT_FALSE(shippedExtended->hasFeature(ProtocolFeature::RequiresItemMapper));

	const auto* vanilla860Account = ProtocolProfileRegistry::resolveAccountLoginLayout(ProtocolProfileId::Cipsoft860Vanilla);
	const auto* vanilla860Game = ProtocolProfileRegistry::resolveGameLoginLayout(ProtocolProfileId::Cipsoft860Vanilla);
	ASSERT_NE(nullptr, vanilla860Account);
	ASSERT_NE(nullptr, vanilla860Game);
	EXPECT_EQ(AccountCharacterListLayout::LegacyCharacterList, vanilla860Account->characterListLayout);
	EXPECT_FALSE(vanilla860Account->sendsSessionKey);
	EXPECT_EQ(GameLoginAuthenticationLayout::AccountPassword, vanilla860Game->authenticationLayout);
	EXPECT_FALSE(vanilla860Game->hasOtcV8Probe);

	EXPECT_FALSE(ProtocolProfileRegistry::isProfileAllowed(ProtocolProfileId::OTCv8Extended860));
	EXPECT_EQ(nullptr, ProtocolProfileRegistry::resolveAccountLoginLayout(ProtocolProfileId::OTCv8Extended860));
	EXPECT_EQ(nullptr, ProtocolProfileRegistry::resolveGameLoginLayout(ProtocolProfileId::OTCv8Extended860));
}
