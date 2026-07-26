#!/usr/bin/env bash
set -Eeuo pipefail

require_env() {
	local name="$1"
	if [[ -z "${!name:-}" ]]; then
		echo "ERROR: required environment variable ${name} is not set" >&2
		exit 64
	fi
}

for command_name in docker python3; do
	if ! command -v "${command_name}" >/dev/null 2>&1; then
		echo "ERROR: required command is unavailable: ${command_name}" >&2
		exit 69
	fi
done

require_env PRS001_VERIFIED_DIR
require_env PRS001_RESTORE_VOLUME
require_env PRS001_RESTORE_CONTAINER
require_env PRS001_NETWORK
require_env PRS001_DB_ROOT_PASSWORD
require_env PRS001_TARGET_DATETIME
require_env PRS001_MARIADB_IMAGE
require_env PRS001_MARIADB_VERSION

if [[ ! -d "${PRS001_VERIFIED_DIR}/full" || ! -d "${PRS001_VERIFIED_DIR}/binlogs" || ! -s "${PRS001_VERIFIED_DIR}/manifest.json" ]]; then
	echo "ERROR: verified recovery-set directory is incomplete" >&2
	exit 66
fi
if docker inspect "${PRS001_RESTORE_CONTAINER}" >/dev/null 2>&1; then
	echo "ERROR: restore container already exists and will not be replaced" >&2
	exit 65
fi
if ! docker volume inspect "${PRS001_RESTORE_VOLUME}" >/dev/null 2>&1; then
	echo "ERROR: restore volume does not exist" >&2
	exit 66
fi
if ! docker network inspect "${PRS001_NETWORK}" >/dev/null 2>&1; then
	echo "ERROR: restore network does not exist" >&2
	exit 66
fi

verified_dir="$(cd "${PRS001_VERIFIED_DIR}" && pwd -P)"

readarray -t manifest_values < <(python3 - \
	"${verified_dir}/manifest.json" \
	"${PRS001_TARGET_DATETIME}" \
	"${PRS001_MARIADB_IMAGE}" \
	"${PRS001_MARIADB_VERSION}" <<'PY'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

manifest_path, target_text, expected_image, expected_version = sys.argv[1:]
manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
if manifest.get("mariadb_image") != expected_image:
    raise SystemExit("manifest image does not match the pinned image")
if manifest.get("mariadb_version_expected") != expected_version:
    raise SystemExit("manifest version does not match the pinned version")
try:
    target = datetime.strptime(target_text, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
except ValueError as exc:
    raise SystemExit("target datetime must use YYYY-MM-DD HH:MM:SS in UTC") from exc

def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value[:-1] + "+00:00")

backup_completed = parse_utc(manifest["backup_completed_at"])
archive_completed = parse_utc(manifest["archive_completed_at"])
if not backup_completed <= target <= archive_completed:
    raise SystemExit("target datetime is outside the recoverable range")
print(manifest["backup_binlog_file"])
print(manifest["backup_binlog_position"])
PY
)
backup_binlog_file="${manifest_values[0]:-}"
backup_binlog_position="${manifest_values[1]:-}"
if [[ -z "${backup_binlog_file}" || ! "${backup_binlog_position}" =~ ^[0-9]+$ ]]; then
	echo "ERROR: manifest did not provide a valid backup coordinate" >&2
	exit 72
fi

read -r coordinate_file coordinate_position _ < "${verified_dir}/full/xtrabackup_binlog_info"
if [[ "${coordinate_file}" != "${backup_binlog_file}" || "${coordinate_position}" != "${backup_binlog_position}" ]]; then
	echo "ERROR: manifest and physical-backup coordinates disagree" >&2
	exit 72
fi

