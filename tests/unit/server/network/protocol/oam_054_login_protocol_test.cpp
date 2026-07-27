#include "server/network/message/outputmessage.hpp"
#include "server/network/protocol/login_protocol_wire.hpp"

#include <gtest/gtest.h>

#ifndef USE_PRECOMPILED_HEADERS
	#include <cstring>
	#include <stdexcept>
	#include <string>
	#include <vector>
#endif

namespace {
	class WireReader {
	public:
		explicit WireReader(OutputMessage &message) :
			data(message.getOutputBuffer()), size(message.getLength()) { }

		template <typename T>
		T read() {
			if (position + sizeof(T) > size) {
				throw std::out_of_range("login wire read exceeds message length");
			}

			T value {};
			std::memcpy(&value, data + position, sizeof(T));
			position += sizeof(T);
			return value;
		}

		std::string readString() {
			const auto length = read<uint16_t>();
			if (position + length > size) {
				throw std::out_of_range("login wire string exceeds message length");
			}

			std::string value(reinterpret_cast<const char*>(data + position), length);
			position += length;
			return value;
		}

		[[nodiscard]] bool complete() const {
			return position == size;
		}

	private:
		const uint8_t* data;
		size_t size;
		size_t position = 0;
	};
}

TEST(Oam054LoginProtocolTest, SessionKeyMatchesMaintainedClientOpcodeAndString) {
	OutputMessage output;
	login_protocol_wire::writeSessionKey(output, "opaque-session-token");

	WireReader reader(output);
	EXPECT_EQ(login_protocol_wire::SESSION_KEY_OPCODE, reader.read<uint8_t>());
	EXPECT_EQ("opaque-session-token", reader.readString());
	EXPECT_TRUE(reader.complete());
}

TEST(Oam054LoginProtocolTest, ModernCharacterListMatchesMaintainedClientFieldOrder) {
	OutputMessage output;
	const std::vector worlds {
		login_protocol_wire::ModernWorld {
			.id = 7,
			.name = "Otheryn",
			.host = "127.0.0.1",
			.port = 7172,
			.previewState = 1,
		},
	};
	const std::vector characters {
		login_protocol_wire::ModernCharacter { .worldId = 7, .name = "Alice" },
		login_protocol_wire::ModernCharacter { .worldId = 7, .name = "Bob" },
	};
	constexpr uint32_t premiumExpiry = 2'000'000'000;
	login_protocol_wire::writeModernCharacterList(
		output,
		worlds,
		characters,
		login_protocol_wire::makeModernAccountTail(true, premiumExpiry)
	);

	WireReader reader(output);
	EXPECT_EQ(login_protocol_wire::CHARACTER_LIST_OPCODE, reader.read<uint8_t>());
	EXPECT_EQ(1, reader.read<uint8_t>());
	EXPECT_EQ(7, reader.read<uint8_t>());
	EXPECT_EQ("Otheryn", reader.readString());
	EXPECT_EQ("127.0.0.1", reader.readString());
	EXPECT_EQ(7172, reader.read<uint16_t>());
	EXPECT_EQ(1, reader.read<uint8_t>());

	EXPECT_EQ(2, reader.read<uint8_t>());
	EXPECT_EQ(7, reader.read<uint8_t>());
	EXPECT_EQ("Alice", reader.readString());
	EXPECT_EQ(7, reader.read<uint8_t>());
	EXPECT_EQ("Bob", reader.readString());

	EXPECT_EQ(static_cast<uint8_t>(login_protocol_wire::AccountStatus::Ok), reader.read<uint8_t>());
	EXPECT_EQ(static_cast<uint8_t>(login_protocol_wire::SubscriptionStatus::Premium), reader.read<uint8_t>());
	EXPECT_EQ(premiumExpiry, reader.read<uint32_t>());
	EXPECT_TRUE(reader.complete());
}

TEST(Oam054LoginProtocolTest, ModernFreeAccountTailIsExplicitAndComplete) {
	OutputMessage output;
	const std::vector<login_protocol_wire::ModernWorld> worlds;
	const std::vector<login_protocol_wire::ModernCharacter> characters;
	login_protocol_wire::writeModernCharacterList(
		output,
		worlds,
		characters,
		login_protocol_wire::makeModernAccountTail(false, 0)
	);

	WireReader reader(output);
	EXPECT_EQ(login_protocol_wire::CHARACTER_LIST_OPCODE, reader.read<uint8_t>());
	EXPECT_EQ(0, reader.read<uint8_t>());
	EXPECT_EQ(0, reader.read<uint8_t>());
	EXPECT_EQ(static_cast<uint8_t>(login_protocol_wire::AccountStatus::Ok), reader.read<uint8_t>());
	EXPECT_EQ(static_cast<uint8_t>(login_protocol_wire::SubscriptionStatus::Free), reader.read<uint8_t>());
	EXPECT_EQ(0U, reader.read<uint32_t>());
	EXPECT_TRUE(reader.complete());
}

