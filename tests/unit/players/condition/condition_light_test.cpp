/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#include "creatures/combat/condition.hpp"
#include "creatures/players/player.hpp"
#include "io/fileloader.hpp"
#include "items/tile.hpp"
#include "utils/tools.hpp"

#include <optional>

namespace {
	struct SerializedLightState {
		uint32_t level = 0;
		uint32_t interval = 0;
	};

	template <typename T>
	bool readAttribute(PropStream &stream, ConditionAttr_t expected, T &value) {
		uint8_t attribute = 0;
		return stream.read<uint8_t>(attribute)
			&& attribute == static_cast<uint8_t>(expected)
			&& stream.read<T>(value);
	}

	std::optional<SerializedLightState> serializeLightState(ConditionLight &condition) {
		PropWriteStream output;
		condition.serialize(output);

		size_t size = 0;
		const char* data = output.getStream(size);
		PropStream input;
		input.init(data, size);

		int8_t type = 0;
		uint32_t id = 0;
		uint32_t ticks = 0;
		uint8_t isBuff = 0;
		uint32_t subId = 0;
		uint16_t tickSound = 0;
		uint16_t addSound = 0;
		bool persistent = false;
		uint32_t color = 0;
		SerializedLightState state;
		uint32_t internalTicks = 0;

		if (!readAttribute(input, CONDITIONATTR_TYPE, type)
		    || !readAttribute(input, CONDITIONATTR_ID, id)
		    || !readAttribute(input, CONDITIONATTR_TICKS, ticks)
		    || !readAttribute(input, CONDITIONATTR_ISBUFF, isBuff)
		    || !readAttribute(input, CONDITIONATTR_SUBID, subId)
		    || !readAttribute(input, CONDITIONATTR_TICKSOUND, tickSound)
		    || !readAttribute(input, CONDITIONATTR_ADDSOUND, addSound)
		    || !readAttribute(input, CONDITIONATTR_PERSISTENT, persistent)
		    || !readAttribute(input, CONDITIONATTR_LIGHTCOLOR, color)
		    || !readAttribute(input, CONDITIONATTR_LIGHTLEVEL, state.level)
		    || !readAttribute(input, CONDITIONATTR_LIGHTTICKS, internalTicks)
		    || !readAttribute(input, CONDITIONATTR_LIGHTINTERVAL, state.interval)
		    || input.size() != 0) {
			return std::nullopt;
		}

		return state;
	}

	std::shared_ptr<Player> createPlayerAt(const std::shared_ptr<Tile> &tile) {
		auto player = std::make_shared<Player>();
		player->setParent(tile);
		return player;
	}
}

TEST(ConditionLightTest, NormalizesZeroLevelDuringDeserialization) {
	ConditionLight condition(CONDITIONID_DEFAULT, CONDITION_LIGHT, 5000, false, 0, 7, 215);

	PropWriteStream output;
	output.write<uint32_t>(0);

	size_t size = 0;
	const char* data = output.getStream(size);
	PropStream input;
	input.init(data, size);

	ASSERT_TRUE(condition.unserializeProp(CONDITIONATTR_LIGHTLEVEL, input));
	ASSERT_EQ(0u, input.size());

	const auto state = serializeLightState(condition);
	ASSERT_TRUE(state.has_value());
	EXPECT_EQ(1u, state->level);
}

TEST(ConditionLightTest, StartsZeroLevelAtMinimumValidLevelAndInterval) {
	UPDATE_OTSYS_TIME();
	const auto tile = std::make_shared<DynamicTile>(Position(100, 100, 7));
	const auto player = createPlayerAt(tile);
	ConditionLight condition(CONDITIONID_DEFAULT, CONDITION_LIGHT, 5000, false, 0, 0, 215);

	ASSERT_TRUE(condition.startCondition(player));

	const auto state = serializeLightState(condition);
	ASSERT_TRUE(state.has_value());
	EXPECT_EQ(1u, state->level);
	EXPECT_EQ(5000u, state->interval);
	EXPECT_EQ(1u, player->getCreatureLight().level);
}

TEST(ConditionLightTest, PreservesValidLevelAndInterval) {
	UPDATE_OTSYS_TIME();
	const auto tile = std::make_shared<DynamicTile>(Position(100, 100, 7));
	const auto player = createPlayerAt(tile);
	ConditionLight condition(CONDITIONID_DEFAULT, CONDITION_LIGHT, 5000, false, 0, 5, 215);

	ASSERT_TRUE(condition.startCondition(player));

	const auto state = serializeLightState(condition);
	ASSERT_TRUE(state.has_value());
	EXPECT_EQ(5u, state->level);
	EXPECT_EQ(1000u, state->interval);
	EXPECT_EQ(5u, player->getCreatureLight().level);
}
