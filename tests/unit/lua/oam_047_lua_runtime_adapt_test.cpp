#include "lua/scripts/lua_environment.hpp"
#include "lua/scripts/luascript.hpp"

#ifndef USE_PRECOMPILED_HEADERS
	#include <memory>
	#include <string>
#endif

namespace {
	bool registerEvent(LuaScriptInterface &interface, const std::string &eventName, int32_t &eventId) {
		auto* state = interface.getLuaState();
		if (!state) {
			return false;
		}

		const auto stackTop = lua_gettop(state);
		const std::string chunk = "function " + eventName + "() return true end";
		if (luaL_dostring(state, chunk.c_str()) != LUA_OK) {
			lua_settop(state, stackTop);
			return false;
		}

		eventId = interface.getEvent(eventName);
		lua_settop(state, stackTop);
		return eventId >= EVENT_ID_USER;
	}

	bool hasEvent(LuaScriptInterface &interface, int32_t eventId) {
		auto* state = interface.getLuaState();
		if (!state) {
			return false;
		}

		const auto stackTop = lua_gettop(state);
		const bool result = interface.pushFunction(eventId);
		lua_settop(state, stackTop);
		return result;
	}
}

TEST(Oam047LuaRuntimeAdaptTest, MainReinitRebindsActiveChildrenAndDropsOldRegistryEntries) {
	auto &environment = g_luaEnvironment();
	ASSERT_NE(environment.getLuaState(), nullptr);

	LuaScriptInterface first("OAM-047 first child");
	LuaScriptInterface second("OAM-047 second child");
	ASSERT_TRUE(first.initState());
	ASSERT_TRUE(second.initState());
	ASSERT_EQ(first.getLuaState(), environment.getLuaState());
	ASSERT_EQ(second.getLuaState(), environment.getLuaState());

	int32_t firstOldEvent = -1;
	int32_t secondOldEvent = -1;
	ASSERT_TRUE(registerEvent(first, "oam047FirstOld", firstOldEvent));
	ASSERT_TRUE(registerEvent(second, "oam047SecondOld", secondOldEvent));
	ASSERT_TRUE(hasEvent(first, firstOldEvent));
	ASSERT_TRUE(hasEvent(second, secondOldEvent));

	ASSERT_TRUE(environment.reInitState());
	ASSERT_EQ(first.getLuaState(), environment.getLuaState());
	ASSERT_EQ(second.getLuaState(), environment.getLuaState());
	EXPECT_FALSE(hasEvent(first, firstOldEvent));
	EXPECT_FALSE(hasEvent(second, secondOldEvent));

	int32_t firstNewEvent = -1;
	int32_t secondNewEvent = -1;
	ASSERT_TRUE(registerEvent(first, "oam047FirstNew", firstNewEvent));
	ASSERT_TRUE(registerEvent(second, "oam047SecondNew", secondNewEvent));
	EXPECT_TRUE(hasEvent(first, firstNewEvent));
	EXPECT_TRUE(hasEvent(second, secondNewEvent));
}

TEST(Oam047LuaRuntimeAdaptTest, UninitializedInterfaceIsNotAttachedByMainReinit) {
	auto &environment = g_luaEnvironment();
	ASSERT_NE(environment.getLuaState(), nullptr);

	LuaScriptInterface dormant("OAM-047 dormant child");
	ASSERT_EQ(dormant.getLuaState(), nullptr);
	ASSERT_TRUE(environment.reInitState());
	EXPECT_EQ(dormant.getLuaState(), nullptr);
}

TEST(Oam047LuaRuntimeAdaptTest, DestroyedInterfaceIsRemovedBeforeLaterMainReinit) {
	auto &environment = g_luaEnvironment();
	ASSERT_NE(environment.getLuaState(), nullptr);

	{
		auto ephemeral = std::make_unique<LuaScriptInterface>("OAM-047 ephemeral child");
		ASSERT_TRUE(ephemeral->initState());
		int32_t eventId = -1;
		ASSERT_TRUE(registerEvent(*ephemeral, "oam047Ephemeral", eventId));
		ASSERT_TRUE(hasEvent(*ephemeral, eventId));
	}

	ASSERT_TRUE(environment.reInitState());
	LuaScriptInterface survivor("OAM-047 survivor child");
	ASSERT_TRUE(survivor.initState());
	int32_t eventId = -1;
	ASSERT_TRUE(registerEvent(survivor, "oam047Survivor", eventId));
	EXPECT_TRUE(hasEvent(survivor, eventId));
}

TEST(Oam047LuaRuntimeAdaptTest, SharedTestInterfaceIsReboundWithTheOtherChildren) {
	auto &environment = g_luaEnvironment();
	auto* testInterface = environment.getTestInterface();
	ASSERT_NE(testInterface, nullptr);
	ASSERT_EQ(testInterface->getLuaState(), environment.getLuaState());

	int32_t oldEvent = -1;
	ASSERT_TRUE(registerEvent(*testInterface, "oam047TestOld", oldEvent));
	ASSERT_TRUE(hasEvent(*testInterface, oldEvent));

	ASSERT_TRUE(environment.reInitState());
	ASSERT_EQ(testInterface->getLuaState(), environment.getLuaState());
	EXPECT_FALSE(hasEvent(*testInterface, oldEvent));

	int32_t newEvent = -1;
	ASSERT_TRUE(registerEvent(*testInterface, "oam047TestNew", newEvent));
	EXPECT_TRUE(hasEvent(*testInterface, newEvent));
}
