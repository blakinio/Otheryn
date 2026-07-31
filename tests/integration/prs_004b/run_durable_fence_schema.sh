#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
work_dir="$(mktemp -d)"
trap 'rm -rf "${work_dir}"' EXIT

host="${TEST_DB_HOST:-127.0.0.1}"
port="${TEST_DB_PORT:-3306}"
user="${TEST_DB_USER:-root}"
database="${TEST_DB_NAME:-prs004b_test}"
export MYSQL_PWD="${TEST_DB_PASSWORD:-root}"
mysql_base=(mariadb --protocol=tcp --host="${host}" --port="${port}" --user="${user}" --batch --skip-column-names)

ready=false
for _ in $(seq 1 60); do
	if "${mysql_base[@]}" -e "SELECT 1" >/dev/null 2>&1; then
		ready=true
		break
	fi
	sleep 1
done
if [[ "${ready}" != "true" ]]; then
	echo "MariaDB did not become ready" >&2
	exit 1
fi

scalar() {
	"${mysql_base[@]}" "${database}" -e "$1"
}

require_equal() {
	local expected="$1"
	local actual="$2"
	local label="$3"
	if [[ "${actual}" != "${expected}" ]]; then
		echo "${label}: expected '${expected}', got '${actual}'" >&2
		exit 1
	fi
}

verify_contract() {
	local player_count
	local fence_count
	player_count="$(scalar "SELECT COUNT(*) FROM players")"
	fence_count="$(scalar "SELECT COUNT(*) FROM player_writer_fence")"

	require_equal "59" "$(scalar "SELECT value FROM server_config WHERE config = 'db_version'")" "database version"
	require_equal "1" "$(scalar "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'player_writer_fence'")" "authority table"
	require_equal "1" "$(scalar "SELECT COUNT(*) FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = DATABASE() AND TRIGGER_NAME = 'oncreate_player_writer_fence'")" "creation trigger"
	require_equal "4" "$(scalar "SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'player_writer_fence'")" "authority columns"
	require_equal "1" "$(scalar "SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME = 'player_writer_fence' AND CONSTRAINT_NAME = 'player_writer_fence_pk' AND CONSTRAINT_TYPE = 'PRIMARY KEY'")" "subject primary key"
	require_equal "1" "$(scalar "SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME = 'player_writer_fence' AND CONSTRAINT_NAME = 'player_writer_fence_token_uq' AND CONSTRAINT_TYPE = 'UNIQUE'")" "token uniqueness"
	require_equal "1" "$(scalar "SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = DATABASE() AND TABLE_NAME = 'player_writer_fence' AND CONSTRAINT_NAME = 'player_writer_fence_active_ck' AND CONSTRAINT_TYPE = 'CHECK'")" "active-state check"
	require_equal "1" "$(scalar "SELECT COUNT(*) FROM information_schema.REFERENTIAL_CONSTRAINTS WHERE CONSTRAINT_SCHEMA = DATABASE() AND CONSTRAINT_NAME = 'player_writer_fence_player_fk' AND REFERENCED_TABLE_NAME = 'players' AND DELETE_RULE = 'CASCADE'")" "subject foreign key"
	require_equal "${player_count}" "${fence_count}" "one authority row per player"
	require_equal "0" "$(scalar "SELECT COUNT(*) FROM player_writer_fence WHERE ownership_generation <> 0 OR writer_token IS NOT NULL OR state_revision <> 0")" "inactive backfill"
}

extract_migration_sql() {
	python3 - "${repo_root}/data-otservbr-global/migrations/59.lua" "${work_dir}/59.sql" <<'PY'
import re
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text(encoding="utf-8")
statements = []
for name in ("createWriterFenceTableSql", "backfillWriterFenceSql", "createWriterFenceTriggerSql"):
    match = re.search(rf"local {name} = \[\[(.*?)\]\]", source, re.DOTALL)
    if match is None:
        raise SystemExit(f"missing migration SQL literal: {name}")
    statements.append(match.group(1).strip())
Path(sys.argv[2]).write_text("\n\n".join(statements) + "\n", encoding="utf-8")
PY
}

