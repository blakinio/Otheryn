#include <gtest/gtest.h>

#include "lua/scripts/luascript.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <memory>
	#include <string>
#endif

namespace {
	constexpr auto HARNESS = R"lua(
GROUP_TYPE_NORMAL = 1
GROUP_TYPE_TUTOR = 2
GROUP_TYPE_GAMEMASTER = 4
TALKTYPE_CHANNEL_Y = 1
TALKTYPE_CHANNEL_O = 2
TALKTYPE_CHANNEL_R1 = 3
CONDITION_CHANNELMUTEDTICKS = 1
CONDITIONID_DEFAULT = 1
CONDITION_PARAM_SUBID = 1
CONDITION_PARAM_TICKS = 2
PlayerFlag_TalkOrangeHelpChannel = 1
PlayerFlag_CanTalkRedChannel = 2
RETURNVALUE_PLAYERWITHTHISNAMEISNOTONLINE = "offline"

function Condition(...)
	return { setParameter = function(self, ...) end }
end

local targets = {}

function makePlayer(name, groupId, accountType)
	local player = {
		name = name,
		groupId = groupId,
		accountType = accountType,
		muted = false,
		cancelled = nil,
		kvstore = {}
	}

	function player:getGroup()
		local id = self.groupId
		return { getId = function() return id end }
	end

	function player:getAccountType()
		return self.accountType
	end

	function player:getLevel()
		return 100
	end

	function player:kv()
		local values = self.kvstore
		return {
			get = function(_, key) return values[key] end,
			set = function(_, key, value) values[key] = value end,
			remove = function(_, key) values[key] = nil end
		}
	end

	function player:getCondition(...)
		return self.muted
	end

	function player:addCondition(...)
		self.muted = true
	end

	function player:removeCondition(...)
		self.muted = false
	end

	function player:getName()
		return self.name
	end

	function player:sendCancelMessage(message)
		self.cancelled = message
	end

	function player:hasFlag(...)
		return false
	end

	return player
end

function registerTarget(player)
	targets[player.name] = player
end

function Player(name)
	return targets[name]
end

function sendChannelMessage(...)
end
)lua";

	std::unique_ptr<lua_State, decltype(&lua_close)> createState() {
		std::unique_ptr<lua_State, decltype(&lua_close)> state(luaL_newstate(), &lua_close);
		luaL_openlibs(state.get());
		return state;
	}

	void loadHarnessAndHelpScript(lua_State* state) {
		ASSERT_EQ(luaL_dostring(state, HARNESS), LUA_OK) << lua_tostring(state, -1);
		const std::string scriptPath = std::string(TESTS_SOURCE_DIR) + "/data/chatchannels/scripts/help.lua";
		ASSERT_EQ(luaL_dofile(state, scriptPath.c_str()), LUA_OK) << lua_tostring(state, -1);
	}

	bool getBooleanGlobal(lua_State* state, const char* name) {
		lua_getglobal(state, name);
		const bool value = lua_toboolean(state, -1) != 0;
		lua_pop(state, 1);
		return value;
	}
} // namespace

TEST(Oam025ChatCommunicationAdaptTest, MuteRejectsHigherGroupEvenWhenAccountTypeIsLower) {
	auto state = createState();
	ASSERT_NE(state, nullptr);
	loadHarnessAndHelpScript(state.get());

	constexpr auto SCENARIO = R"lua(
local actor = makePlayer("Actor", 3, 99)
local target = makePlayer("Target", 4, 0)
registerTarget(target)
onSpeak(actor, TALKTYPE_CHANNEL_Y, "!mute Target")
result_muted = target.muted
)lua";
	ASSERT_EQ(luaL_dostring(state.get(), SCENARIO), LUA_OK) << lua_tostring(state.get(), -1);
	EXPECT_FALSE(getBooleanGlobal(state.get(), "result_muted"));
}

TEST(Oam025ChatCommunicationAdaptTest, UnmuteAllowsLowerGroupRegardlessOfAccountType) {
	auto state = createState();
	ASSERT_NE(state, nullptr);
	loadHarnessAndHelpScript(state.get());

	constexpr auto SCENARIO = R"lua(
local actor = makePlayer("Actor", 3, 0)
local target = makePlayer("Target", 1, 99)
target.muted = true
target.kvstore["channel-help-exhaustion"] = os.time() + 180
registerTarget(target)
onSpeak(actor, TALKTYPE_CHANNEL_Y, "!unmute Target")
result_muted = target.muted
)lua";
	ASSERT_EQ(luaL_dostring(state.get(), SCENARIO), LUA_OK) << lua_tostring(state.get(), -1);
	EXPECT_FALSE(getBooleanGlobal(state.get(), "result_muted"));
}
