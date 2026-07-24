local tutorialStorage = Storage.Quest.U8_2.TheBeginningQuest

local hintConfig = {
	[50058] = {
		storageValue = 1,
		tutorialId = 2,
		markPosition = Position(32000, 32278, 7),
		markType = MAPMARK_REDEAST,
		markDescription = "To the Village",
	},
	[50059] = {
		storageValue = 2,
		text = "To look at objects such as this sign, right-click on them and select 'Look'. Sometimes you have to walk a bit closer to signs. Messages like this can be reviewed later in the Server Log window.",
		effectPosition = Position(32007, 32276, 7),
	},
	[50060] = {
		storageValue = 3,
		text = "Now continue to the next mark on your automap to the east. Point at a mark to read its name.",
		markPosition = Position(32023, 32273, 7),
		markType = MAPMARK_GREENNORTH,
		markDescription = "Santiago's Hut",
	},
	[50061] = {
		storageValue = 4,
		tutorialId = 21,
		text = "To go up stairs or ramps like this one, simply walk on them.",
		effectPosition = Position(32023, 32273, 7),
	},
	[50062] = {
		storageValue = 5,
		text = "This is Santiago, a Non-Player-Character. You can chat with NPCs by typing 'Hi' or 'Hello'. Walk to Santiago and try it!",
		markPosition = Position(32034, 32275, 6),
		markType = MAPMARK_REDSOUTH,
		markDescription = "Santiago's Hut",
	},
	[50063] = { storageValue = 6, tutorialId = 22 },
	[50064] = { storageValue = 7, tutorialId = 4 },
	[50065] = {
		storageValue = 8,
		text = "You can't see any cockroaches here. Open this chest and see if you can find something to light the room better.",
		effectPosition = Position(32033, 32278, 8),
	},
	[50067] = {
		storageValue = 10,
		text = "Look at the metallic object on the floor. Right-click the sewer grate and select 'Use' to climb down.",
		effectPosition = Position(32035, 32285, 8),
	},
	[50068] = {
		storageValue = 11,
		tutorialId = 7,
		text = "You smell stinky cockroaches around here. When you see one, walk to it and attack it from your battle list.",
	},
	[50069] = {
		storageValue = 12,
		tutorialId = 23,
		text = "Right-click the lower right end of the ladder and select 'Use' to climb up.",
		effectPosition = Position(32035, 32285, 9),
	},
	[50066] = {
		storageValue = 13,
		text = "Maybe you shouldn't stay in this forest longer than necessary. Zirella is waiting for her firewood!",
	},
	[50075] = {
		storageValue = 14,
		text = "Do you have trouble finding those dead trees? Use one to break a branch.",
		effectPosition = Position(32067, 32281, 7),
		secondEffectPosition = Position(32073, 32276, 7),
	},
	[50078] = {
		storageValue = 18,
		text = "This is a loose stone pile. Right-click your shovel, select 'Use with', and then left-click the stone pile to dig it open.",
		effectPosition = Position(32070, 32266, 7),
	},
	[50079] = {
		storageValue = 20,
		text = "Caves like this one are common in Tibia. To climb out again, you need something which you can find in this chest.",
		effectPosition = Position(32067, 32264, 8),
	},
}

local function sendTutorialEffect(position)
	position:sendMagicEffect(CONST_ME_TUTORIALARROW)
	position:sendMagicEffect(CONST_ME_TUTORIALSQUARE)
end

local function advanceHint(player, config)
	if player:getStorageValue(tutorialStorage.TutorialHintsStorage) >= config.storageValue then
		return false
	end

	player:setStorageValue(tutorialStorage.TutorialHintsStorage, config.storageValue)
	if config.tutorialId then
		player:sendTutorial(config.tutorialId)
	end
	if config.text then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, config.text)
	end
	if config.effectPosition then
		sendTutorialEffect(config.effectPosition)
	end
	if config.secondEffectPosition then
		sendTutorialEffect(config.secondEffectPosition)
	end
	if config.markPosition then
		player:addMapMark(config.markPosition, config.markType, config.markDescription)
	end
	return true
end

local tutorialHintTiles = MoveEvent()

