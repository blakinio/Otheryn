local replaceWriterFenceCheckSql = [[
ALTER TABLE `player_writer_fence`
	DROP CONSTRAINT `player_writer_fence_active_ck`,
	ADD CONSTRAINT `player_writer_fence_active_ck` CHECK (
		(`ownership_generation` = 0 AND `writer_token` IS NULL AND `state_revision` = 0)
		OR (`ownership_generation` > 0)
	);
]]

function onUpdateDatabase()
	logger.info("Updating database to version 60 (preserve released writer-fence generation and revision)")

	if not db.tableExists("player_writer_fence") then
		logger.error("Table player_writer_fence is missing while applying database version 60")
		return false
	end

	if not db.query(replaceWriterFenceCheckSql) then
		logger.error("Failed to replace player_writer_fence active-state check")
		return false
	end

	return true
end
