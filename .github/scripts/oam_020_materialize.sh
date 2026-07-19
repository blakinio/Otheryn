#!/usr/bin/env bash
set -euo pipefail

TARGET_BASE="63547f30fc21e495217b8a92fa44aaad2db188ef"
LEGACY_BASE="c353b89b5a7f783cf4ee22fe1ba91850de837a68"
EXPECTED_BRANCH="dudantas/oam-020-exaltation-forge-adapt"

current_branch="$(git branch --show-current)"
if [[ "${current_branch}" != "${EXPECTED_BRANCH}" ]]; then
  echo "Refusing to materialize on unexpected branch: ${current_branch}" >&2
  exit 1
fi

if ! git merge-base --is-ancestor "${TARGET_BASE}" HEAD; then
  echo "Target branch does not descend from pinned OAM-020 target base ${TARGET_BASE}" >&2
  exit 1
fi

mapfile -t bootstrap_changes < <(git diff --name-only "${TARGET_BASE}" HEAD)
for path in "${bootstrap_changes[@]}"; do
  case "${path}" in
    .github/scripts/oam_020_materialize.sh|.github/workflows/oam-020-materialize.yml) ;;
    *)
      echo "Unexpected pre-materialization target change: ${path}" >&2
      exit 1
      ;;
  esac
done

if git remote get-url legacy-oam020 >/dev/null 2>&1; then
  git remote remove legacy-oam020
fi
git remote add legacy-oam020 https://github.com/blakinio/canary.git
git fetch --no-tags legacy-oam020 "${LEGACY_BASE}:refs/remotes/legacy-oam020/oam-020-baseline"

resolved_legacy="$(git rev-parse refs/remotes/legacy-oam020/oam-020-baseline)"
if [[ "${resolved_legacy}" != "${LEGACY_BASE}" ]]; then
  echo "Legacy baseline mismatch: expected ${LEGACY_BASE}, got ${resolved_legacy}" >&2
  exit 1
fi

DONORS=(
  209289d38e64aafe7ce3e036867bb632cd0363b8
  84f5c09263f459d726fbc7b9f79557b2cbb0801d
  f1d217c43e8e302978f533212e6aa9d1ce2b77c8
  94f8a3b63271b3708e33496e937620a6cd4b9717
  e16c9f769b1bcdd05e1719e861f0a52cc2594560
  444aa8ae13edc01c6e77b03139a43d386b437308
  ded1830b143388d65c895ad30918faf128df66ed
  7771bbec22d970d9779bff740e3f7f2e0df42f19
  82348f9faca788a8cbb5c13feb75b4e06d8da9dc
)

for commit in "${DONORS[@]}"; do
  if ! git merge-base --is-ancestor "${commit}" "${LEGACY_BASE}"; then
    echo "Donor ${commit} is not contained in pinned legacy baseline ${LEGACY_BASE}" >&2
    exit 1
  fi
done

mapfile -t ORDERED_DONORS < <(
  for commit in "${DONORS[@]}"; do
    printf '%s %s\n' "$(git show -s --format=%ct "${commit}")" "${commit}"
  done | sort -n | awk '{print $2}'
)

apply_donor_paths() {
  local commit="$1"
  shift
  local patch_file
  patch_file="$(mktemp)"
  git diff --binary "${commit}^1" "${commit}" -- "$@" > "${patch_file}"
  if [[ ! -s "${patch_file}" ]]; then
    echo "Expected bounded donor patch is empty for ${commit}" >&2
    rm -f "${patch_file}"
    exit 1
  fi
  echo "Applying donor ${commit}: $*"
  if ! git apply --3way --index "${patch_file}"; then
    echo "Failed exact three-way application for donor ${commit}" >&2
    rm -f "${patch_file}"
    exit 1
  fi
  rm -f "${patch_file}"
}

