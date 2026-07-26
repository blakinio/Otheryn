local ClientPackets = {
	Taskboard = 0x5F,
}

local ServerPackets = {
	Taskboard = 0x5B,
}

local OutboundWindow = {
	Bounty = 0x00,
	Weekly = 0x01,
	Shop = 0x02,
}

local ClientAction = {
	Bounty = 0x00,
	Weekly = 0x01,
	BountyDifficulty = 0x02,
	BountyReroll = 0x03,
	ClaimDailyReroll = 0x04,
	BountySelect = 0x05,
	BountyClaimReward = 0x06,
	TalismanUpgrade = 0x07,
	WeeklyDelivery = 0x08,
	WeeklyDifficulty = 0x09,
	Shop = 0x0A,
	ShopBuy = 0x0B,
	UnlockPreferenceSlot = 0x0C,
	ClearPreferred = 0x0D,
	ClearUnwanted = 0x0E,
	AssignPreferred = 0x0F,
	AssignUnwanted = 0x10,
}

local OfferType = {
	BonusPromotion = 0x04,
}

local OfferId = {
	BonusPromotion = 0,
}

local OfferStatus = {
	Available = 0x00,
	NotEnoughPoints = 0x02,
	Bought = 0x04,
}

local Storage = {
	BonusPromotionPoints = 1000006,
}

local MaxBonusPromotionPoints = 50

local OneBytePayloadActions = {
	[ClientAction.BountyDifficulty] = true,
	[ClientAction.BountySelect] = true,
	[ClientAction.TalismanUpgrade] = true,
	[ClientAction.WeeklyDelivery] = true,
	[ClientAction.WeeklyDifficulty] = true,
}

local OneU16PayloadActions = {
	[ClientAction.UnlockPreferenceSlot] = true,
	[ClientAction.ClearPreferred] = true,
	[ClientAction.ClearUnwanted] = true,
}

local TwoU16PayloadActions = {
	[ClientAction.AssignPreferred] = true,
	[ClientAction.AssignUnwanted] = true,
}

local BountyResponseActions = {
	[ClientAction.Bounty] = true,
	[ClientAction.BountyDifficulty] = true,
	[ClientAction.BountyReroll] = true,
	[ClientAction.ClaimDailyReroll] = true,
	[ClientAction.BountySelect] = true,
	[ClientAction.BountyClaimReward] = true,
	[ClientAction.TalismanUpgrade] = true,
	[ClientAction.UnlockPreferenceSlot] = true,
	[ClientAction.ClearPreferred] = true,
	[ClientAction.ClearUnwanted] = true,
	[ClientAction.AssignPreferred] = true,
	[ClientAction.AssignUnwanted] = true,
}

local WeeklyResponseActions = {
	[ClientAction.Weekly] = true,
	[ClientAction.WeeklyDelivery] = true,
	[ClientAction.WeeklyDifficulty] = true,
}

local ShopResponseActions = {
	[ClientAction.Shop] = true,
}

-- Official-client packet shim for 15.25 Taskboard traffic.
-- Bounty and Weekly remain empty but structurally valid. The Shop exposes only
-- the bounded Wheel Bonus Promotion offer authorized by OAM-051B.

local function readU8(msg)
	if msg:getUnreadBytes() < 1 then
		return nil
	end

	return msg:getByte()
end

local function readU16(msg)
	if msg:getUnreadBytes() < 2 then
		return nil
	end

	return msg:getU16()
end

local function consumeU8(msg)
	return readU8(msg) ~= nil
end

local function consumeU16(msg)
	return readU16(msg) ~= nil
end

local function addEmptyBountyTalismanLine(msg)
	msg:addU16(0)
	msg:addByte(0)
	msg:addU16(0)
end

local function sendBountyWindow(player)
	local msg = NetworkMessage()
	msg:addByte(ServerPackets.Taskboard)
	msg:addByte(OutboundWindow.Bounty)
	msg:addByte(0) -- bounty task count
	msg:addByte(0) -- daily rerolls
	msg:addByte(0) -- reroll state
	msg:addByte(0) -- current difficulty
	addEmptyBountyTalismanLine(msg)
	addEmptyBountyTalismanLine(msg)
	addEmptyBountyTalismanLine(msg)
	addEmptyBountyTalismanLine(msg)
	msg:addByte(0) -- preferred/unwanted slot count
	msg:sendToPlayer(player)
end

local function sendWeeklyWindow(player)
	local msg = NetworkMessage()
	msg:addByte(ServerPackets.Taskboard)
	msg:addByte(OutboundWindow.Weekly)
	msg:addU16(0) -- any creature required amount
	msg:addU16(0) -- any creature current amount
	msg:addByte(0) -- weekly kill task count
	msg:addByte(0) -- weekly item task count
	msg:addByte(0) -- current difficulty
	msg:addU32(0) -- kill experience reward
	msg:addU32(0) -- item delivery experience reward
	msg:addByte(0) -- completed kill tasks
	msg:addByte(0) -- completed item tasks
	msg:addByte(0) -- difficulty selection available
	msg:addByte(0) -- suggested difficulty
	msg:addU32(0) -- next reset timestamp
	msg:addByte(0) -- third weekly slot unlocked
	msg:addU32(0) -- task hunting points reward
	msg:addU32(0) -- soulseals reward tail for current official clients
	msg:sendToPlayer(player)
