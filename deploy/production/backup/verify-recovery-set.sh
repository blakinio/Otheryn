#!/usr/bin/env bash
set -Eeuo pipefail

require_env() {
	local name="$1"
	if [[ -z "${!name:-}" ]]; then
		echo "ERROR: required environment variable ${name} is not set" >&2
		exit 64
	fi
}

for command_name in gpg python3 sha256sum tar; do
	if ! command -v "${command_name}" >/dev/null 2>&1; then
		echo "ERROR: required command is unavailable: ${command_name}" >&2
		exit 69
	fi
done

require_env PRS001_RECOVERY_SET
require_env PRS001_ENCRYPTION_PASSPHRASE_FILE
require_env PRS001_OUTPUT_DIR
require_env PRS001_MARIADB_IMAGE
require_env PRS001_MARIADB_VERSION
require_env PRS001_RECOVERY_FORMAT_VERSION

if [[ ! -d "${PRS001_RECOVERY_SET}" ]]; then
	echo "ERROR: recovery set directory does not exist" >&2
	exit 66
fi
if [[ ! -s "${PRS001_ENCRYPTION_PASSPHRASE_FILE}" ]]; then
	echo "ERROR: encryption passphrase file is missing or empty" >&2
	exit 66
fi
if [[ -e "${PRS001_OUTPUT_DIR}" ]]; then
	echo "ERROR: verification output already exists and will not be replaced" >&2
	exit 65
fi

recovery_set="$(cd "${PRS001_RECOVERY_SET}" && pwd -P)"
output_parent="$(dirname "${PRS001_OUTPUT_DIR}")"
mkdir -p "${output_parent}"
output_parent="$(cd "${output_parent}" && pwd -P)"
output_dir="${output_parent}/$(basename "${PRS001_OUTPUT_DIR}")"
work_dir="$(mktemp -d)"
staged_output="${output_dir}.tmp-$$"
cleanup() {
	rm -rf "${work_dir}"
	if [[ -d "${staged_output}" ]]; then
		rm -rf "${staged_output}"
	fi
}
trap cleanup EXIT

for required_file in manifest.json payload.tar.gpg SHA256SUMS; do
	if [[ ! -s "${recovery_set}/${required_file}" ]]; then
		echo "ERROR: recovery set is missing ${required_file}" >&2
		exit 72
	fi
done

(
	cd "${recovery_set}"
	sha256sum --check SHA256SUMS
)

python3 - \
	"${recovery_set}/manifest.json" \
	"${PRS001_RECOVERY_FORMAT_VERSION}" \
	"${PRS001_MARIADB_IMAGE}" \
	"${PRS001_MARIADB_VERSION}" <<'PY'
import json
import re
import sys
from datetime import datetime
from pathlib import Path

manifest_path, expected_format, expected_image, expected_version = sys.argv[1:]
manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
required = {
    "format_version",
    "backup_id",
    "mariadb_image",
    "mariadb_version_expected",
    "mariadb_version_reported",
    "backup_started_at",
    "backup_completed_at",
    "archive_completed_at",
    "backup_binlog_file",
    "backup_binlog_position",
    "first_archived_binlog",
    "last_archived_binlog",
    "incremental_backup",
    "payload_encryption",
}
if set(manifest) != required:
    raise SystemExit("manifest fields do not match the recovery-set contract")
if manifest["format_version"] != int(expected_format):
    raise SystemExit("unexpected recovery-set format")
if manifest["mariadb_image"] != expected_image:
    raise SystemExit("manifest image does not match the pinned image")
if manifest["mariadb_version_expected"] != expected_version:
    raise SystemExit("manifest version does not match the pinned version")
if not str(manifest["mariadb_version_reported"]).startswith(expected_version):
    raise SystemExit("running MariaDB version does not match the pinned version")
if manifest["incremental_backup"] is not False:
    raise SystemExit("incremental backup is not accepted in PRS-001 first release")