rollback_to_58() {
	"${mysql_base[@]}" "${database}" <<'SQL'
DROP TRIGGER IF EXISTS `oncreate_player_writer_fence`;
DROP TABLE IF EXISTS `player_writer_fence`;
UPDATE `server_config` SET `value` = '58' WHERE `config` = 'db_version' AND `value` = '59';
SQL
	require_equal "58" "$(scalar "SELECT value FROM server_config WHERE config = 'db_version'")" "rollback version"
	require_equal "0" "$(scalar "SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'player_writer_fence'")" "rollback table"
	require_equal "0" "$(scalar "SELECT COUNT(*) FROM information_schema.TRIGGERS WHERE TRIGGER_SCHEMA = DATABASE() AND TRIGGER_NAME = 'oncreate_player_writer_fence'")" "rollback trigger"
}

apply_migration_sql() {
	"${mysql_base[@]}" "${database}" < "${work_dir}/59.sql"
	"${mysql_base[@]}" "${database}" -e "UPDATE server_config SET value = '59' WHERE config = 'db_version' AND value = '58'"
}

"${mysql_base[@]}" -e "DROP DATABASE IF EXISTS \`${database}\`; CREATE DATABASE \`${database}\` CHARACTER SET utf8 COLLATE utf8_general_ci"
"${mysql_base[@]}" "${database}" < "${repo_root}/schema.sql"
verify_contract

"${mysql_base[@]}" "${database}" -e "INSERT INTO players (name, account_id, conditions) VALUES ('PRS004B Trigger Subject', 1, '')"
subject_id="$(scalar "SELECT id FROM players WHERE name = 'PRS004B Trigger Subject'")"
require_equal "0:NULL:0" "$(scalar "SELECT CONCAT(ownership_generation, ':', COALESCE(HEX(writer_token), 'NULL'), ':', state_revision) FROM player_writer_fence WHERE player_id = ${subject_id}")" "trigger-created authority"

if "${mysql_base[@]}" "${database}" -e "UPDATE player_writer_fence SET ownership_generation = 0, writer_token = UNHEX('00112233445566778899AABBCCDDEEFF') WHERE player_id = ${subject_id}" >/dev/null 2>&1; then
	echo "zero generation with token was accepted" >&2
	exit 1
fi
if "${mysql_base[@]}" "${database}" -e "UPDATE player_writer_fence SET ownership_generation = 1, writer_token = NULL WHERE player_id = ${subject_id}" >/dev/null 2>&1; then
	echo "positive generation without token was accepted" >&2
	exit 1
fi

"${mysql_base[@]}" "${database}" -e "UPDATE player_writer_fence SET ownership_generation = 1, writer_token = UNHEX('00112233445566778899AABBCCDDEEFF') WHERE player_id = ${subject_id}"
"${mysql_base[@]}" "${database}" -e "INSERT INTO players (name, account_id, conditions) VALUES ('PRS004B Duplicate Token Subject', 1, '')"
duplicate_id="$(scalar "SELECT id FROM players WHERE name = 'PRS004B Duplicate Token Subject'")"
if "${mysql_base[@]}" "${database}" -e "UPDATE player_writer_fence SET ownership_generation = 1, writer_token = UNHEX('00112233445566778899AABBCCDDEEFF') WHERE player_id = ${duplicate_id}" >/dev/null 2>&1; then
	echo "duplicate writer token was accepted" >&2
	exit 1
fi

extract_migration_sql
for _ in 1 2; do
	rollback_to_58
	apply_migration_sql
	verify_contract
done

python3 - "${repo_root}" <<'PY'
import sys
from pathlib import Path

root = Path(sys.argv[1])
schema = (root / "schema.sql").read_text(encoding="utf-8")
migration = (root / "data-otservbr-global/migrations/59.lua").read_text(encoding="utf-8")
for token in (
    "player_writer_fence",
    "player_writer_fence_pk",
    "player_writer_fence_token_uq",
    "player_writer_fence_active_ck",
    "player_writer_fence_player_fk",
    "oncreate_player_writer_fence",
):
    assert token in schema, f"schema missing {token}"
    assert token in migration, f"migration missing {token}"
assert "('db_version', '59')" in schema
assert "retryQuery" not in migration
assert "MYSQL_OPT_RECONNECT" not in migration
assert "mysql_ping" not in migration
PY

echo "PRS-004B durable writer-fence schema evidence: PASS"
