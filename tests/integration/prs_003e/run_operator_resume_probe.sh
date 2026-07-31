#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
build_dir="$(mktemp -d)"
trap 'rm -rf "${build_dir}"' EXIT

cd "${repo_root}"

python3 - <<'PY'
from pathlib import Path

header = Path("src/database/database_outage_operator_control.hpp").read_text(encoding="utf-8")
probe = Path("tests/integration/prs_003e/operator_resume_probe.cpp").read_text(encoding="utf-8")

assert header.count("stateOwner_.operatorResume(") == 1, "operator API must invoke the state owner exactly once"
assert "DatabaseOutageOperatorAction::ResumeGameLifecycle" in header, "applied result must expose the lifecycle action"
assert "request.authorized" in header, "operator authorization precondition is missing"
assert "request.explicitlyConfirmed" in header, "explicit confirmation precondition is missing"
assert "expectedTransitionCount" in header, "transition-generation precondition is missing"
assert "expectedLastEventSequence" in header, "event-generation precondition is missing"
assert "recoveryEvidenceAccepted" in header, "accepted recovery-evidence precondition is missing"

for forbidden in (
    "mysql_",
    "MYSQL_OPT_RECONNECT",
    "Game::setGameState",
    "g_game",
    "executeQuery",
    "storeQuery",
    "retryQuery",
):
    assert forbidden not in header, f"operator policy API must not own production transport or database work: {forbidden}"

assert "proveConcurrentExactOnceResume" in probe, "concurrent exact-once evidence is missing"
assert "RejectedRecoveryEvidence" in probe, "evidence invalidation rejection is missing"
assert "ResumeGameLifecycle" in probe, "lifecycle action evidence is missing"
PY

compiler="${CXX:-g++}"
"${compiler}" \
	-std=c++20 \
	-Wall \
	-Wextra \
	-Wpedantic \
	-Werror \
	-pthread \
	-I"${repo_root}/src" \
	"${repo_root}/tests/integration/prs_003e/operator_resume_probe.cpp" \
	-o "${build_dir}/operator_resume_probe"

for iteration in $(seq 1 20); do
	timeout 10s "${build_dir}/operator_resume_probe" >/dev/null
 done

"${build_dir}/operator_resume_probe"