end

local function getPurchasedBonusPromotionPoints(player)
	local storedPoints = player:getStorageValue(Storage.BonusPromotionPoints)
	if storedPoints < 0 then
		return 0
	end

	return math.min(storedPoints, MaxBonusPromotionPoints)
end

local function getBonusPromotionCost(purchasedPoints)
	if purchasedPoints >= MaxBonusPromotionPoints then
		return 0
	end

	local nextPoint = purchasedPoints + 1
	return 100 * (1 + nextPoint * (nextPoint - 1) / 2)
end

local function getBonusPromotionStatus(player, purchasedPoints, nextCost)
	if purchasedPoints >= MaxBonusPromotionPoints then
		return OfferStatus.Bought
	end

	if player:getTaskHuntingPoints() < nextCost then
		return OfferStatus.NotEnoughPoints
	end

	return OfferStatus.Available
end

local function purchaseBonusPromotion(player, offerId)
	if offerId ~= OfferId.BonusPromotion then
		return false
	end

	local purchasedPoints = getPurchasedBonusPromotionPoints(player)
	if purchasedPoints >= MaxBonusPromotionPoints then
		return false
	end

	local cost = getBonusPromotionCost(purchasedPoints)
	if cost == 0 or player:getTaskHuntingPoints() < cost then
		return false
	end

	-- PlayerStorage and Task Hunting state are persisted by the same player SQL
	-- transaction. Mutate storage first and restore it if the debit unexpectedly
	-- fails, so no in-memory half-purchase can survive to the save boundary.
	player:setStorageValue(Storage.BonusPromotionPoints, purchasedPoints + 1)
	if not player:removeTaskHuntingPoints(cost) then
		player:setStorageValue(Storage.BonusPromotionPoints, purchasedPoints)
		return false
	end

	return true
end

local function sendShopWindow(player)
	local purchasedPoints = getPurchasedBonusPromotionPoints(player)
	local nextCost = getBonusPromotionCost(purchasedPoints)
	local status = getBonusPromotionStatus(player, purchasedPoints, nextCost)

	local msg = NetworkMessage()
	msg:addByte(ServerPackets.Taskboard)
	msg:addByte(OutboundWindow.Shop)
	msg:addByte(1) -- offer count
	msg:addByte(OfferType.BonusPromotion)
	msg:addU16(purchasedPoints + 1)
	msg:addU32(nextCost)
	msg:addByte(status)
	msg:sendToPlayer(player)
end

local function sendWindow(player, window)
	if window == OutboundWindow.Weekly then
		sendWeeklyWindow(player)
	elseif window == OutboundWindow.Shop then
		sendShopWindow(player)
	else
		sendBountyWindow(player)
	end
end

local function consumeActionPayload(msg, action)
	if OneBytePayloadActions[action] then
		return consumeU8(msg)
	end

	if OneU16PayloadActions[action] then
		return consumeU16(msg)
	end

	if TwoU16PayloadActions[action] then
		return consumeU16(msg) and consumeU16(msg)
	end

	return true
end

function onRecvbyte(player, msg, byte)
	if byte ~= ClientPackets.Taskboard then
		return
	end

	local action = readU8(msg)
	if not action then
		logger.debug("[Taskboard] ignored malformed 0x5F packet from player='{}': missing action", player:getName())
		return
	end

	if action == ClientAction.ShopBuy then
		local offerId = readU16(msg)
		if not offerId then
			logger.debug("[Taskboard] ignored malformed 0x5F packet from player='{}': incomplete ShopBuy", player:getName())
			return
		end

		local trailingBytes = msg:getUnreadBytes()
		if trailingBytes > 0 then
			logger.debug("[Taskboard] ignored malformed 0x5F packet from player='{}': ShopBuy unexpected trailing bytes={}", player:getName(), trailingBytes)
			return
		end

		purchaseBonusPromotion(player, offerId)
		sendShopWindow(player)
		logger.debug("[Taskboard] player='{}' ShopBuy offer={} handled by bounded OAM-051B shop.", player:getName(), offerId)
		return
	end

	if not consumeActionPayload(msg, action) then
		logger.debug("[Taskboard] ignored malformed 0x5F packet from player='{}': incomplete action {}", player:getName(), action)
		return
	end

	local trailingBytes = msg:getUnreadBytes()
	if trailingBytes > 0 then
		logger.debug("[Taskboard] ignored malformed 0x5F packet from player='{}': action={} unexpected trailing bytes={}", player:getName(), action, trailingBytes)
		return
	end

	if BountyResponseActions[action] then
		sendWindow(player, OutboundWindow.Bounty)
	elseif WeeklyResponseActions[action] then
		sendWindow(player, OutboundWindow.Weekly)
	elseif ShopResponseActions[action] then
		sendWindow(player, OutboundWindow.Shop)
	else
		sendWindow(player, OutboundWindow.Bounty)
	end

	logger.debug("[Taskboard] player='{}' action={} handled by minimal official packet shim.", player:getName(), action)
end
