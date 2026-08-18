#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
cd "$ROOT"

LABEL="${ATLAS_ASSET_LABEL:-15.32}"
WORKERS="${ATLAS_WORKERS:-$(nproc)}"
MAP="$ROOT/vendor/map-analysis/crystalserver/data-global/world/world.otbm"
EXPECTED_MAP_SHA="3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034"
ASSETS="${ATLAS_RESUME_ASSETS:-$ROOT/build/atlas-inputs/$LABEL/assets}"
OUTPUT="${ATLAS_RESUME_OUTPUT:-$ROOT/build/full-map-atlas-$LABEL}"
LOG="${ATLAS_RESUME_LOG:-$ROOT/build/logs/atlas-resume-$LABEL.log}"
OLD_RUNNER="$ROOT/build/.atlas-local-runner-$LABEL.py"

mkdir -p "$(dirname "$LOG")"
exec > >(tee -a "$LOG") 2>&1

echo "Atlas partial resume: $LABEL | workers=$WORKERS"
echo "Existing output:      $OUTPUT"
echo "Existing assets:      $ASSETS"
echo "Log:                  $LOG"

if [[ "$(sha256sum "$MAP" | awk '{print $1}')" != "$EXPECTED_MAP_SHA" ]]; then
  echo "ERROR: unexpected canonical world.otbm SHA-256" >&2
  exit 1
fi
if [[ ! -d "$ASSETS" || ! -f "$ASSETS/catalog-content.json" ]]; then
  echo "ERROR: extracted asset corpus is missing: $ASSETS" >&2
  exit 1
fi
if [[ ! -d "$OUTPUT/tiles" || ! -d "$OUTPUT/.spool" ]]; then
  echo "ERROR: partial Atlas detail/spool output is missing: $OUTPUT" >&2
  exit 1
fi

# Refuse concurrent adoption while the old full-build runner is still alive.
if [[ -f "$OLD_RUNNER" ]] && pgrep -f "$(printf '%s' "$OLD_RUNNER" | sed 's/[][\\.^$*+?{}|()]/\\&/g')" >/dev/null 2>&1; then
  echo "ERROR: the old Atlas full-build process is still running." >&2
  echo "Press Ctrl+C in its terminal, wait for the shell prompt, then rerun this command." >&2
  exit 1
fi

DETAIL_COUNT="$(find "$OUTPUT/tiles" -type f -name '*.png' | wc -l)"
OVERVIEW_COUNT="$(find "$OUTPUT/overview" -type f -name '*.png' 2>/dev/null | wc -l)"
LOW_COUNT="$(find "$OUTPUT/overview-low" -type f -name '*.png' 2>/dev/null | wc -l)"
echo "Existing detail:       $DETAIL_COUNT"
echo "Existing overview 4x:  $OVERVIEW_COUNT"
echo "Existing overview 8x:  $LOW_COUNT"

if [[ "$DETAIL_COUNT" != "3494" ]]; then
  echo "ERROR: resume requires the complete 3494-detail phase; found $DETAIL_COUNT" >&2
  exit 1
fi

# Multiprocessing is safe here because -m gives Python an importable real module,
# not stdin. The module independently validates every existing detail PNG/report.
PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" \
  python3 -m tools.otbm_atlas.resume_partial_local \
  "$MAP" "$ASSETS" "$OUTPUT" \
  --repository "$ROOT" \
  --workers "$WORKERS"

echo "Verifying resumed Atlas..."
PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}" \
  python3 -m tools.otbm_atlas.verify "$OUTPUT" --output "$OUTPUT/verification.json"

echo "DONE: $OUTPUT"
echo "LOG:  $LOG"
