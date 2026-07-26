#!/usr/bin/env bash
set -Eeuo pipefail

require_env() {
	local name="$1"
	if [[ -z "${!name:-}" ]]; then
		echo "ERROR: required environment variable ${name} is not set" >&2
		exit 64
	fi
}

for command_name in docker gpg python3 sha256sum tar; do
	if ! command -v "${command_name}" >/dev/null 2>&1; then
		echo "ERROR: required command is unavailable: ${command_name}" >&2
		exit 69
	fi
done

require_env PRS001_PRIMARY_CONTAINER
require_env PRS001_BACKUP_VOLUME
require_env PRS001_BACKUP_ID
require_env PRS001_DB_ROOT_PASSWORD
require_env PRS001_ARTIFACT_STORE
require_env PRS001_ENCRYPTION_PASSPHRASE_FILE
require_env PRS001_MARIADB_IMAGE
require_env PRS001_MARIADB_VERSION
require_env PRS001_RECOVERY_FORMAT_VERSION

if [[ ! "${PRS001_BACKUP_ID}" =~ ^[A-Za-z0-9._-]+$ ]]; then
	echo "ERROR: PRS001_BACKUP_ID contains unsupported characters" >&2
	exit 64
fi

if [[ ! -s "${PRS001_ENCRYPTION_PASSPHRASE_FILE}" ]]; then
	echo "ERROR: encryption passphrase file is missing or empty" >&2
	exit 66
fi

if ! docker inspect "${PRS001_PRIMARY_CONTAINER}" >/dev/null 2>&1; then
	echo "ERROR: primary container does not exist: ${PRS001_PRIMARY_CONTAINER}" >&2
	exit 66
fi

mkdir -p "${PRS001_ARTIFACT_STORE}"
artifact_store="$(cd "${PRS001_ARTIFACT_STORE}" && pwd -P)"
final_dir="${artifact_store}/${PRS001_BACKUP_ID}"

if [[ -e "${final_dir}" ]]; then
	echo "ERROR: recovery set already exists and will not be replaced: ${final_dir}" >&2
	exit 65
fi

work_dir="$(mktemp -d)"
staging_dir="${artifact_store}/.tmp-${PRS001_BACKUP_ID}-$$"
cleanup() {
	rm -rf "${work_dir}"
	if [[ -d "${staging_dir}" ]]; then
		rm -rf "${staging_dir}"
	fi
}
trap cleanup EXIT

# Close the current binlog before copying the archive. The newly opened file is
# copied too so continuity can be checked without racing a partially written log.
docker exec \
	-e PRS001_DB_ROOT_PASSWORD="${PRS001_DB_ROOT_PASSWORD}" \
	"${PRS001_PRIMARY_CONTAINER}" \
	sh -ceu '
		backup_id="$1"
		backup_root="/backup/${backup_id}"
		credentials_file="${backup_root}/.publish-client.cnf"
		test -s "${backup_root}/full/mariadb_backup_binlog_info"
		test -s "${backup_root}/backup-started-at"
		test -s "${backup_root}/backup-completed-at"

		umask 077
		printf "[client]\nuser=root\npassword=%s\nhost=127.0.0.1\nprotocol=tcp\n" \
			"${PRS001_DB_ROOT_PASSWORD}" > "${credentials_file}"
		cleanup_credentials() {
			rm -f "${credentials_file}"
		}
		trap cleanup_credentials EXIT

		mariadb --defaults-extra-file="${credentials_file}" --execute="FLUSH BINARY LOGS"
		rm -rf "${backup_root}/binlogs"
		mkdir -p "${backup_root}/binlogs"
		set -- /var/lib/mysql/mariadb-bin.[0-9]*
		if [ ! -e "$1" ]; then
			echo "ERROR: no MariaDB binary logs were found" >&2
			exit 72
		fi
		cp "$@" "${backup_root}/binlogs/"

		archive_completed_at="$(mariadb \
			--defaults-extra-file="${credentials_file}" \
			--batch --skip-column-names \
			--execute="SELECT DATE_FORMAT(UTC_TIMESTAMP(6), '\''%Y-%m-%dT%H:%i:%s.%fZ'\'')")"
		printf "%s\n" "${archive_completed_at}" > "${backup_root}/archive-completed-at"
	' sh "${PRS001_BACKUP_ID}"

# Extract only package-owned backup material from the Docker volume. No database
# or production path is accepted from the caller.
docker run --rm \
	--entrypoint sh \
	--volume "${PRS001_BACKUP_VOLUME}:/backup:ro" \
	--volume "${work_dir}:/out" \
	"${PRS001_MARIADB_IMAGE}" \
	-ceu '
		backup_id="$1"
		backup_root="/backup/${backup_id}"
		cd "${backup_root}"
		test -s full/mariadb_backup_binlog_info
		test -s backup-started-at
		test -s backup-completed-at
		test -s archive-completed-at
		cp full/mariadb_backup_binlog_info backup-started-at backup-completed-at archive-completed-at /out/
		for file in binlogs/mariadb-bin.[0-9]*; do
			test -e "${file}" || exit 72
			basename "${file}"
		done | sort > /out/binlog-files.txt
		find full binlogs -type f -print0 | sort -z | xargs -0 sha256sum > /out/FILES.sha256
		tar -cf /out/payload.tar full binlogs
	' sh "${PRS001_BACKUP_ID}"

