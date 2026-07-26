#!/usr/bin/env bash
set -Eeuo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
backup_dir="${repository_root}/deploy/production/backup"
# shellcheck disable=SC1091
source "${backup_dir}/versions.env"

for command_name in docker gpg python3 sha256sum tar; do
	if ! command -v "${command_name}" >/dev/null 2>&1; then
		echo "ERROR: required command is unavailable: ${command_name}" >&2
		exit 69
	fi
done

run_suffix="${GITHUB_RUN_ID:-$$}-${GITHUB_RUN_ATTEMPT:-1}-${RANDOM}"
run_suffix="${run_suffix//_/-}"
primary_container="prs001-primary-${run_suffix}"
restore_container="prs001-restore-${run_suffix}"
prepare_failure_container="prs001-prepare-fail-${run_suffix}"
startup_failure_container="prs001-startup-fail-${run_suffix}"
range_failure_container="prs001-range-fail-${run_suffix}"
network_name="prs001-net-${run_suffix}"
data_volume="prs001-data-${run_suffix}"
backup_volume="prs001-backup-${run_suffix}"
restore_volume="prs001-restore-data-${run_suffix}"
prepare_failure_volume="prs001-prepare-fail-data-${run_suffix}"
startup_failure_volume="prs001-startup-fail-data-${run_suffix}"
range_failure_volume="prs001-range-fail-data-${run_suffix}"
work_dir="$(mktemp -d)"
artifact_store="${work_dir}/offhost-store"
passphrase_file="${work_dir}/encryption-passphrase"
export GNUPGHOME="${work_dir}/gnupg"
mkdir -m 700 "${artifact_store}" "${GNUPGHOME}"
python3 - <<'PY' > "${passphrase_file}"
import secrets
print(secrets.token_hex(32))
PY
chmod 600 "${passphrase_file}"
root_password="$(python3 - <<'PY'
import secrets
print(secrets.token_hex(24))
PY
)"

containers=(
	"${primary_container}"
	"${restore_container}"
	"${prepare_failure_container}"
	"${startup_failure_container}"
	"${range_failure_container}"
)
volumes=(
	"${data_volume}"
	"${backup_volume}"
	"${restore_volume}"
	"${prepare_failure_volume}"
	"${startup_failure_volume}"
	"${range_failure_volume}"
)

cleanup() {
	local container volume
	for container in "${containers[@]}"; do
		docker rm --force "${container}" >/dev/null 2>&1 || true
	done
	for volume in "${volumes[@]}"; do
		docker volume rm --force "${volume}" >/dev/null 2>&1 || true
	done
	docker network rm "${network_name}" >/dev/null 2>&1 || true
	if [[ "${PRS001_KEEP_WORKDIR:-0}" == "1" ]]; then
		echo "PRS-001 evidence retained at ${work_dir}" >&2
	else
		rm -rf "${work_dir}"
	fi
}
trap cleanup EXIT

wait_for_mariadb() {
	local container="$1"
	local ready=0
	for _ in $(seq 1 90); do
		if docker exec \
			-e MYSQL_PWD="${root_password}" \
			"${container}" \
			mariadb-admin --protocol=tcp --host=127.0.0.1 --user=root ping --silent >/dev/null 2>&1; then
			ready=1
			break
		fi
		if [[ "$(docker inspect --format '{{.State.Running}}' "${container}" 2>/dev/null || true)" != "true" ]]; then
			break
		fi
		sleep 1
	done
	if [[ ${ready} -ne 1 ]]; then
		echo "ERROR: MariaDB container did not become ready: ${container}" >&2
		docker logs "${container}" >&2 || true
		return 1
	fi
}

mariadb_query() {
	local sql="$1"
	docker exec \
		-e MYSQL_PWD="${root_password}" \
		"${primary_container}" \
		mariadb --protocol=tcp --host=127.0.0.1 --user=root --batch --skip-column-names \
		--execute="${sql}" | tr -d '\r'
}

expect_failure() {
	local label="$1"
	shift
	set +e
	"$@" >"${work_dir}/${label}.stdout" 2>"${work_dir}/${label}.stderr"
	local status=$?
	set -e
	if [[ ${status} -eq 0 ]]; then
		echo "ERROR: expected failure succeeded: ${label}" >&2
		cat "${work_dir}/${label}.stdout" >&2 || true
		cat "${work_dir}/${label}.stderr" >&2 || true
		exit 1
	fi
	echo "Observed expected failure ${label} with exit ${status}."
}

known_good_checksum=""
assert_known_good_unchanged() {
	local current
	current="$(sha256sum "${artifact_store}/known-good/payload.tar.gpg")"
	if [[ "${current}" != "${known_good_checksum}" ]]; then
		echo "ERROR: previous known-good recovery set changed" >&2
		exit 1
	fi
}