if manifest["payload_encryption"] != "gpg-symmetric-aes256":
    raise SystemExit("unexpected payload encryption")
if not re.fullmatch(r"[A-Za-z0-9._-]+", str(manifest["backup_id"])):
    raise SystemExit("invalid backup identifier")
if not re.fullmatch(r"mariadb-bin\.[0-9]+", str(manifest["backup_binlog_file"])):
    raise SystemExit("invalid backup binlog filename")
if not isinstance(manifest["backup_binlog_position"], int) or manifest["backup_binlog_position"] < 4:
    raise SystemExit("invalid backup binlog position")
if not (manifest["first_archived_binlog"] <= manifest["backup_binlog_file"] <= manifest["last_archived_binlog"]):
    raise SystemExit("backup coordinate is outside the archived binlog range")

def parse_utc(value: object) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise SystemExit("manifest timestamp is not UTC")
    return datetime.fromisoformat(value[:-1] + "+00:00")

started = parse_utc(manifest["backup_started_at"])
completed = parse_utc(manifest["backup_completed_at"])
archived = parse_utc(manifest["archive_completed_at"])
if not started <= completed <= archived:
    raise SystemExit("manifest timestamps are not monotonic")

for key in manifest:
    lowered = key.casefold()
    if any(token in lowered for token in ("password", "passphrase", "secret", "token", "private_key")):
        raise SystemExit("manifest contains a forbidden secret-shaped field")
PY

gpg --batch --yes --pinentry-mode loopback \
	--passphrase-file "${PRS001_ENCRYPTION_PASSPHRASE_FILE}" \
	--decrypt \
	--output "${work_dir}/envelope.tar" \
	"${recovery_set}/payload.tar.gpg"

tar -tf "${work_dir}/envelope.tar" > "${work_dir}/envelope-files.txt"
python3 - "${work_dir}/envelope-files.txt" <<'PY'
import sys
from pathlib import Path

entries = {line.strip().lstrip("./") for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()}
if entries != {"payload.tar", "FILES.sha256"}:
    raise SystemExit("encrypted envelope contains unexpected paths")
PY

mkdir -m 700 "${work_dir}/envelope"
tar -xf "${work_dir}/envelope.tar" -C "${work_dir}/envelope"
tar -tf "${work_dir}/envelope/payload.tar" > "${work_dir}/payload-files.txt"
python3 - "${work_dir}/payload-files.txt" <<'PY'
import sys
from pathlib import PurePosixPath, Path

entries = [line.strip() for line in Path(sys.argv[1]).read_text().splitlines() if line.strip()]
if not entries:
    raise SystemExit("payload archive is empty")
for entry in entries:
    path = PurePosixPath(entry)
    if path.is_absolute() or ".." in path.parts:
        raise SystemExit("payload archive contains an unsafe path")
    if path.parts[0] not in {"full", "binlogs"}:
        raise SystemExit("payload archive contains an unexpected top-level path")
PY

mkdir -m 700 "${staged_output}"
tar -xf "${work_dir}/envelope/payload.tar" -C "${staged_output}"

if [[ "${PRS001_TEST_REMOVE_BINLOG:-0}" == "1" ]]; then
	injected_binlog="$(find "${staged_output}/binlogs" -maxdepth 1 -type f -name 'mariadb-bin.[0-9]*' | sort | head -n 1)"
	if [[ -z "${injected_binlog}" ]]; then
		echo "ERROR: missing-binlog injection found no binlog" >&2
		exit 72
	fi
	rm -f "${injected_binlog}"
fi

(
	cd "${staged_output}"
	sha256sum --check "${work_dir}/envelope/FILES.sha256"
)
cp "${recovery_set}/manifest.json" "${staged_output}/manifest.json"
cp "${work_dir}/envelope/FILES.sha256" "${staged_output}/FILES.sha256"
mv "${staged_output}" "${output_dir}"

echo "${output_dir}"