read -r backup_binlog_file backup_binlog_position _ < "${work_dir}/mariadb_backup_binlog_info"
if [[ ! "${backup_binlog_file}" =~ ^mariadb-bin\.[0-9]+$ ]] || [[ ! "${backup_binlog_position}" =~ ^[0-9]+$ ]]; then
	echo "ERROR: invalid backup binlog coordinate" >&2
	exit 72
fi

first_archived_binlog="$(head -n 1 "${work_dir}/binlog-files.txt")"
last_archived_binlog="$(tail -n 1 "${work_dir}/binlog-files.txt")"
if [[ -z "${first_archived_binlog}" || -z "${last_archived_binlog}" ]]; then
	echo "ERROR: binary log archive is empty" >&2
	exit 72
fi

reported_version="$({
	docker exec \
		-e MYSQL_PWD="${PRS001_DB_ROOT_PASSWORD}" \
		"${PRS001_PRIMARY_CONTAINER}" \
		mariadb --protocol=tcp --host=127.0.0.1 --user=root --batch --skip-column-names \
		--execute="SELECT VERSION()"
} | tr -d '\r')"

local_package="${work_dir}/local-package"
mkdir -m 700 "${local_package}" "${local_package}/envelope"
mv "${work_dir}/payload.tar" "${local_package}/envelope/payload.tar"
mv "${work_dir}/FILES.sha256" "${local_package}/envelope/FILES.sha256"

tar -C "${local_package}/envelope" -cf "${local_package}/envelope.tar" payload.tar FILES.sha256
gpg --batch --yes --pinentry-mode loopback \
	--passphrase-file "${PRS001_ENCRYPTION_PASSPHRASE_FILE}" \
	--symmetric --cipher-algo AES256 --s2k-mode 3 --s2k-digest-algo SHA512 \
	--output "${local_package}/payload.tar.gpg" \
	"${local_package}/envelope.tar"
rm -rf "${local_package}/envelope" "${local_package}/envelope.tar"

python3 - \
	"${local_package}/manifest.json" \
	"${PRS001_RECOVERY_FORMAT_VERSION}" \
	"${PRS001_BACKUP_ID}" \
	"${PRS001_MARIADB_IMAGE}" \
	"${PRS001_MARIADB_VERSION}" \
	"${reported_version}" \
	"$(cat "${work_dir}/backup-started-at")" \
	"$(cat "${work_dir}/backup-completed-at")" \
	"$(cat "${work_dir}/archive-completed-at")" \
	"${backup_binlog_file}" \
	"${backup_binlog_position}" \
	"${first_archived_binlog}" \
	"${last_archived_binlog}" <<'PY'
import json
import sys
from pathlib import Path

(
    manifest_path,
    format_version,
    backup_id,
    image,
    expected_version,
    reported_version,
    backup_started_at,
    backup_completed_at,
    archive_completed_at,
    backup_binlog_file,
    backup_binlog_position,
    first_archived_binlog,
    last_archived_binlog,
) = sys.argv[1:]

manifest = {
    "format_version": int(format_version),
    "backup_id": backup_id,
    "mariadb_image": image,
    "mariadb_version_expected": expected_version,
    "mariadb_version_reported": reported_version,
    "backup_started_at": backup_started_at,
    "backup_completed_at": backup_completed_at,
    "archive_completed_at": archive_completed_at,
    "backup_binlog_file": backup_binlog_file,
    "backup_binlog_position": int(backup_binlog_position),
    "first_archived_binlog": first_archived_binlog,
    "last_archived_binlog": last_archived_binlog,
    "incremental_backup": False,
    "payload_encryption": "gpg-symmetric-aes256",
}
Path(manifest_path).write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY

(
	cd "${local_package}"
	sha256sum manifest.json payload.tar.gpg > SHA256SUMS
)

if [[ "${PRS001_FAIL_AT:-}" == "publish" ]]; then
	echo "ERROR: injected artifact publication failure" >&2
	exit 71
fi

mkdir -m 700 "${staging_dir}"
cp "${local_package}/manifest.json" "${local_package}/payload.tar.gpg" "${local_package}/SHA256SUMS" "${staging_dir}/"
(
	cd "${staging_dir}"
	sha256sum --check SHA256SUMS
)
mv "${staging_dir}" "${final_dir}"

echo "${final_dir}"
