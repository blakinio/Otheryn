FORGE_NORMAL_MONSTER = 0
FORGE_INFLUENCED_MONSTER = 1
FORGE_FIENDISH_MONSTER = 2
MESSAGE_EVENT_ADVANCE = 19

local function fail(message)
	io.stderr:write(message .. "\n")
	os.exit(1)
end

local function expectEqual(expected, actual, label)
	if expected ~= actual then
		fail(label .. ": expected " .. tostring(expected) .. ", got " .. tostring(actual))
	end
end

local function expectContains(text, needle, label)
	if not string.find(text, needle, 1, true) then
		fail(label .. ": expected '" .. text .. "' to contain '" .. needle .. "'")
	end
end

local function newPlayer(premium, dust, limit)
	local messages = {}
	local player = {}

	function player:isPremium()
		return premium
	end

	function player:getForgeDusts()
		return dust
	end

	function player:getForgeDustLevel()
		return limit
	end

	function player:addForgeDusts(amount)
		dust = dust + amount
	end

	function player:sendTextMessage(messageType, text)
		table.insert(messages, { messageType = messageType, text = text })
	end

	function player:state()
		return dust, messages
	end

	return player
end

dofile("data/libs/systems/exaltation_forge.lua")

local freePlayer = newPlayer(false, 10, 100)
expectEqual(0, ForgeMonster:creditDust(freePlayer, 5), "non-Premium credit")
local freeDust, freeMessages = freePlayer:state()
expectEqual(10, freeDust, "non-Premium Dust remains unchanged")
expectEqual(1, #freeMessages, "non-Premium message count")
expectContains(freeMessages[1].text, "Premium Account", "non-Premium message")

local premiumPlayer = newPlayer(true, 10, 100)
expectEqual(5, ForgeMonster:creditDust(premiumPlayer, 5), "Premium credit")
local premiumDust, premiumMessages = premiumPlayer:state()
expectEqual(15, premiumDust, "Premium Dust credit")
expectEqual(1, #premiumMessages, "Premium message count")

local cappedPlayer = newPlayer(true, 98, 100)
expectEqual(2, ForgeMonster:creditDust(cappedPlayer, 5), "cap-aware credit")
local cappedDust = cappedPlayer:state()
expectEqual(100, cappedDust, "cap-aware Dust total")

print("Exaltation Forge Premium Dust tests passed")
