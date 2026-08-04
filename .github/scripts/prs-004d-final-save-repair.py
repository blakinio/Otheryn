#!/usr/bin/env python3

from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: prs-004d-final-save-repair.py <save_manager.cpp>")

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")

    old_attempt = """\t\tconst auto attempt = executePlayerCheckpointAttempt(*state, *generation, [this, &player] {
\t\t\treturn doSavePlayer(player, true);
\t\t});"""
    new_attempt = """\t\tconst auto attempt = executePlayerCheckpointAttempt(*state, *generation, [this, &player] {
\t\t\treturn doSavePlayer(player, false);
\t\t});"""
    old_success = """\t\tif (!attempt.followUpRequired && !state->isDirty()) {
\t\t\treturn true;
\t\t}"""
    new_success = """\t\tif (!attempt.followUpRequired && !state->isDirty()) {
\t\t\tif (!releasePlayerWriterFence(player)) {
\t\t\t\tlogger.error("Final save for player {} committed but durable writer-fence release failed.", player->getName());
\t\t\t\treturn false;
\t\t\t}
\t\t\treturn true;
\t\t}"""

    if new_attempt in text and new_success in text:
        return 0

    if text.count(old_attempt) != 1 or text.count(old_success) != 1:
        raise SystemExit("final-save repair markers are neither pristine nor fully repaired")

    path.write_text(
        text.replace(old_attempt, new_attempt, 1).replace(old_success, new_success, 1),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
