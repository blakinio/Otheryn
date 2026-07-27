/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "server/network/protocol/protocollogin.hpp"

#include "config/configmanager.hpp"
#include "security/login_session_manager.hpp"
#include "server/network/message/outputmessage.hpp"
#include "server/network/protocol/login_protocol_wire.hpp"
#include "server/network/protocol/protocol_port_utils.hpp"
#include "server/network/protocol/protocol_session_hint.hpp"
#include "server/network/protocol/transport_codec.hpp"
#include "game/scheduling/dispatcher.hpp"
#include "account/account.hpp"
#include "creatures/players/livestream/livestream.hpp"
#include "creatures/players/player.hpp"
#include "io/iologindata.hpp"
#include "creatures/players/management/ban.hpp"
#include "game/game.hpp"
#include "core.hpp"
#include "enums/account_errors.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <array>
#endif

void ProtocolLogin::disconnectClient(const std::string &message) const {
	const auto output = OutputMessagePool::getOutputMessage();

	output->addByte(0x0B);
	output->addString(message);
	send(output);

	disconnect();
}

void ProtocolLogin::getCharacterList(const std::string &accountDescriptor, const std::string &password) const {
	Account account(accountDescriptor);
	account.setProtocolCompat(oldProtocol);

	if (oldProtocol && !g_configManager().getBoolean(OLD_PROTOCOL)) {
		disconnectClient(ProtocolProfileRegistry::getUnsupportedClientProtocolMessage(false));
		return;
	}

	if (account.load() != AccountErrors_t::Ok || !account.authenticate(password)) {
		std::ostringstream ss;
		ss << (oldProtocol ? "Username" : "Email") << " or password is not correct.";
		disconnectClient(ss.str());
		return;
	}

	auto output = OutputMessagePool::getOutputMessage();
	const std::string &motd = g_configManager().getString(SERVER_MOTD);
	if (!motd.empty()) {
		output->addByte(0x14);

		std::ostringstream ss;
		ss << g_game().getMotdNum() << "\n"
		   << motd;
		output->addString(ss.str());
	}

	auto [players, result] = account.getAccountPlayers();
	if (AccountErrors_t::Ok != result) {
		g_logger().warn("Account[{}] failed to load players!", account.getID());
	}

	const auto* loginLayout = protocolProfile ? ProtocolProfileRegistry::resolveAccountLoginLayout(protocolProfile->id) : nullptr;
	const auto characterListLayout = loginLayout ? loginLayout->characterListLayout : AccountCharacterListLayout::WorldListWithSessionKey;

	std::string sessionKey = accountDescriptor + "\n" + password;
	if (loginLayout && loginLayout->sendsSessionKey && !oldProtocol && protocolProfile && g_configManager().getString(AUTH_TYPE) == "session") {
		std::vector<std::string> allowedCharacterNames;
		allowedCharacterNames.reserve(players.size());
		for (const auto &[name, deletion] : players) {
			allowedCharacterNames.emplace_back(name);
		}

		LoginSessionIssueParams issueParams;
		issueParams.accountId = account.getID();
		issueParams.allowedCharacterNames = std::move(allowedCharacterNames);
		issueParams.protocolProfile = protocolProfile->id;

		auto secureToken = LoginSessionManager::getInstance().issueToken(issueParams);
		if (!secureToken) {
			g_logger().error("[ProtocolLogin::getCharacterList] Failed to issue secure login session token for account [{}]", account.getID());
			disconnectClient("Could not create a secure login session. Please try again.");
			return;
		}

		sessionKey = std::move(*secureToken);
	}

	if (loginLayout && loginLayout->sendsSessionKey) {
		login_protocol_wire::writeSessionKey(*output, sessionKey);
	}

	if (characterListLayout == AccountCharacterListLayout::LegacyCharacterList) {
		const auto serverName = g_configManager().getString(SERVER_NAME);
		const auto configuredWorldIp = g_configManager().getString(IP);
		const auto worldIp = protocol_port_utils::legacyIpStringToNumber(configuredWorldIp);
		if (worldIp == 0) {
			g_logger().warn("Legacy character list cannot encode configured IP '{}'; old clients require a numeric IPv4 address.", configuredWorldIp);
			disconnectClient("Legacy 8.60 clients require the server IP to be a numeric IPv4 address.");
			return;
		}

		const auto worldPort = protocolProfile ? protocol_port_utils::getGamePortForProfile(*protocolProfile) : protocol_port_utils::getModernGamePort();
		const auto serializedCount = std::min(players.size(), login_protocol_wire::MAX_CHARACTER_COUNT);
		std::vector<login_protocol_wire::LegacyCharacter> characters;
		std::vector<std::string> characterNames;
		characters.reserve(serializedCount);
		characterNames.reserve(serializedCount);
		for (size_t index = 0; index < serializedCount; ++index) {
			const auto &[name, deletion] = players[index];
			characters.emplace_back(login_protocol_wire::LegacyCharacter {
				.name = name,
				.worldName = serverName,
				.worldIp = worldIp,
				.worldPort = worldPort,
			});
			characterNames.emplace_back(name);
		}

		login_protocol_wire::writeLegacyCharacterList(
			*output,
			characters,
			static_cast<uint16_t>(std::min<uint32_t>(std::numeric_limits<uint16_t>::max(), account.getPremiumRemainingDays()))
		);
		send(output);

		if (protocolProfile) {
			ProtocolSessionHintStore::getInstance().registerHint(getIP(), protocolProfile->id, sessionKey, characterNames);
		}

		disconnect();
		return;
	}

	const auto serializedCount = std::min(players.size(), login_protocol_wire::MAX_CHARACTER_COUNT);
	std::vector<login_protocol_wire::ModernCharacter> characters;
	std::vector<std::string> characterNames;
	characters.reserve(serializedCount);
	characterNames.reserve(serializedCount);
	for (size_t index = 0; index < serializedCount; ++index) {
		const auto &[name, deletion] = players[index];
		characters.emplace_back(login_protocol_wire::ModernCharacter {
			.worldId = 0,
			.name = name,
		});
		characterNames.emplace_back(name);
	}

	const std::array worlds {
		login_protocol_wire::ModernWorld {
			.id = 0,
			.name = g_configManager().getString(SERVER_NAME),
			.host = g_configManager().getString(IP),
			.port = protocolProfile ? protocol_port_utils::getGamePortForProfile(*protocolProfile) : protocol_port_utils::getModernGamePort(),
			.previewState = 0,
		},
	};
	const bool freePremium = g_configManager().getBoolean(FREE_PREMIUM);
	const uint32_t premiumExpiry = freePremium ? 0 : account.getPremiumLastDay();
	const auto accountTail = login_protocol_wire::makeModernAccountTail(freePremium || premiumExpiry > getTimeNow(), premiumExpiry);
	login_protocol_wire::writeModernCharacterList(*output, worlds, characters, accountTail);
	send(output);

	if (protocolProfile) {
		ProtocolSessionHintStore::getInstance().registerHint(getIP(), protocolProfile->id, sessionKey, characterNames);
	}

	disconnect();
}

