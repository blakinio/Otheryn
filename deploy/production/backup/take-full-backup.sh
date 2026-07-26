#!/usr/bin/env bash
set -Eeuo pipefail

require_env() {
	local name="$1"
	if [[ -z "${!name:-}" ]]; then
		echo "ERROR: required environment variable ${name} is not set" >&2
		exit 64
	fi
}

require_env PRS001_PRIMARY_CONTAINER
require_env PRS001_BACKUP_ID
require_env PRS001_DB_ROOT_PASSWORD

if ! command -v docker >/dev/null 2>&1; then
	echo "ERROR: docker is required" >&2
	exit 69
fi

if [[ ! "${PRS001_BACKUP_ID}" =~ ^[A-Za-z0-9._-]+$ ]]; then
	echo "ERROR: PRS001_BACKUP_ID contains unsupported characters" >&2
	exit 64
fi

if ! docker inspect "${PRS001_PRIMARY_CONTAINER}" >/dev/null 2>&1; then
	echo "ERROR: primary container does not exist: ${PRS001_PRIMARY_CONTAINER}" >&2
	exit 66
fi

backup_started_at="$({
	docker exec \
		-e MYSQL_PWD="${PRS001_DB_ROOT_PASSWORD}" \
		"${PRS001_PRIMARY_CONTAINER}" \
		mariadb --protocol=tcp --host=127.0.0.1 --user=root --batch --skip-column-names \
		--execute="SELECT DATE_FORMAT(UTC_TIMESTAMP(6), '%Y-%m-%dT%H:%i:%s.%fZ')"
} | tr -d '\r')"

if [[ -z "${backup_started_at}" ]]; then
	echo "ERROR: failed to read backup start time from MariaDB" >&2
	exit 70
fi

docker exec \
	-e PRS001_DB_ROOT_PASSWORD="${PRS001_DB_ROOT_PASSWORD}" \
	"${PRS001_PRIMARY_CONTAINER}" \
	sh -ceu '
		backup_id="$1"
		backup_started_at="$2"
		fail_at="$3"
		backup_root="/backup/${backup_id}"
		credentials_file="${backup_root}/.client.cnf"

		if [ -e "${backup_root}" ]; then
			echo "ERROR: backup identifier already exists: ${backup_id}" >&2
			exit 65
		fi

		umask 077
		mkdir -p "${backup_root}/full"
		printf "%s\n" "${backup_started_at}" > "${backup_root}/backup-started-at"
		printf "[client]\nuser=root\npassword=%s\nhost=127.0.0.1\nprotocol=tcp\n" \
			"${PRS001_DB_ROOT_PASSWORD}" > "${credentials_file}"
		cleanup_credentials() {
			rm -f "${credentials_file}"
		}
		trap cleanup_credentials EXIT

		if [ "${fail_at}" = "backup" ]; then
			echo "ERROR: injected backup command failure" >&2
			exit 70
		fi

		mariadb-backup \
			--defaults-extra-file="${credentials_file}" \
			--backup \
			--target-dir="${backup_root}/full" \
			--binlog-info=ON

		test -s "${backup_root}/full/mariadb_backup_checkpoints"
		test -s "${backup_root}/full/mariadb_backup_binlog_info"

		backup_completed_at="$(mariadb \
			--defaults-extra-file="${credentials_file}" \
			--batch --skip-column-names \
			--execute="SELECT DATE_FORMAT(UTC_TIMESTAMP(6), '\''%Y-%m-%dT%H:%i:%s.%fZ'\'')")"
		printf "%s\n" "${backup_completed_at}" > "${backup_root}/backup-completed-at"
	' sh "${PRS001_BACKUP_ID}" "${backup_started_at}" "${PRS001_FAIL_AT:-}"

echo "/backup/${PRS001_BACKUP_ID}/full"