mapfile -t archived_binlogs < <(find "${verified_dir}/binlogs" -maxdepth 1 -type f -name 'mariadb-bin.[0-9]*' -printf '%f\n' | sort)
if [[ ${#archived_binlogs[@]} -eq 0 ]]; then
	echo "ERROR: no archived binlogs are available" >&2
	exit 72
fi

python3 - "${backup_binlog_file}" "${archived_binlogs[@]}" <<'PY'
import re
import sys

coordinate = sys.argv[1]
files = sys.argv[2:]
pattern = re.compile(r"^mariadb-bin\.(\d+)$")
numbers = []
for name in files:
    match = pattern.fullmatch(name)
    if not match:
        raise SystemExit("invalid archived binlog filename")
    numbers.append(int(match.group(1)))
if coordinate not in files:
    raise SystemExit("backup coordinate binlog is missing from the archive")
for previous, current in zip(numbers, numbers[1:]):
    if current != previous + 1:
        raise SystemExit("archived binlog sequence has a gap")
PY

selected_binlogs=()
include=0
for binlog in "${archived_binlogs[@]}"; do
	if [[ "${binlog}" == "${backup_binlog_file}" ]]; then
		include=1
	fi
	if [[ ${include} -eq 1 ]]; then
		selected_binlogs+=("${binlog}")
	fi
done
if [[ ${#selected_binlogs[@]} -eq 0 ]]; then
	echo "ERROR: no binlogs remain after the backup coordinate" >&2
	exit 72
fi

if [[ "${PRS001_FAIL_AT:-}" == "prepare" ]]; then
	echo "ERROR: injected prepare failure" >&2
	exit 73
fi

docker run --rm \
	--entrypoint mariadb-backup \
	--volume "${verified_dir}/full:/backup" \
	"${PRS001_MARIADB_IMAGE}" \
	--prepare --target-dir=/backup

docker run --rm \
	--entrypoint sh \
	--volume "${verified_dir}/full:/backup:ro" \
	--volume "${PRS001_RESTORE_VOLUME}:/var/lib/mysql" \
	"${PRS001_MARIADB_IMAGE}" \
	-ceu '
		find /var/lib/mysql -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
		mariadb-backup --copy-back --target-dir=/backup
		chown -R mysql:mysql /var/lib/mysql
	'

startup_arguments=()
if [[ "${PRS001_FAIL_AT:-}" == "startup" ]]; then
	startup_arguments+=("--definitely-invalid-prs001-option")
fi

docker run --detach \
	--name "${PRS001_RESTORE_CONTAINER}" \
	--network "${PRS001_NETWORK}" \
	--env MARIADB_ROOT_PASSWORD="${PRS001_DB_ROOT_PASSWORD}" \
	--volume "${PRS001_RESTORE_VOLUME}:/var/lib/mysql" \
	"${PRS001_MARIADB_IMAGE}" \
	"${startup_arguments[@]}" >/dev/null

ready=0
for _ in $(seq 1 90); do
	if docker exec \
		-e MYSQL_PWD="${PRS001_DB_ROOT_PASSWORD}" \
		"${PRS001_RESTORE_CONTAINER}" \
		mariadb-admin --protocol=tcp --host=127.0.0.1 --user=root ping --silent >/dev/null 2>&1; then
		ready=1
		break
	fi
	if [[ "$(docker inspect --format '{{.State.Running}}' "${PRS001_RESTORE_CONTAINER}" 2>/dev/null || true)" != "true" ]]; then
		break
	fi
	sleep 1
done
if [[ ${ready} -ne 1 ]]; then
	echo "ERROR: restored MariaDB did not become ready" >&2
	docker logs "${PRS001_RESTORE_CONTAINER}" >&2 || true
	exit 74
fi

docker exec "${PRS001_RESTORE_CONTAINER}" mkdir -p /tmp/prs001-binlogs
docker cp "${verified_dir}/binlogs/." "${PRS001_RESTORE_CONTAINER}:/tmp/prs001-binlogs/"

container_binlogs=()
for binlog in "${selected_binlogs[@]}"; do
	container_binlogs+=("/tmp/prs001-binlogs/${binlog}")
done

docker exec \
	-e MYSQL_PWD="${PRS001_DB_ROOT_PASSWORD}" \
	"${PRS001_RESTORE_CONTAINER}" \
	sh -ceu '
		start_position="$1"
		target_datetime="$2"
		shift 2
		mariadb-binlog \
			--start-position="${start_position}" \
			--stop-datetime="${target_datetime}" \
			"$@" | mariadb --protocol=tcp --host=127.0.0.1 --user=root
	' sh "${backup_binlog_position}" "${PRS001_TARGET_DATETIME}" "${container_binlogs[@]}"

echo "${PRS001_RESTORE_CONTAINER}"