function tutorialHintTiles.onStepIn(creature, item, position, fromPosition)
	local player = creature:getPlayer()
	if not player then
		return true
	end

	local actionId = item.actionid
	local currentHint = player:getStorageValue(tutorialStorage.TutorialHintsStorage)

	if actionId == 50076 then
		if currentHint == 15 then
			player:setStorageValue(tutorialStorage.TutorialHintsStorage, 16)
			sendTutorialEffect(Position(32062, 32271, 7))
			player:sendTutorial(24)
		end
		return true
	end

	if actionId == 50077 then
		if player:getStorageValue(tutorialStorage.ZirellaNpcGreetStorage) >= 8 and currentHint < 17 then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "This is Zirella's door. Right-click the lower part of the door and select 'Use' to open it.")
			player:setStorageValue(tutorialStorage.TutorialHintsStorage, 17)
		end
		return true
	end

	if actionId == 50081 then
		-- Current server item IDs: rope 3003. Advanced tutorial states remain passable
		-- even when the reward item is no longer carried by an existing character.
		if currentHint >= 20 and currentHint < 21 and (player:getItemCount(3003) > 0 or currentHint > 20) then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "To climb out of this cave, right-click your rope, select 'Use with', then left-click the rope spot.")
			sendTutorialEffect(Position(32070, 32266, 8))
			player:setStorageValue(tutorialStorage.TutorialHintsStorage, 21)
		end
		return true
	end

	local config = hintConfig[actionId]
	if not config then
		return true
	end

	if actionId == 50069 and player:getStorageValue(tutorialStorage.SantiagoNpcGreetStorage) < 6 and currentHint < 12 then
		return true
	end

	if actionId == 50078 and currentHint < 19 and player:getItemCount(3457) < 1 then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You have not claimed the shovel reward from Zirella's house.")
		player:teleportTo(fromPosition, true)
		return true
	end

	advanceHint(player, config)
	return true
end

tutorialHintTiles:type("stepin")
tutorialHintTiles:aid(50058, 50059, 50060, 50061, 50062, 50063, 50064, 50065, 50066, 50067, 50068, 50069, 50075, 50076, 50077, 50078, 50079, 50081)
tutorialHintTiles:register()

local stopConfig = {
	[50070] = {
		storage = tutorialStorage.SantiagoNpcGreetStorage,
		minimum = 12,
		maximum = 12,
		belowText = "You have no business in this part of the island anymore. Continue by solving Santiago's quest!",
		aboveText = "You have no business in this area of the island anymore. Talk to Santiago to learn how to continue.",
	},
	[50071] = {
		storage = tutorialStorage.SantiagoNpcGreetStorage,
		minimum = 12,
		belowText = "Santiago really needs help. Talk to him by typing 'Hi' or 'Hello'.",
	},
	[50072] = {
		storage = tutorialStorage.SantiagoNpcGreetStorage,
		minimum = 2,
		belowText = "This is Santiago's room. Maybe you should talk to him before looking around his house.",
	},
	[50074] = {
		storage = tutorialStorage.SantiagoNpcGreetStorage,
		minimum = 14,
		belowText = "You don't have any business there anymore. Continue to the east!",
	},
	[50080] = {
		storage = tutorialStorage.ZirellaNpcGreetStorage,
		minimum = 1,
		secondaryMinimum = 7,
		belowText = "Zirella really needs help. Go talk to her.",
		secondaryText = "This is not the way to the forest. You should head southwest first.",
	},
	[50088] = {
		storage = tutorialStorage.TutorialHintsStorage,
		minimum = 20,
		belowText = "Before you head to the village, dig open that hole with your shovel and climb down. You will find something useful there.",
	},
}

local pairedPass = {}
local tutorialStopTiles = MoveEvent()

local function denyPassage(player, fromPosition, text)
	player:teleportTo(fromPosition, true)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, text)
end

function tutorialStopTiles.onStepIn(creature, item, position, fromPosition)
	local player = creature:getPlayer()
	if not player then
		return true
	end

	local actionId = item.actionid
	local config = stopConfig[actionId]
	if not config then
		return true
	end

	local playerId = player:getId()
	if actionId == 50070 and player:getStorageValue(tutorialStorage.TutorialHintsStorage) == 5 then
		return true
	end
	if actionId == 50071 then
		pairedPass[playerId] = true
	elseif actionId == 50074 and pairedPass[playerId] then
		local playerPosition = player:getPosition()
		player:teleportTo(Position(playerPosition.x + 1, playerPosition.y, playerPosition.z), false)
		pairedPass[playerId] = nil
		return true
	end

	local value = player:getStorageValue(config.storage)
	if value < config.minimum then
		denyPassage(player, fromPosition, config.belowText)
		return true
	end
	if config.maximum and value > config.maximum then
		denyPassage(player, fromPosition, config.aboveText)
		return true
	end
	if config.secondaryMinimum and value < config.secondaryMinimum then
		denyPassage(player, fromPosition, config.secondaryText)
		return true
	end

	return true
end

tutorialStopTiles:type("stepin")
tutorialStopTiles:aid(50070, 50071, 50072, 50074, 50080, 50088)
tutorialStopTiles:register()
