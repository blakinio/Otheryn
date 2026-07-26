#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

script_path = Path("tools/ai-agent/oam_051a_materialize.py")
source = script_path.read_text(encoding="utf-8")
old = '''patch_path = Path("/tmp/oam-051a-selected.patch")
patch = subprocess.run(
    ["git", "diff", "--binary", parent, donor, "--", *SELECTED_DONOR_PATHS],
    check=True,
    stdout=subprocess.PIPE,
).stdout
patch_path.write_bytes(patch)
run("git", "apply", "--3way", str(patch_path))
'''
new = '''non_player_paths = [path for path in SELECTED_DONOR_PATHS if not path.endswith("player_wheel.cpp")]
patch_path = Path("/tmp/oam-051a-selected.patch")
patch = subprocess.run(
    ["git", "diff", "--binary", parent, donor, "--", *non_player_paths],
    check=True,
    stdout=subprocess.PIPE,
).stdout
patch_path.write_bytes(patch)
run("git", "apply", "--3way", str(patch_path))

player_patch_path = Path("/tmp/oam-051a-player-wheel.patch")
player_patch = subprocess.run(
    ["git", "diff", "--binary", parent, donor, "--", "src/creatures/players/components/wheel/player_wheel.cpp"],
    check=True,
    stdout=subprocess.PIPE,
).stdout
player_patch_path.write_bytes(player_patch)
player_apply = subprocess.run(
    ["git", "apply", "--reject", "--whitespace=nowarn", str(player_patch_path)],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)
print(player_apply.stdout, end="")
if player_apply.returncode != 0:
    rejects = sorted(Path(".").rglob("*.rej"))
    for reject in rejects:
        print(f"--- REJECT {reject} ---")
        print(reject.read_text(encoding="utf-8"))
    raise RuntimeError(f"player_wheel.cpp selective patch left {len(rejects)} rejected hunks")
'''
if source.count(old) != 1:
    raise RuntimeError(f"expected one materializer patch anchor, found {source.count(old)}")
modified = source.replace(old, new, 1)
exec(compile(modified, str(script_path), "exec"), {"__name__": "__main__", "__file__": str(script_path)})
