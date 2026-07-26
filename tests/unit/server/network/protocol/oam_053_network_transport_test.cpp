#include "server/network/connection/connection.hpp"
#include "server/network/message/networkmessage.hpp"
#include "server/network/message/outputmessage.hpp"
#include "server/network/protocol/protocol.hpp"
#include "server/network/protocol/transport_codec.hpp"

#include <gtest/gtest.h>

namespace {
	class OamTransportProtocol final : public Protocol {
	public:
		explicit OamTransportProtocol(const Connection_ptr &connection) :
			Protocol(connection) { }

		void onRecvFirstMessage(NetworkMessage &) override { }
		void parsePacket(NetworkMessage &) override { }

		void enableEncryptionForTest() {
			enableXTEAEncryption();
		}
	};

	[[nodiscard]] uint16_t readU16(const uint8_t* buffer) {
		return static_cast<uint16_t>(buffer[0]) | static_cast<uint16_t>(buffer[1] << 8);
	}

	NetworkMessage makeSequenceFrame(uint32_t sequence, uint8_t opcode = 0x14) {
		NetworkMessage message;
		message.add<uint32_t>(sequence);
		message.addByte(opcode);
		message.setBufferPosition(NetworkMessage::INITIAL_BUFFER_POSITION);
		return message;
	}

	NetworkMessage makeEncryptedZeroBlockFrame(uint32_t sequence) {
		NetworkMessage message;
		message.add<uint32_t>(sequence);
		for (size_t index = 0; index < XTEA_MULTIPLE; ++index) {
			message.addByte(0);
		}
		message.setLength(HEADER_LENGTH + CHECKSUM_LENGTH + XTEA_MULTIPLE);
		message.setBufferPosition(NetworkMessage::INITIAL_BUFFER_POSITION);
		return message;
	}

	void closeConnection(const Connection_ptr &connection) {
		// These focused tests never accept a Protocol into Connection, so forced close
		// releases the manager entry and socket synchronously without queuing release().
		connection->close(true);
	}
}

TEST(Oam053NetworkTransportTest, CurrentProfilesOwnDistinctChecksumContracts) {
	const auto &login = TransportCodecs::currentLogin().getProfile();
	const auto &sequence = TransportCodecs::currentGameSequence().getProfile();
	const auto &plain = TransportCodecs::currentGamePlain().getProfile();

	EXPECT_EQ(CHECKSUM_METHOD_ADLER32, login.inboundChecksum);
	EXPECT_EQ(CHECKSUM_METHOD_ADLER32, login.outboundChecksum);
	EXPECT_EQ(CompressionLayout::None, login.compression);

	EXPECT_EQ(CHECKSUM_METHOD_SEQUENCE, sequence.inboundChecksum);
	EXPECT_EQ(CHECKSUM_METHOD_SEQUENCE, sequence.outboundChecksum);
	EXPECT_EQ(CompressionLayout::Official, sequence.compression);
	EXPECT_TRUE(sequence.sequenceHighBitSignalsCompression);

	EXPECT_EQ(CHECKSUM_METHOD_NONE, plain.inboundChecksum);
	EXPECT_EQ(CHECKSUM_METHOD_NONE, plain.outboundChecksum);
	EXPECT_EQ(CompressionLayout::None, plain.compression);
	EXPECT_EQ(0, plain.modernLengthExtraBytes);
	EXPECT_FALSE(plain.lengthIncludesChecksum);
}

TEST(Oam053NetworkTransportTest, CurrentFirstFrameConsumesCapturedPhysicalBody) {
	constexpr uint16_t capturedOuterBlockCount = 0x0015;
	constexpr uint16_t capturedPhysicalBodySize = 172;
	constexpr uint16_t checksumFreeBodySize = 168;

	const auto initialBehavior = ProtocolProfileRegistry::defaultModernInitialBehavior();
	EXPECT_EQ(TransportProfileId::CurrentGameSequence, initialBehavior.transport);

	const auto sequencedSize = TransportCodecs::get(initialBehavior.transport).decodeBodySize(capturedOuterBlockCount);
	const auto plainSize = TransportCodecs::currentGamePlain().decodeBodySize(capturedOuterBlockCount);
	ASSERT_TRUE(sequencedSize.has_value());
	ASSERT_TRUE(plainSize.has_value());
	EXPECT_EQ(capturedPhysicalBodySize, *sequencedSize);
	EXPECT_EQ(checksumFreeBodySize, *plainSize);
}

