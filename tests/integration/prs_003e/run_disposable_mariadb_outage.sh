#!/usr/bin/env bash
set -euo pipefail

readonly ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
readonly SOURCE_FILE="${ROOT_DIR}/tests/integration/prs_003e/database_outage_injector.cpp"
readonly CONTAINER_NAME="otheryn-prs003e-${GITHUB_RUN_ID:-local}-$$"
readonly DATABASE_NAME="otheryn_prs003e"
readonly BINARY_FILE="$(mktemp "${TMPDIR:-/tmp}/otheryn-prs003e.XXXXXX")"

cleanup() {
	rm -f "${BINARY_FILE}"
	docker rm --force "${CONTAINER_NAME}" >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

command -v docker >/dev/null 2>&1 || {
	echo "docker is required for the disposable PRS-003E-A evidence run" >&2
	exit 1
}
command -v mariadb_config >/dev/null 2>&1 || {
	echo "mariadb_config is required; install the MariaDB Connector/C development package" >&2
	exit 1
}

# This database is disposable, loopback-only and uses no production credential.
docker run --detach --rm \
	--name "${CONTAINER_NAME}" \
	--publish 127.0.0.1::3306 \
	--env MARIADB_ALLOW_EMPTY_ROOT_PASSWORD=1 \
	--env "MARIADB_DATABASE=${DATABASE_NAME}" \
	mariadb:11.4 >/dev/null

for attempt in $(seq 1 60); do
	if docker exec "${CONTAINER_NAME}" healthcheck.sh --connect --innodb_initialized >/dev/null 2>&1; then
		break
	fi
	if [[ "${attempt}" -eq 60 ]]; then
		docker logs "${CONTAINER_NAME}" >&2 || true
		echo "disposable MariaDB did not become ready" >&2
		exit 1
	fi
	sleep 1
done

host_port="$(docker port "${CONTAINER_NAME}" 3306/tcp | awk -F: 'NR == 1 { print $NF }')"
[[ "${host_port}" =~ ^[0-9]+$ ]] || {
	echo "cannot determine disposable MariaDB host port" >&2
	exit 1
}

read -r -a mariadb_cflags <<< "$(mariadb_config --cflags)"
read -r -a mariadb_libs <<< "$(mariadb_config --libs)"

"${CXX:-c++}" \
	-std=c++20 \
	-Wall \
	-Wextra \
	-Wpedantic \
	-Werror \
	-pthread \
	-I"${ROOT_DIR}/src" \
	"${mariadb_cflags[@]}" \
	"${SOURCE_FILE}" \
	-o "${BINARY_FILE}" \
	"${mariadb_libs[@]}"

export PRS003E_DB_HOST=127.0.0.1
export PRS003E_DB_PORT="${host_port}"
export PRS003E_DB_USER=root
export PRS003E_DB_PASSWORD=
export PRS003E_DB_NAME="${DATABASE_NAME}"

"${BINARY_FILE}"
