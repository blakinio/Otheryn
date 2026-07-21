#!/usr/bin/env python3
from pathlib import Path

replacements = {
    Path("data/scripts/lib/register_bestiary_charm.lua"): [
        (
            "registerCharm.category = function(charm, mask)\n\tif mask.type then\n\t\tcharm:category(mask.category)\n\tend\nend",
            "registerCharm.category = function(charm, mask)\n\tif mask.category then\n\t\tcharm:category(mask.category)\n\tend\nend",
        ),
    ],
    Path("src/io/iobestiary.cpp"): [
        (
            "100000 + (playerLevel > 100 ? playerLevel * 11000 : 0)",
            "100000 + (playerLevel > 100 ? (playerLevel - 100) * 11000 : 0)",
        ),
    ],
}

for path, path_replacements in replacements.items():
    text = path.read_text(encoding="utf-8")
    for old, new in path_replacements:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{path}: expected exactly one match, found {count}: {old!r}")
        text = text.replace(old, new, 1)
    path.write_text(text, encoding="utf-8")