TEST(Oam054LoginProtocolTest, LegacyCharacterListMatchesMaintainedClientFieldOrder) {
	OutputMessage output;
	const std::vector characters {
		login_protocol_wire::LegacyCharacter {
			.name = "Legacy Knight",
			.worldName = "Otheryn 8.60",
			.worldIp = 0x0100007F,
			.worldPort = 7173,
		},
	};
	login_protocol_wire::writeLegacyCharacterList(output, characters, 42);

	WireReader reader(output);
	EXPECT_EQ(login_protocol_wire::CHARACTER_LIST_OPCODE, reader.read<uint8_t>());
	EXPECT_EQ(1, reader.read<uint8_t>());
	EXPECT_EQ("Legacy Knight", reader.readString());
	EXPECT_EQ("Otheryn 8.60", reader.readString());
	EXPECT_EQ(0x0100007FU, reader.read<uint32_t>());
	EXPECT_EQ(7173, reader.read<uint16_t>());
	EXPECT_EQ(42, reader.read<uint16_t>());
	EXPECT_TRUE(reader.complete());
}

TEST(Oam054LoginProtocolTest, ModernCharacterCountCapsPayloadAtU8Boundary) {
	OutputMessage output;
	const std::vector worlds {
		login_protocol_wire::ModernWorld { .id = 0, .name = "World", .host = "127.0.0.1", .port = 7172, .previewState = 0 },
	};
	std::vector<login_protocol_wire::ModernCharacter> characters;
	for (size_t index = 0; index < 260; ++index) {
		characters.emplace_back(login_protocol_wire::ModernCharacter { .worldId = 0, .name = "C" + std::to_string(index) });
	}
	login_protocol_wire::writeModernCharacterList(output, worlds, characters, login_protocol_wire::makeModernAccountTail(false, 0));

	WireReader reader(output);
	EXPECT_EQ(login_protocol_wire::CHARACTER_LIST_OPCODE, reader.read<uint8_t>());
	EXPECT_EQ(1, reader.read<uint8_t>());
	EXPECT_EQ(0, reader.read<uint8_t>());
	EXPECT_EQ("World", reader.readString());
	EXPECT_EQ("127.0.0.1", reader.readString());
	EXPECT_EQ(7172, reader.read<uint16_t>());
	EXPECT_EQ(0, reader.read<uint8_t>());

	EXPECT_EQ(255, reader.read<uint8_t>());
	for (size_t index = 0; index < 255; ++index) {
		EXPECT_EQ(0, reader.read<uint8_t>());
		EXPECT_EQ("C" + std::to_string(index), reader.readString());
	}
	EXPECT_EQ(static_cast<uint8_t>(login_protocol_wire::AccountStatus::Ok), reader.read<uint8_t>());
	EXPECT_EQ(static_cast<uint8_t>(login_protocol_wire::SubscriptionStatus::Free), reader.read<uint8_t>());
	EXPECT_EQ(0U, reader.read<uint32_t>());
	EXPECT_TRUE(reader.complete());
}

TEST(Oam054LoginProtocolTest, LegacyCharacterCountCapsPayloadAtU8Boundary) {
	OutputMessage output;
	std::vector<login_protocol_wire::LegacyCharacter> characters;
	for (size_t index = 0; index < 260; ++index) {
		characters.emplace_back(login_protocol_wire::LegacyCharacter {
			.name = "L" + std::to_string(index),
			.worldName = "Legacy",
			.worldIp = 0x0100007F,
			.worldPort = 7173,
		});
	}
	login_protocol_wire::writeLegacyCharacterList(output, characters, 7);

	WireReader reader(output);
	EXPECT_EQ(login_protocol_wire::CHARACTER_LIST_OPCODE, reader.read<uint8_t>());
	EXPECT_EQ(255, reader.read<uint8_t>());
	for (size_t index = 0; index < 255; ++index) {
		EXPECT_EQ("L" + std::to_string(index), reader.readString());
		EXPECT_EQ("Legacy", reader.readString());
		EXPECT_EQ(0x0100007FU, reader.read<uint32_t>());
		EXPECT_EQ(7173, reader.read<uint16_t>());
	}
	EXPECT_EQ(7, reader.read<uint16_t>());
	EXPECT_TRUE(reader.complete());
}