for commit in "${ORDERED_DONORS[@]}"; do
  case "${commit}" in
    209289d38e64aafe7ce3e036867bb632cd0363b8)
      apply_donor_paths "${commit}" \
        src/creatures/players/player.cpp \
        src/game/functions/forge_transfer_policy.hpp \
        src/server/network/protocol/protocolgame.cpp \
        tests/integration/game/forge_it.cpp \
        tests/unit/players/forge_test.cpp
      ;;
    84f5c09263f459d726fbc7b9f79557b2cbb0801d)
      apply_donor_paths "${commit}" \
        src/creatures/players/components/player_forge_history.hpp \
        src/creatures/players/player.cpp
      ;;
    f1d217c43e8e302978f533212e6aa9d1ce2b77c8)
      apply_donor_paths "${commit}" data/libs/systems/exaltation_forge.lua
      ;;
    94f8a3b63271b3708e33496e937620a6cd4b9717)
      apply_donor_paths "${commit}" \
        src/creatures/players/player.cpp \
        src/game/functions/forge_fusion_policy.hpp \
        src/game/functions/forge_transfer_policy.hpp \
        tests/integration/game/forge_it.cpp \
        tests/unit/players/forge_test.cpp
      ;;
    e16c9f769b1bcdd05e1719e861f0a52cc2594560)
      apply_donor_paths "${commit}" \
        src/creatures/players/player.cpp \
        src/game/functions/forge_transaction.hpp \
        tests/integration/game/forge_it.cpp \
        tests/unit/players/CMakeLists.txt \
        tests/unit/players/forge_transaction_test.cpp
      ;;
    444aa8ae13edc01c6e77b03139a43d386b437308)
      apply_donor_paths "${commit}" \
        config.lua.dist \
        data/libs/systems/exaltation_forge.lua \
        src/config/configmanager.cpp \
        src/config/forge_config_defaults.hpp \
        tests/unit/game/CMakeLists.txt \
        tests/unit/game/forge_config_test.cpp
      ;;
    ded1830b143388d65c895ad30918faf128df66ed)
      apply_donor_paths "${commit}" \
        data/libs/systems/exaltation_forge.lua \
        docs/lua-api/lua_api.json \
        src/lua/functions/creatures/player/player_functions.cpp \
        src/lua/functions/creatures/player/player_functions.hpp \
        tests/lua/test_exaltation_forge_premium.lua
      ;;
    7771bbec22d970d9779bff740e3f7f2e0df42f19)
      apply_donor_paths "${commit}" \
        src/creatures/players/player.cpp \
        src/game/functions/forge_effect_policy.hpp \
        tests/unit/players/CMakeLists.txt \
        tests/unit/players/forge_effect_policy_test.cpp
      ;;
    82348f9faca788a8cbb5c13feb75b4e06d8da9dc)
      apply_donor_paths "${commit}" \
        src/creatures/players/player.cpp \
        tests/integration/game/forge_it.cpp
      ;;
    *)
      echo "Unexpected donor in ordered set: ${commit}" >&2
      exit 1
      ;;
  esac
done

git diff --cached --check

allowed_paths=(
  config.lua.dist
  data/libs/systems/exaltation_forge.lua
  docs/lua-api/lua_api.json
  src/config/configmanager.cpp
  src/config/forge_config_defaults.hpp
  src/creatures/players/components/player_forge_history.hpp
  src/creatures/players/player.cpp
  src/game/functions/forge_effect_policy.hpp
  src/game/functions/forge_fusion_policy.hpp
  src/game/functions/forge_transaction.hpp
  src/game/functions/forge_transfer_policy.hpp
  src/lua/functions/creatures/player/player_functions.cpp
  src/lua/functions/creatures/player/player_functions.hpp
  src/server/network/protocol/protocolgame.cpp
  tests/integration/game/forge_it.cpp
  tests/lua/test_exaltation_forge_premium.lua
  tests/unit/game/CMakeLists.txt
  tests/unit/game/forge_config_test.cpp
  tests/unit/players/CMakeLists.txt
  tests/unit/players/forge_effect_policy_test.cpp
  tests/unit/players/forge_test.cpp
  tests/unit/players/forge_transaction_test.cpp
)

is_allowed() {
  local candidate="$1"
  local allowed
  for allowed in "${allowed_paths[@]}"; do
    if [[ "${candidate}" == "${allowed}" ]]; then
      return 0
    fi
  done
  return 1
}

mapfile -t staged_paths < <(git diff --cached --name-only)
if [[ "${#staged_paths[@]}" -eq 0 ]]; then
  echo "Materializer produced no target changes" >&2
  exit 1
fi
for path in "${staged_paths[@]}"; do
  if ! is_allowed "${path}"; then
    echo "Materializer staged non-allowlisted path: ${path}" >&2
    exit 1
  fi
done

git rm .github/scripts/oam_020_materialize.sh .github/workflows/oam-020-materialize.yml

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git commit -m "fix(forge): adapt OAM-020 validated behavior"

mapfile -t final_paths < <(git diff --name-only "${TARGET_BASE}" HEAD)
if [[ "${#final_paths[@]}" -eq 0 ]]; then
  echo "Final target diff is empty" >&2
  exit 1
fi
for path in "${final_paths[@]}"; do
  if ! is_allowed "${path}"; then
    echo "Final target diff contains non-allowlisted path: ${path}" >&2
    exit 1
  fi
done

git diff --check "${TARGET_BASE}"..HEAD
git push origin "HEAD:${EXPECTED_BRANCH}"
