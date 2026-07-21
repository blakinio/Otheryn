#!/usr/bin/env python3
from pathlib import Path

path = Path("src/creatures/players/components/player_cyclopedia.cpp")
text = path.read_text(encoding="utf-8")
old = "(select count(*) FROM `player_deaths` WHERE ((`killed_by` = {} AND `is_player` = 1) OR (`mostdamage_by` = {} AND `mostdamage_is_player` = 1))) as `entries`"
new = "(select count(*) FROM `player_deaths` WHERE ((`killed_by` = {} AND `is_player` = 1) OR (`mostdamage_by` = {} AND `mostdamage_is_player` = 1)) AND `time` >= UNIX_TIMESTAMP(DATE_SUB(NOW(), INTERVAL 70 DAY))) as `entries`"
count = text.count(old)
if count != 1:
    raise SystemExit(f"expected exactly one donor precondition match, found {count}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("materialized OAM-029 recent-PvP count-window correction")
