if not ForgeMonster then
	ForgeMonster = {
		timeLeftToChangeMonsters = {},
		names = {
			[FORGE_NORMAL_MONSTER] = "normal",
			[FORGE_INFLUENCED_MONSTER] = "influenced",
			[FORGE_FIENDISH_MONSTER] = "fiendish",
		},
		chanceToAppear = {
			fiendish = 80,
			influenced = 20,
		},
		maxFiendish = 4,
		eventName = "ForgeMonster",
	}
end

function getFiendishMinutesLeft(leftTime)
	local secLeft = leftTime - os.time()
	local desc = "This monster will stay fiendish for less than"

	if math.floor(secLeft / 60) >= 1 then
		desc = desc .. " " .. math.floor(secLeft / 60) .. " minutes and"
		secLeft = secLeft - math.floor(secLeft / 60) * 60
	end

	if secLeft < 60 then
		desc = desc .. " " .. secLeft .. " seconds."
	end
	return desc
end

function ForgeMonster:getTimeLeftToChangeMonster(creature)
	local monster = Monster(creature)
	if monster then
		local leftTime = monster:getTimeToChangeFiendish()
		leftTime = leftTime or 0
		return getFiendishMinutesLeft(leftTime)
	end
	return 0
end

function ForgeMonster:getPlayerKiller(killer)
	if not killer then
		return nil
	end

	if killer:isPlayer() then
		return killer
	end

	local master = killer:getMaster()
	if master and master:isPlayer() then
		return master
	end
	return nil
end

function ForgeMonster:creditDust(player, amount)
	if not player then
		return 0
	end

	if not player:isPremium() then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You did not receive " .. amount .. " dust for the Exaltation Forge because a Premium Account is required.")
		return 0
	end

	local totalDusts = player:getForgeDusts()
	local limitDusts = player:getForgeDustLevel()
	if totalDusts >= limitDusts then
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You did not receive " .. amount .. " dust for the Exaltation Forge because you have already reached the maximum of " .. limitDusts .. " dust.")
		return 0
	end

	local creditedAmount = math.min(amount, limitDusts - totalDusts)
	player:addForgeDusts(creditedAmount)
	local actualTotalDusts = player:getForgeDusts()
	player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You received " .. creditedAmount .. " dust for the Exaltation Forge. You now have " .. actualTotalDusts .. " out of a maximum of " .. limitDusts .. " dusts.")
	return creditedAmount
end

function ForgeMonster:onDeath(creature, corpse, killer, mostDamageKiller, unjustified, mostDamageUnjustified)
	if not creature then
		return true
	end

	local stack = creature:getForgeStack()
	if stack <= 0 then
		return true
	end

	local playerKiller = self:getPlayerKiller(killer)
	if not playerKiller then
		return true
	end

	local forgeAmountMultiplier = configManager.getFloat(configKeys.FORGE_AMOUNT_MULTIPLIER) or 3
	local amount = math.random(stack, forgeAmountMultiplier * stack)
	local party = playerKiller:getParty()
	if not party or not party:isSharedExperienceEnabled() then
		self:creditDust(playerKiller, amount)
		return true
	end

	local recipients = { party:getLeader() }
	for _, member in ipairs(party:getMembers()) do
		if member and not table.contains(recipients, member) then
			table.insert(recipients, member)
		end
	end

	for _, recipient in ipairs(recipients) do
		if recipient and recipient:hasCondition(CONDITION_INFIGHT) then
			self:creditDust(recipient, amount)
		end
	end
	return true
end

function ForgeMonster:onSpawn(creature)
	local monster = Monster(creature)
	if not monster then
		return false
	end

	local monsterType = monster:getType()
	if not monsterType then
		return false
	end

	local pos = monster:getPosition()
	local tile = Tile(pos)
	if tile and tile:hasFlag(TILESTATE_NOLOGOUT) then
		return false
	end

	Game.addInfluencedMonster(monster)
end

function ForgeMonster:pickFiendish()
	for _, cid in pairs(Game.getFiendishMonsters()) do
		if Monster(cid) then
			return cid
		end
	end
	return 0
end

function ForgeMonster:pickInfluenced()
	for _, cid in pairs(Game.getInfluencedMonsters()) do
		if Monster(cid) then
			return cid
		end
	end
	return 0
end

function ForgeMonster:pickClosestFiendish(creature)
	local player = Player(creature)
	if not player then
		return 0
	end

	local creatures = {}

	local playerPosition = player:getPosition()
	for _, cid in pairs(Game.getFiendishMonsters()) do
		if Monster(cid) then
			creatures[#creatures + 1] = { cid = cid, distance = Monster(cid):getPosition():getDistance(playerPosition) }
		end
	end

	if #creatures == 0 then
		return false
	end

	table.sort(creatures, function(a, b)
		return a.distance < b.distance
	end)
	return creatures[1].cid
end

function ForgeMonster:exceededMaxInfluencedMonsters()
	local totalMonsters = 0
	for _, cid in pairs(Game.getInfluencedMonsters()) do
		if Monster(cid) then
			totalMonsters = totalMonsters + 1
		end
	end
	local configMaxMonsters = configManager.getNumber(configKeys.FORGE_INFLUENCED_CREATURES_LIMIT)
	if totalMonsters >= configMaxMonsters then
		return true
	end
	return false
end
