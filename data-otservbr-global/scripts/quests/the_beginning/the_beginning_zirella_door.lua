local tutorialStorage = Storage.Quest.U8_2.TheBeginningQuest

local ZIRELLA_DOOR_UID = 50085
local ZIRELLA_REWARD_STAGE = 8
local CLOSED_DOOR_ITEM_ID = 6898
local OPEN_DOOR_ITEM_ID = 6899
local zirellaDoorPosition = Position(32058, 32266, 7)

-- UID 50085 is the map-authoritative quest gate; generic quest-door AIDs do not encode Zirella's stage.
local function isSamePosition(first, second)
	return first.x == second.x and first.y == second.y and first.z == second.z
end

local zirellaDoor = Action()

function zirellaDoor.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	if item.uid ~= ZIRELLA_DOOR_UID or not isSamePosition(fromPosition, zirellaDoorPosition) then
		return false
	end

	if item.itemid == CLOSED_DOOR_ITEM_ID then
		if player:getStorageValue(tutorialStorage.ZirellaNpcGreetStorage) < ZIRELLA_REWARD_STAGE then
			player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The door seems to be sealed against unwanted intruders.")
			return true
		end

		item:transform(OPEN_DOOR_ITEM_ID)
		item:getPosition():sendSingleSoundEffect(SOUND_EFFECT_TYPE_ACTION_OPEN_DOOR)
		player:teleportTo(toPosition, true)
		return true
	end

	if item.itemid == OPEN_DOOR_ITEM_ID then
		if Creature.checkCreatureInsideDoor(player, toPosition) then
			return true
		end

		item:transform(CLOSED_DOOR_ITEM_ID)
		item:getPosition():sendSingleSoundEffect(SOUND_EFFECT_TYPE_ACTION_CLOSE_DOOR)
		return true
	end

	return true
end

zirellaDoor:uid(ZIRELLA_DOOR_UID)
zirellaDoor:register()