TEST(Oam053NetworkTransportTest, ChecksumFreeBlockCountRoundTripsEncodedBodySize) {
	asio::io_service ioService;
	auto connection = ConnectionManager::getInstance().createConnection(ioService, nullptr);
	auto protocol = std::make_shared<OamTransportProtocol>(connection);
	protocol->enableEncryptionForTest();

	OutputMessage message;
	message.addByte(0x42);
	TransportCodecs::currentGamePlain().encodeOutbound(*protocol, message);

	const auto lengthHeader = readU16(message.getOutputBuffer());
	const auto decodedBodySize = TransportCodecs::currentGamePlain().decodeBodySize(lengthHeader);
	ASSERT_TRUE(decodedBodySize.has_value());
	EXPECT_EQ(1, lengthHeader);
	EXPECT_EQ(message.getLength() - HEADER_LENGTH, *decodedBodySize);

	closeConnection(connection);
}

TEST(Oam053NetworkTransportTest, TruncatedChecksumIsMalformedAndDoesNotConsumeSequence) {
	asio::io_service ioService;
	auto connection = ConnectionManager::getInstance().createConnection(ioService, nullptr);
	auto protocol = std::make_shared<OamTransportProtocol>(connection);
	const auto &codec = TransportCodecs::currentGameSequence();

	NetworkMessage truncated;
	truncated.addByte(0x01);
	truncated.setBufferPosition(NetworkMessage::INITIAL_BUFFER_POSITION);
	EXPECT_EQ(InboundTransportStatus::MalformedFrame, codec.prepareInbound(*protocol, truncated).status);

	auto accepted = makeSequenceFrame(1);
	EXPECT_EQ(InboundTransportStatus::Accepted, codec.prepareInbound(*protocol, accepted).status);

	closeConnection(connection);
}

TEST(Oam053NetworkTransportTest, ZeroGapAndReplayDoNotConsumeAcceptedSequence) {
	asio::io_service ioService;
	auto connection = ConnectionManager::getInstance().createConnection(ioService, nullptr);
	auto protocol = std::make_shared<OamTransportProtocol>(connection);
	const auto &codec = TransportCodecs::currentGameSequence();

	auto zero = makeSequenceFrame(0);
	const auto zeroResult = codec.prepareInbound(*protocol, zero);
	EXPECT_EQ(InboundTransportStatus::ZeroSequence, zeroResult.status);
	EXPECT_EQ(1, zeroResult.expectedSequence.value_or(0));

	auto gap = makeSequenceFrame(2);
	const auto gapResult = codec.prepareInbound(*protocol, gap);
	EXPECT_EQ(InboundTransportStatus::SequenceMismatch, gapResult.status);
	EXPECT_EQ(1, gapResult.expectedSequence.value_or(0));

	auto first = makeSequenceFrame(1);
	EXPECT_EQ(InboundTransportStatus::Accepted, codec.prepareInbound(*protocol, first).status);

	auto replay = makeSequenceFrame(1);
	const auto replayResult = codec.prepareInbound(*protocol, replay);
	EXPECT_EQ(InboundTransportStatus::SequenceMismatch, replayResult.status);
	EXPECT_EQ(2, replayResult.expectedSequence.value_or(0));

	auto second = makeSequenceFrame(2);
	EXPECT_EQ(InboundTransportStatus::Accepted, codec.prepareInbound(*protocol, second).status);

	closeConnection(connection);
}

TEST(Oam053NetworkTransportTest, DecryptFailureDoesNotConsumeExpectedSequence) {
	asio::io_service ioService;
	auto connection = ConnectionManager::getInstance().createConnection(ioService, nullptr);
	auto protocol = std::make_shared<OamTransportProtocol>(connection);
	protocol->enableEncryptionForTest();
	const auto &codec = TransportCodecs::currentGameSequence();

	auto rejected = makeEncryptedZeroBlockFrame(1);
	const auto rejectedResult = codec.prepareInbound(*protocol, rejected);
	EXPECT_EQ(InboundTransportStatus::DecryptFailure, rejectedResult.status);
	EXPECT_EQ(1, rejectedResult.expectedSequence.value_or(0));

	auto retry = makeEncryptedZeroBlockFrame(1);
	const auto retryResult = codec.prepareInbound(*protocol, retry);
	EXPECT_EQ(InboundTransportStatus::DecryptFailure, retryResult.status);
	EXPECT_EQ(1, retryResult.expectedSequence.value_or(0));

	closeConnection(connection);
}
