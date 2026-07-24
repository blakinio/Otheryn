local tutorialStorage = Storage.Quest.U8_2.TheBeginningQuest

local DEAD_TREE_ITEM_ID = 7753
local BRANCH_ITEM_ID = 7772
local ZIRELLA_CART_ITEM_ID = 7751
local ZIRELLA_ACTIVE_STAGE = 6
local ZIRELLA_DELIVERED_STAGE = 7
local BRANCH_HINT_STAGE = 15
local TREE_EXHAUST_SECONDS = 5

local zirellaCartPosition = Position(32062, 32271, 7)
local tutorialDeadTreePositions = {
	["32073:32276:7"] = true,
	["32067:32281:7"] = true,
	["32079:32285:7"] = true,
	["32081:32276:7"] = true,
	["32066:32288:7"] = true,
}
local treeExhaustUntil = {}

local function positionKey(position)
	return string.format("%d:%d:%d", position.x, position.y, position.z)
end

local function isSamePosition(first, second)
	return first.x == second.x and first.y == second.y and first.z == second.z
end

local function isCollectingWoodActive(player)
	return player:getStorageValue(tutorialStorage.ZirellaNpcGreetStorage) == ZIRELLA_ACTIVE_STAGE and player:getStorageValue(tutorialStorage.ZirellaQuestLog) == ZIRELLA_ACTIVE_STAGE
end

local tutorialDeadTree = Action()

function tutorialDeadTree.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	if item.itemid ~= DEAD_TREE_ITEM_ID or not tutorialDeadTreePositions[positionKey(fromPosition)] then
		return false
	end

	if not isCollectingWoodActive(player) then
		return true
	end

	local playerGuid = player:getGuid()
	local now = os.time()
	if (treeExhaustUntil[playerGuid] or 0) > now then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You have to wait a few seconds until this tree can be used again.")
		return true
	end

	local branch = Game.createItem(BRANCH_ITEM_ID, 1, player:getPosition())
	if not branch then
		player:sendCancelMessage("There is not enough room to break off a branch.")
		return true
	end

	treeExhaustUntil[playerGuid] = now + TREE_EXHAUST_SECONDS
	player:sendTutorial(24)
	branch:decay()

	if player:getStorageValue(tutorialStorage.TutorialHintsStorage) < BRANCH_HINT_STAGE then
		player:setStorageValue(tutorialStorage.TutorialHintsStorage, BRANCH_HINT_STAGE)
	end
	return true
end

tutorialDeadTree:id(DEAD_TREE_ITEM_ID)
tutorialDeadTree:register()

local tutorialBranch = Action()

function tutorialBranch.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	if not target or target.itemid ~= ZIRELLA_CART_ITEM_ID or not isSamePosition(toPosition, zirellaCartPosition) then
		return false
	end

	if not isCollectingWoodActive(player) then
		return true
	end

	item:remove(1)
	toPosition:sendMagicEffect(CONST_ME_MAGIC_GREEN)
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Well done! You successfully used a branch on Zirella's cart. Talk to her and tell her you did it!")
	player:setStorageValue(tutorialStorage.ZirellaNpcGreetStorage, ZIRELLA_DELIVERED_STAGE)
	player:setStorageValue(tutorialStorage.ZirellaQuestLog, ZIRELLA_DELIVERED_STAGE)
	return true
end

tutorialBranch:id(BRANCH_ITEM_ID)
tutorialBranch:register()