const AccountLoginLayout* ProtocolLogin::resolveLoginLayout(NetworkMessage &msg, uint16_t version) {
	const auto* loginLayout = ProtocolProfileRegistry::resolveAccountLoginLayout(version);
	if (!loginLayout) {
		disconnectClient(fmt::format("Unsupported client protocol version {}.", version));
		return nullptr;
	}

	protocolProfile = ProtocolProfileRegistry::getProfile(loginLayout->profileId);
	if (!protocolProfile || !ProtocolProfileRegistry::isProfileAllowed(protocolProfile->id)) {
		disconnectClient(fmt::format("Unsupported client protocol version {}.", version));
		return nullptr;
	}

	if (!loginLayout->hasAssetSignaturesBeforeRsa) {
		msg.skipBytes(loginLayout->bytesToSkipBeforeRsa);
		return loginLayout;
	}

	if (!msg.canRead(sizeof(uint32_t) * 3)) {
		disconnectClient(fmt::format("Invalid login packet for protocol version {}.", version));
		return nullptr;
	}

	const ClientAssetSignatures assetSignatures {
		.dat = msg.get<uint32_t>(),
		.spr = msg.get<uint32_t>(),
		.pic = msg.get<uint32_t>(),
	};

	protocolProfile = ProtocolProfileRegistry::resolveByClientVersionAndAssets(version, assetSignatures);
	if (!protocolProfile || !ProtocolProfileRegistry::isProfileAllowed(protocolProfile->id)) {
		disconnectClient(fmt::format("Unsupported client protocol version {}.", version));
		return nullptr;
	}

	loginLayout = ProtocolProfileRegistry::resolveAccountLoginLayout(protocolProfile->id);
	if (!loginLayout) {
		disconnectClient(fmt::format("Unsupported client protocol version {}.", version));
		return nullptr;
	}

	return loginLayout;
}

