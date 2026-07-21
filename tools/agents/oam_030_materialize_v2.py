#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src/io/io_bosstiary.cpp"
CMAKE = ROOT / "tests/unit/game/CMakeLists.txt"
TEST = ROOT / "tests/unit/game/oam_030_bosstiary_adapt_test.cpp"
DOC = ROOT / "docs/oam-030-bosstiary-adapt.md"
TASK = ROOT / "docs/agents/tasks/active/OTH-20260721-oam030-bosstiary-adapt.md"

lines = SOURCE.read_text(encoding="utf-8").splitlines()
result_index = next(i for i, line in enumerate(lines) if "DBResult_ptr result = database.storeQuery(query);" in line)
if "if (!result)" not in lines[result_index + 1] or "Failed to detect boosted boss database. (CODE 01)" not in lines[result_index + 2]:
    raise SystemExit("OAM-030 early-return anchor mismatch")
del lines[result_index + 1:result_index + 5]
missing_index = next(i for i in range(result_index + 1, len(lines)) if lines[i].strip() == "if (!result) {")
if "No boosted boss found in g_database(). A new one will be selected." not in lines[missing_index + 1] or lines[missing_index + 2].strip() != "} else {":
    raise SystemExit("OAM-030 missing-row anchor mismatch")
replacement = [
    "\tif (!result) {",
    "\t\tg_logger().warn(\"[{}] No boosted boss row found. A new one will be selected.\", __FUNCTION__);",
    "\t\tif (!database.executeQuery(\"INSERT INTO `boosted_boss` (`boostname`, `date`, `raceid`) VALUES ('default', '0', '0')\")) {",
    "\t\t\tg_logger().error(\"[{}] Failed to initialize the boosted boss database row. (CODE 01)\", __FUNCTION__);",
    "\t\t\treturn;",
    "\t\t}",
    "\t} else {",
]
lines[missing_index:missing_index + 3] = replacement
SOURCE.write_text("\n".join(lines) + "\n", encoding="utf-8")

legacy = (ROOT / "tools/agents/oam_030_materialize.py").read_text(encoding="utf-8")
marker = "cmake = CMAKE.read_text"
if marker not in legacy:
    raise SystemExit("OAM-030 materializer tail anchor missing")
tail = marker + legacy.split(marker, 1)[1]
exec(tail, globals())
