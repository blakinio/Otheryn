#!/usr/bin/env bash
set -euo pipefail

fetch_verified() {
  local url="$1"
  local expected="$2"
  local destination="$3"
  local tmp
  echo "VERIFYING $destination expected=$expected"
  tmp="$(mktemp)"
  curl --fail --silent --show-error --location "$url" --output "$tmp"
  actual="$(git hash-object "$tmp")"
  echo "HASHED $destination actual=$actual"
  if [[ "$actual" != "$expected" ]]; then
    echo "SHA mismatch for $destination: expected=$expected actual=$actual" >&2
    exit 1
  fi
  mkdir -p "$(dirname "$destination")"
  mv "$tmp" "$destination"
}

PR264=d14d5c992d4095c79672a8469050aa9e103e34bb
PR288=67ac28ee314ccc31671344515633c9411c3fe9df
RAW=https://raw.githubusercontent.com/blakinio/canary

fetch_verified "$RAW/$PR264/src/creatures/players/components/player_achievement.cpp" 998a077b6302233ba81969e904f72ad19d4b4840 src/creatures/players/components/player_achievement.cpp
fetch_verified "$RAW/$PR264/src/creatures/players/components/player_achievement.hpp" c44334cc9993c5a497ea2023d52cdd6d26501914 src/creatures/players/components/player_achievement.hpp
fetch_verified "$RAW/$PR264/tests/unit/players/components/player_achievement_test.cpp" c10d90aa649322520739696507ba8a0ff2d05a06 tests/unit/players/components/player_achievement_test.cpp

fetch_verified "$RAW/$PR288/data/scripts/lib/register_achievements.lua" 25e5b794a41adb84f7c0f7d309283d4fdb971511 data/scripts/lib/register_achievements.lua
fetch_verified "$RAW/$PR288/src/creatures/players/components/weapon_proficiency.cpp" 780d39f0c2cd0002ebd12f11a611212592217976 src/creatures/players/components/weapon_proficiency.cpp
fetch_verified "$RAW/$PR288/src/creatures/players/components/weapon_proficiency.hpp" 1ce80f1789aec6649df9943b24081f0df8f10fb2 src/creatures/players/components/weapon_proficiency.hpp
fetch_verified "$RAW/$PR288/tests/unit/players/components/weapon_proficiency_test.cpp" 756088ca70188226b2bbe96dd44f038fd6afe417 tests/unit/players/components/weapon_proficiency_test.cpp

python3 - <<'PY'
from pathlib import Path
path = Path('tests/unit/players/components/CMakeLists.txt')
text = path.read_text()
if 'player_achievement_test.cpp' not in text:
    text = text.replace('PRIVATE ', 'PRIVATE player_achievement_test.cpp ', 1)
path.write_text(text)
PY

test "$(git hash-object data/scripts/lib/register_achievements.lua)" = 25e5b794a41adb84f7c0f7d309283d4fdb971511
test "$(git hash-object src/creatures/players/components/player_achievement.cpp)" = 998a077b6302233ba81969e904f72ad19d4b4840
test "$(git hash-object src/creatures/players/components/player_achievement.hpp)" = c44334cc9993c5a497ea2023d52cdd6d26501914
test "$(git hash-object tests/unit/players/components/player_achievement_test.cpp)" = c10d90aa649322520739696507ba8a0ff2d05a06
test "$(git hash-object src/creatures/players/components/weapon_proficiency.cpp)" = 780d39f0c2cd0002ebd12f11a611212592217976
test "$(git hash-object src/creatures/players/components/weapon_proficiency.hpp)" = 1ce80f1789aec6649df9943b24081f0df8f10fb2
test "$(git hash-object tests/unit/players/components/weapon_proficiency_test.cpp)" = 756088ca70188226b2bbe96dd44f038fd6afe417

echo "ALL_DONOR_HASHES_VERIFIED"

git config user.name github-actions[bot]
git config user.email 41898282+github-actions[bot]@users.noreply.github.com
git add \
  data/scripts/lib/register_achievements.lua \
  src/creatures/players/components/player_achievement.cpp \
  src/creatures/players/components/player_achievement.hpp \
  src/creatures/players/components/weapon_proficiency.cpp \
  src/creatures/players/components/weapon_proficiency.hpp \
  tests/unit/players/components/player_achievement_test.cpp \
  tests/unit/players/components/weapon_proficiency_test.cpp \
  tests/unit/players/components/CMakeLists.txt

git rm -f -- \
  .github/oam012-materialize.sh \
  .github/workflows/oam012-materialize-donor.yml

if git diff --cached --quiet; then
  echo "No donor or helper-cleanup changes to commit"
  exit 0
fi

git commit -m "chore(oam): materialize exact OAM-012 donor state"
git push origin HEAD:fix/oam-012-achievements-reconciliation
