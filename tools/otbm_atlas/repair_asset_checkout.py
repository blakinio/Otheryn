"""Safely repair legacy CRLF materialization of canonical Atlas assets."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile


PROFICIENCIES_ASSET = Path("vendor/map-analysis/tibia-client/15.25.bd5a04/assets/proficiencies-1a915dffd9265cd1c18d39e55da7ede691b2e58add534bc186238ae028a73f22.json")


def repair_crlf_asset(repository: Path, relative: Path) -> bool:
	"""Restore a tracked blob only when its sole worktree delta is CRLF."""
	repository = repository.resolve()
	path = repository / relative
	blob = subprocess.run(
		["git", "show", f"HEAD:{relative.as_posix()}"],
		cwd=repository,
		check=True,
		capture_output=True,
	).stdout
	local = path.read_bytes()
	if local == blob:
		return False
	if b"\r\n" not in local or local.replace(b"\r\n", b"\n") != blob:
		raise ValueError(f"refusing to replace non-CRLF asset difference: {relative.as_posix()}")
	with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
		temporary = Path(handle.name)
		handle.write(blob)
	try:
		os.chmod(temporary, path.stat().st_mode)
		os.replace(temporary, path)
	except BaseException:
		temporary.unlink(missing_ok=True)
		raise
	return True


def main() -> None:
	repository = Path(__file__).parents[2]
	repaired = repair_crlf_asset(repository, PROFICIENCIES_ASSET)
	print("repaired canonical asset bytes" if repaired else "canonical asset bytes already present")


if __name__ == "__main__":
	main()
