local createWriterFenceTableSql = [[
CREATE TABLE `player_writer_fence` (
	`player_id` int(11) NOT NULL,
	`ownership_generation` bigint(20) UNSIGNED NOT NULL DEFAULT '0',
	`writer_token` binary(16) DEFAULT NULL,
	`state_revision` bigint(20) UNSIGNED NOT NULL DEFAULT '0',
	CONSTRAINT `player_writer_fence_pk` PRIMARY KEY (`player_id`),
	CONSTRAINT `player_writer_fence_token_uq` UNIQUE (`writer_token`),
	CONSTRAINT `player_writer_fence_active_ck` CHECK (
		(`ownership_generation` = 0 AND `writer_token` IS NULL)
		OR (`ownership_generation` > 0 AND `writer_token` IS NOT NULL)
	),
	CONSTRAINT `player_writer_fence_player_fk`
		FOREIGN KEY (`player_id`) REFERENCES `players` (`id`)
		ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
]]

local backfillWriterFenceSql = [[
INSERT INTO `player_writer_fence`
	(`player_id`, `ownership_generation`, `writer_token`, `state_revision`)
SELECT `id`, 0, NULL, 0
FROM `players`;
]]

local createWriterFenceTriggerSql = [[
CREATE TRIGGER `oncreate_player_writer_fence`
AFTER INSERT ON `players`
FOR EACH ROW
INSERT INTO `player_writer_fence`
	(`player_id`, `ownership_generation`, `writer_token`, `state_revision`)
VALUES (NEW.`id`, 0, NULL, 0);
]]

local dropWriterFenceTriggerSql = [[
DROP TRIGGER IF EXISTS `oncreate_player_writer_fence`;
]]

local dropWriterFenceTableSql = [[
DROP TABLE IF EXISTS `player_writer_fence`;
]]

local function cleanupPartialMigration()
	local triggerDropped = db.query(dropWriterFenceTriggerSql)
	local tableDropped = db.query(dropWriterFenceTableSql)
	return triggerDropped and tableDropped
end

function onUpdateDatabase()
	logger.info("Updating database to version 59 (add durable player writer fence)")

	if db.tableExists("player_writer_fence") then
		logger.error("Table player_writer_fence already exists while database version is below 59")
		return false
	end

	if not db.query(createWriterFenceTableSql) then
		logger.error("Failed to create player_writer_fence table")
		return false
	end

	if not db.query(backfillWriterFenceSql) then
		logger.error("Failed to backfill player_writer_fence rows")
		if not cleanupPartialMigration() then
			logger.error("Failed to clean up partial player_writer_fence migration after backfill failure")
		end
		return false
	end

	if not db.query(createWriterFenceTriggerSql) then
		logger.error("Failed to create oncreate_player_writer_fence trigger")
		if not cleanupPartialMigration() then
			logger.error("Failed to clean up partial player_writer_fence migration after trigger failure")
		end
		return false
	end

	return true
end