run_take_backup() {
	local backup_id="$1"
	local fail_at="${2:-}"
	env \
		PRS001_PRIMARY_CONTAINER="${primary_container}" \
		PRS001_BACKUP_ID="${backup_id}" \
		PRS001_DB_ROOT_PASSWORD="${root_password}" \
		PRS001_FAIL_AT="${fail_at}" \
		bash "${backup_dir}/take-full-backup.sh"
}

run_publish() {
	local backup_id="$1"
	local fail_at="${2:-}"
	env \
		PRS001_PRIMARY_CONTAINER="${primary_container}" \
		PRS001_BACKUP_VOLUME="${backup_volume}" \
		PRS001_BACKUP_ID="${backup_id}" \
		PRS001_DB_ROOT_PASSWORD="${root_password}" \
		PRS001_ARTIFACT_STORE="${artifact_store}" \
		PRS001_ENCRYPTION_PASSPHRASE_FILE="${passphrase_file}" \
		PRS001_MARIADB_IMAGE="${PRS001_MARIADB_IMAGE}" \
		PRS001_MARIADB_VERSION="${PRS001_MARIADB_VERSION}" \
		PRS001_RECOVERY_FORMAT_VERSION="${PRS001_RECOVERY_FORMAT_VERSION}" \
		PRS001_FAIL_AT="${fail_at}" \
		bash "${backup_dir}/publish-recovery-set.sh"
}

run_verify() {
	local recovery_set="$1"
	local output_dir="$2"
	local remove_binlog="${3:-0}"
	env \
		PRS001_RECOVERY_SET="${recovery_set}" \
		PRS001_ENCRYPTION_PASSPHRASE_FILE="${passphrase_file}" \
		PRS001_OUTPUT_DIR="${output_dir}" \
		PRS001_MARIADB_IMAGE="${PRS001_MARIADB_IMAGE}" \
		PRS001_MARIADB_VERSION="${PRS001_MARIADB_VERSION}" \
		PRS001_RECOVERY_FORMAT_VERSION="${PRS001_RECOVERY_FORMAT_VERSION}" \
		PRS001_TEST_REMOVE_BINLOG="${remove_binlog}" \
		bash "${backup_dir}/verify-recovery-set.sh"
}

run_restore() {
	local verified_dir="$1"
	local restore_volume_name="$2"
	local restore_container_name="$3"
	local target_datetime="$4"
	local fail_at="${5:-}"
	env \
		PRS001_VERIFIED_DIR="${verified_dir}" \
		PRS001_RESTORE_VOLUME="${restore_volume_name}" \
		PRS001_RESTORE_CONTAINER="${restore_container_name}" \
		PRS001_NETWORK="${network_name}" \
		PRS001_DB_ROOT_PASSWORD="${root_password}" \
		PRS001_TARGET_DATETIME="${target_datetime}" \
		PRS001_MARIADB_IMAGE="${PRS001_MARIADB_IMAGE}" \
		PRS001_MARIADB_VERSION="${PRS001_MARIADB_VERSION}" \
		PRS001_FAIL_AT="${fail_at}" \
		bash "${backup_dir}/restore-pitr.sh"
}

echo "Pulling pinned MariaDB image ${PRS001_MARIADB_IMAGE}."
docker pull "${PRS001_MARIADB_IMAGE}" >/dev/null
docker network create "${network_name}" >/dev/null
for volume in "${volumes[@]}"; do
	docker volume create "${volume}" >/dev/null
done

docker run --detach \
	--name "${primary_container}" \
	--network "${network_name}" \
	--env TZ=UTC \
	--env MARIADB_ROOT_PASSWORD="${root_password}" \
	--volume "${data_volume}:/var/lib/mysql" \
	--volume "${backup_volume}:/backup" \
	"${PRS001_MARIADB_IMAGE}" \
	--server-id=1 \
	--log-bin=mariadb-bin \
	--binlog-format=ROW \
	--binlog-row-image=FULL \
	--sync-binlog=1 \
	--innodb-flush-log-at-trx-commit=1 \
	--binlog-expire-logs-seconds=1209600 >/dev/null
wait_for_mariadb "${primary_container}"

reported_version="$(mariadb_query 'SELECT VERSION()')"
if [[ "${reported_version}" != "${PRS001_MARIADB_VERSION}"* ]]; then
	echo "ERROR: running MariaDB version does not match the pin: ${reported_version}" >&2
	exit 1
fi
configuration="$(mariadb_query "SELECT CONCAT(@@global.log_bin, '|', @@global.binlog_format, '|', @@global.binlog_row_image, '|', @@global.sync_binlog, '|', @@global.innodb_flush_log_at_trx_commit)")"
if [[ "${configuration}" != "1|ROW|FULL|1|1" ]]; then
	echo "ERROR: durability configuration was not applied: ${configuration}" >&2
	exit 1
fi

