#include <gtest/gtest.h>

#include <fstream>
#include <sstream>
#include <string>

namespace {
	std::string readSource(const std::string &relativePath) {
		std::ifstream input(std::string(OAM042_SOURCE_DIR) + "/" + relativePath);
		EXPECT_TRUE(input.is_open()) << relativePath;
		std::ostringstream buffer;
		buffer << input.rdbuf();
		return buffer.str();
	}

	void expectContains(const std::string &source, const std::string &needle) {
		EXPECT_NE(source.find(needle), std::string::npos) << needle;
	}
} // namespace

TEST(Oam042NpcsReuseTest, PreservesLoaderRegistrationCallbacksAndShopContract) {
	const auto source = readSource("src/creatures/npcs/npcs.cpp");
	ASSERT_FALSE(source.empty());

	expectContains(source, "coreFolder + \"/npclib/load.lua\"");
	expectContains(source, "datapackFolder + \"/npc\"");
	expectContains(source, "g_scripts().loadScripts(datapackFolder + \"/npc\", false, reloading)");
	expectContains(source, "const std::string key = asLowerCaseString(name)");
	expectContains(source, "npcs[key] = std::make_shared<NpcType>(name)");

	expectContains(source, "case NPCS_EVENT_THINK:");
	expectContains(source, "case NPCS_EVENT_APPEAR:");
	expectContains(source, "case NPCS_EVENT_DISAPPEAR:");
	expectContains(source, "case NPCS_EVENT_MOVE:");
	expectContains(source, "case NPCS_EVENT_SAY:");
	expectContains(source, "case NPCS_EVENT_PLAYER_BUY:");
	expectContains(source, "case NPCS_EVENT_PLAYER_SELL:");
	expectContains(source, "case NPCS_EVENT_PLAYER_CHECK_ITEM:");
	expectContains(source, "case NPCS_EVENT_PLAYER_CLOSE_CHANNEL:");

	expectContains(source, "if (shopBlock.itemSellPrice > iType.sellPrice)");
	expectContains(source, "if (shopBlock.itemBuyPrice > iType.buyPrice)");
	expectContains(source, "std::ranges::any_of(npcType->info.shopItemVector");
	expectContains(source, "npcType->info.shopItemVector.emplace_back(shopBlock)");
}

TEST(Oam042NpcsReuseTest, PreservesLuaNpcRuntimeSurface) {
	const auto source = readSource("src/lua/functions/creatures/npc/npc_functions.cpp");
	ASSERT_FALSE(source.empty());

	expectContains(source, "Lua::registerSharedClass(L, \"Npc\", \"Creature\", NpcFunctions::luaNpcCreate)");
	expectContains(source, "Lua::registerMethod(L, \"Npc\", \"setPlayerInteraction\"");
	expectContains(source, "Lua::registerMethod(L, \"Npc\", \"removePlayerInteraction\"");
	expectContains(source, "Lua::registerMethod(L, \"Npc\", \"openShopWindow\"");
	expectContains(source, "Lua::registerMethod(L, \"Npc\", \"closeShopWindow\"");
	expectContains(source, "Lua::registerMethod(L, \"Npc\", \"sellItem\"");
	expectContains(source, "ShopFunctions::init(L)");
	expectContains(source, "NpcTypeFunctions::init(L)");
}

TEST(Oam042NpcsReuseTest, PreservesCoreDialogueAndTravelContract) {
	const auto load = readSource("data/npclib/load.lua");
	ASSERT_FALSE(load.empty());
	expectContains(load, "npclib/npc.lua");
	expectContains(load, "modules/scripts/npc/npc_dialog.lua");
	expectContains(load, "npclib/npc_system/npc_handler.lua");
	expectContains(load, "npclib/npc_system/keyword_handler.lua");
	expectContains(load, "npclib/npc_system/modules.lua");
	expectContains(load, "npclib/npc_system/custom_modules.lua");
	expectContains(load, "npclib/npc_system/bank_system.lua");

	const auto modules = readSource("data/npclib/npc_system/modules.lua");
	ASSERT_FALSE(modules.empty());
	expectContains(modules, "function StdModule.travel(npc, player, message, keywords, parameters, node)");
	expectContains(modules, "if not npcHandler:checkInteraction(npc, player) then");
	expectContains(modules, "if parameters.premium and not player:isPremium() then");
	expectContains(modules, "elseif parameters.level and player:getLevel() < parameters.level then");
	expectContains(modules, "elseif player:isPzLocked() then");
	expectContains(modules, "elseif not player:removeMoneyBank(cost) then");
	expectContains(modules, "player:kv():set(\"npc-exhaustion\", os.time() + 3)");
	expectContains(modules, "player:teleportTo(destination)");
	expectContains(modules, "npcHandler:resetNpc(npc, player)");
}

TEST(Oam042NpcsReuseTest, PreservesHarlowTravelAndStorageGate) {
	const auto source = readSource("data-otservbr-global/npc/harlow.lua");
	ASSERT_FALSE(source.empty());

	expectContains(source, "local internalNpcName = \"Harlow\"");
	expectContains(source, "Game.createNpcType(internalNpcName)");
	expectContains(source, "Storage.Quest.U8_4.BloodBrothers.VengothAccess) == 1");
	expectContains(source, "cost = 100, destination = Position(32858, 31549, 7)");
	expectContains(source, "npcHandler:setCallback(CALLBACK_MESSAGE_DEFAULT, creatureSayCallback)");
	expectContains(source, "npcHandler:addModule(FocusModule:new(), npcConfig.name, true, true, true)");
	expectContains(source, "npcType:register(npcConfig)");
}

TEST(Oam042NpcsReuseTest, PreservesRashidQuestAndShopGate) {
	const auto source = readSource("data-otservbr-global/npc/rashid.lua");
	ASSERT_FALSE(source.empty());

	expectContains(source, "local internalNpcName = \"Rashid\"");
	expectContains(source, "Storage.Quest.U8_1.TheTravellingTrader.Mission01");
	expectContains(source, "Storage.Quest.U8_1.TheTravellingTrader.Mission07");
	expectContains(source, "player:addAchievement(\"Recognised Trader\")");
	expectContains(source, "local function onTradeRequest(npc, creature)");
	expectContains(source, "you do not belong to my exclusive customers");
	expectContains(source, "npcHandler:setCallback(CALLBACK_ON_TRADE_REQUEST, onTradeRequest)");
	expectContains(source, "npcConfig.shop = {");
	expectContains(source, "{ itemName = \"abyss hammer\", clientId = 7414, sell = 20000 }");
	expectContains(source, "npcType:register(npcConfig)");
}
