#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

LABEL="${ATLAS_ASSET_LABEL:-15.32}"
WORKERS="${ATLAS_WORKERS:-$(nproc)}"
FILE_ID="${ATLAS_ASSET_DRIVE_FILE_ID:-1Dlo3bS4K1nS3mw4BhPZdlHT7lX5zRAvv}"
EXPECTED_ZIP_SHA="${ATLAS_ASSET_ZIP_SHA:-1a6bad8b7598cd874f534cd4aae2d249fb3d9b4458b3ccfa75754f91bb27870f}"

MAP="$ROOT/vendor/map-analysis/crystalserver/data-global/world/world.otbm"
EXPECTED_MAP_SHA="3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034"
INPUT_BASE="$ROOT/build/atlas-inputs"
ZIP="$INPUT_BASE/$LABEL.zip"
INPUT_ROOT="$INPUT_BASE/$LABEL"
ASSETS="$INPUT_ROOT/assets"
OUTPUT="$ROOT/build/full-map-atlas-$LABEL"
LOG="$ROOT/build/logs/atlas-$LABEL.log"
URL="https://drive.usercontent.google.com/download?id=${FILE_ID}&export=download&confirm=t"

mkdir -p "$INPUT_BASE" "$ROOT/build/logs"
exec > >(tee -a "$LOG") 2>&1

echo "Atlas build: $LABEL | workers=$WORKERS"

if [[ "$(sha256sum "$MAP" | awk '{print $1}')" != "$EXPECTED_MAP_SHA" ]]; then
  echo "ERROR: unexpected canonical world.otbm SHA-256" >&2
  exit 1
fi

if [[ ! -f "$ZIP" ]]; then
  echo "Downloading assets $LABEL..."
  rm -f "$ZIP.part"
  curl -fL --retry 5 --retry-delay 2 --progress-bar "$URL" -o "$ZIP.part"
  mv "$ZIP.part" "$ZIP"
fi

ACTUAL_ZIP_SHA="$(sha256sum "$ZIP" | awk '{print $1}')"
if [[ "$ACTUAL_ZIP_SHA" != "$EXPECTED_ZIP_SHA" ]]; then
  echo "ERROR: asset ZIP SHA-256 mismatch" >&2
  echo "expected: $EXPECTED_ZIP_SHA" >&2
  echo "actual:   $ACTUAL_ZIP_SHA" >&2
  exit 1
fi

if [[ ! -d "$ASSETS" ]]; then
  echo "Extracting assets $LABEL..."
  unzip -t "$ZIP" >/dev/null
  TMP="$INPUT_BASE/.extract-$LABEL-$$"
  rm -rf "$TMP"
  mkdir -p "$TMP"
  unzip -q "$ZIP" -d "$TMP"
  test -f "$TMP/assets/catalog-content.json"
  rm -rf "$INPUT_ROOT"
  mv "$TMP" "$INPUT_ROOT"
fi

python3 - "$ASSETS" <<'PY'
from pathlib import Path
import json, sys
root = Path(sys.argv[1])
catalog = json.loads((root / "catalog-content.json").read_text(encoding="utf-8"))
if not isinstance(catalog, list):
    raise SystemExit("invalid asset catalog")
missing = [e.get("file") for e in catalog if isinstance(e, dict) and isinstance(e.get("file"), str) and not (root / e["file"]).is_file()]
if missing:
    raise SystemExit(f"missing catalog files: {missing[:5]}")
if len(list(root.glob("appearances-*.dat"))) != 1:
    raise SystemExit("expected exactly one appearances-*.dat")
print(f"Assets OK: {len(catalog)} catalog entries")
PY

echo "Smoke render..."
SMOKE="$ROOT/build/atlas-smoke-$LABEL"
mkdir -p "$SMOKE"
python3 -m tools.otbm_atlas.render \
  "$MAP" "$ASSETS" \
  --bounds 32280 32440 32155 32305 7 \
  --output "$SMOKE/thais.png" \
  --report "$SMOKE/thais-render.json"

echo "Starting full Atlas build..."
python3 - "$MAP" "$ASSETS" "$OUTPUT" "$WORKERS" <<'PY'
from pathlib import Path
import sys
import tools.otbm_atlas.atlas as atlas

repo = Path(".").resolve()
map_path = Path(sys.argv[1]).resolve()
assets = Path(sys.argv[2]).resolve()
output = Path(sys.argv[3]).resolve()
workers = int(sys.argv[4])

atlas.CANONICAL_ASSET_ROOT = assets.relative_to(repo)
manifest = atlas.build_atlas(
    map_path,
    assets,
    output,
    repository_root=repo,
    workers=workers,
    allow_full_build=True,
)
count = len(manifest.get("chunks", []))
if count != 3494:
    raise SystemExit(f"expected 3494 chunks, got {count}")
print(f"Full Atlas build OK: {count} chunks")
PY

echo "Verifying Atlas..."
python3 -m tools.otbm_atlas.verify "$OUTPUT" --output "$OUTPUT/verification.json"

echo "DONE: $OUTPUT"
echo "LOG:  $LOG"