mariadb_query "CREATE DATABASE IF NOT EXISTS prs001; CREATE TABLE prs001.events (id INT PRIMARY KEY, marker VARCHAR(64) NOT NULL) ENGINE=InnoDB; INSERT INTO prs001.events VALUES (1, 'base-in-backup');"
run_take_backup known-good >/dev/null
mariadb_query "INSERT INTO prs001.events VALUES (2, 'expected-before-cutoff');"
sleep 2
target_datetime="$(mariadb_query "SELECT DATE_FORMAT(UTC_TIMESTAMP(), '%Y-%m-%d %H:%i:%s')")"
sleep 2
mariadb_query "INSERT INTO prs001.events VALUES (3, 'harmful-after-cutoff');"
run_publish known-good >/dev/null

if grep -F "${root_password}" "${artifact_store}/known-good/manifest.json" >/dev/null; then
	echo "ERROR: recovery manifest leaked the disposable database password" >&2
	exit 1
fi
known_good_checksum="$(sha256sum "${artifact_store}/known-good/payload.tar.gpg")"

verified_success="${work_dir}/verified-success"
run_verify "${artifact_store}/known-good" "${verified_success}" >/dev/null
run_restore "${verified_success}" "${restore_volume}" "${restore_container}" "${target_datetime}" >/dev/null

restored_rows="$(docker exec \
	-e MYSQL_PWD="${root_password}" \
	"${restore_container}" \
	mariadb --protocol=tcp --host=127.0.0.1 --user=root --batch --skip-column-names \
	--execute="SELECT GROUP_CONCAT(CONCAT(id, ':', marker) ORDER BY id SEPARATOR ',') FROM prs001.events" | tr -d '\r')"
if [[ "${restored_rows}" != "1:base-in-backup,2:expected-before-cutoff" ]]; then
	echo "ERROR: PITR result is incorrect: ${restored_rows}" >&2
	exit 1
fi

expect_failure backup-command \
	env PRS001_PRIMARY_CONTAINER="${primary_container}" PRS001_BACKUP_ID="failed-backup" \
	PRS001_DB_ROOT_PASSWORD="${root_password}" PRS001_FAIL_AT=backup \
	bash "${backup_dir}/take-full-backup.sh"
assert_known_good_unchanged

run_take_backup failed-publish >/dev/null
expect_failure artifact-publication \
	env PRS001_PRIMARY_CONTAINER="${primary_container}" PRS001_BACKUP_VOLUME="${backup_volume}" \
	PRS001_BACKUP_ID="failed-publish" PRS001_DB_ROOT_PASSWORD="${root_password}" \
	PRS001_ARTIFACT_STORE="${artifact_store}" PRS001_ENCRYPTION_PASSPHRASE_FILE="${passphrase_file}" \
	PRS001_MARIADB_IMAGE="${PRS001_MARIADB_IMAGE}" PRS001_MARIADB_VERSION="${PRS001_MARIADB_VERSION}" \
	PRS001_RECOVERY_FORMAT_VERSION="${PRS001_RECOVERY_FORMAT_VERSION}" PRS001_FAIL_AT=publish \
	bash "${backup_dir}/publish-recovery-set.sh"
if [[ -e "${artifact_store}/failed-publish" ]]; then
	echo "ERROR: failed publication created a final recovery set" >&2
	exit 1
fi
assert_known_good_unchanged

cp -a "${artifact_store}/known-good" "${artifact_store}/corrupt-checksum"
printf 'corruption' >> "${artifact_store}/corrupt-checksum/payload.tar.gpg"
expect_failure checksum-mismatch run_verify "${artifact_store}/corrupt-checksum" "${work_dir}/verified-corrupt"
assert_known_good_unchanged

expect_failure missing-binlog run_verify "${artifact_store}/known-good" "${work_dir}/verified-missing" 1
assert_known_good_unchanged

verified_prepare_failure="${work_dir}/verified-prepare-failure"
run_verify "${artifact_store}/known-good" "${verified_prepare_failure}" >/dev/null
expect_failure prepare-failure run_restore "${verified_prepare_failure}" "${prepare_failure_volume}" "${prepare_failure_container}" "${target_datetime}" prepare
assert_known_good_unchanged

verified_startup_failure="${work_dir}/verified-startup-failure"
run_verify "${artifact_store}/known-good" "${verified_startup_failure}" >/dev/null
expect_failure startup-failure run_restore "${verified_startup_failure}" "${startup_failure_volume}" "${startup_failure_container}" "${target_datetime}" startup
assert_known_good_unchanged

verified_range_failure="${work_dir}/verified-range-failure"
run_verify "${artifact_store}/known-good" "${verified_range_failure}" >/dev/null
expect_failure target-out-of-range run_restore "${verified_range_failure}" "${range_failure_volume}" "${range_failure_container}" "1970-01-01 00:00:00"
assert_known_good_unchanged

echo "PRS-001 disposable full-backup, encrypted publication, isolated restore, exact-time PITR and failure-injection drill passed."