void ProtocolLogin::onRecvFirstMessage(NetworkMessage &msg) {
	if (g_game().getGameState() == GAME_STATE_SHUTDOWN) {
		disconnect();
		return;
	}

	msg.skipBytes(2); // client OS

	auto version = msg.get<uint16_t>();
	const auto* loginLayout = resolveLoginLayout(msg, version);
	if (!loginLayout) {
		return;
	}

	if (const auto connection = getConnection()) {
		connection->setTransportCodec(TransportCodecs::get(loginLayout->responseTransport), InitialTransportState::ResolvedFromPrelude);
	}

	oldProtocol = protocolProfile->hasFeature(ProtocolFeature::OldProtocolCompat);

	if (!Protocol::RSA_decrypt(msg)) {
		g_logger().warn("[ProtocolLogin::onRecvFirstMessage] - RSA Decrypt Failed");
		disconnect();
		return;
	}

	std::array<uint32_t, 4> key = { msg.get<uint32_t>(), msg.get<uint32_t>(), msg.get<uint32_t>(), msg.get<uint32_t>() };
	enableXTEAEncryption();
	setXTEAKey(key.data());

	setChecksumMethod(CHECKSUM_METHOD_ADLER32);

	if (g_game().getGameState() == GAME_STATE_STARTUP) {
		disconnectClient("Gameworld is starting up. Please wait.");
		return;
	}

	if (g_game().getGameState() == GAME_STATE_MAINTAIN) {
		disconnectClient("Gameworld is under maintenance.\nPlease re-connect in a while.");
		return;
	}

	BanInfo banInfo;
	auto curConnection = getConnection();
	if (!curConnection) {
		return;
	}

	if (IOBan::isIpBanned(curConnection->getIP(), banInfo)) {
		if (banInfo.reason.empty()) {
			banInfo.reason = "(none)";
		}

		std::ostringstream ss;
		ss << "Your IP has been banned until " << formatDateShort(banInfo.expiresAt) << " by " << banInfo.bannedBy << ".\n\nReason specified:\n"
		   << banInfo.reason;
		disconnectClient(ss.str());
		return;
	}

	std::string accountDescriptor = msg.getString();
	if (accountDescriptor.empty()) {
		std::ostringstream ss;
		ss << "Invalid " << (oldProtocol ? "username" : "email") << ".";
		disconnectClient(ss.str());
		return;
	}

	std::string password = msg.getString();
	if (accountDescriptor == "@livestream") {
		if (oldProtocol && !g_configManager().getBoolean(OLD_PROTOCOL)) {
			disconnectClient(ProtocolProfileRegistry::getUnsupportedClientProtocolMessage(false));
			return;
		}

		dispatchProtocolTask(
			[self = std::static_pointer_cast<ProtocolLogin>(shared_from_this()), password] {
				self->getLivestreamCharacterList(password);
			},
			"ProtocolLogin::getLivestreamCharacterList"
		);
		return;
	}

	if (password.empty()) {
		disconnectClient("Invalid password.");
		return;
	}

	dispatchProtocolTask(
		[self = std::static_pointer_cast<ProtocolLogin>(shared_from_this()), accountDescriptor, password] {
			self->getCharacterList(accountDescriptor, password);
		},
		__FUNCTION__
	);
}

void ProtocolLogin::getLivestreamCharacterList(const std::string &password) const {
	const auto casters = g_livestream().getBroadcastingCasters(password);
	if (casters.empty()) {
		disconnectClient("There are no players with the livestream on.");
		return;
	}

	auto output = OutputMessagePool::getOutputMessage();
	output->addByte(0x14);
	output->addString("Welcome to Livestream System!");

	login_protocol_wire::writeSessionKey(*output, fmt::format("@livestream\n{}", password));

	const auto serializedCount = std::min(casters.size(), login_protocol_wire::MAX_CHARACTER_COUNT);
	std::vector<login_protocol_wire::ModernCharacter> characters;
	characters.reserve(serializedCount);
	for (size_t index = 0; index < serializedCount; ++index) {
		characters.emplace_back(login_protocol_wire::ModernCharacter {
			.worldId = 0,
			.name = casters[index]->getName(),
		});
	}

	const std::array worlds {
		login_protocol_wire::ModernWorld {
			.id = 0,
			.name = g_configManager().getString(SERVER_NAME),
			.host = g_configManager().getString(IP),
			.port = static_cast<uint16_t>(g_configManager().getNumber(GAME_PORT)),
			.previewState = 0,
		},
	};
	login_protocol_wire::writeModernCharacterList(
		*output,
		worlds,
		characters,
		login_protocol_wire::makeModernAccountTail(false, 0)
	);

	send(output);
	disconnect();
}
