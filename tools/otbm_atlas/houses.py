"""Parse canonical house metadata without discarding source provenance."""

from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

FIELDS = {"name", "houseid", "entryx", "entryy", "entryz", "rent", "guildhall", "townid", "size", "clientid", "beds"}
REQUIRED = FIELDS - {"guildhall"}


def parse_houses(path: Path) -> dict[str, object]:
	root = ET.parse(path).getroot()
	if root.tag != "houses": raise ValueError(f"{path}: expected <houses>")
	houses = []
	for entry in root:
		if entry.tag != "house": raise ValueError(f"{path}: unknown <{entry.tag}>")
		unknown = set(entry.attrib) - FIELDS
		if unknown: raise ValueError(f"{path}: unknown house attributes {sorted(unknown)}")
		if not REQUIRED <= set(entry.attrib): raise ValueError(f"{path}: incomplete house")
		houses.append({
			"houseId": int(entry.attrib["houseid"]), "clientId": int(entry.attrib["clientid"]), "name": entry.attrib["name"],
			"entry": {"x": int(entry.attrib["entryx"]), "y": int(entry.attrib["entryy"]), "z": int(entry.attrib["entryz"])},
			"rent": int(entry.attrib["rent"]), "townId": int(entry.attrib["townid"]), "size": int(entry.attrib["size"]),
			"beds": int(entry.attrib["beds"]), "guildhall": entry.attrib.get("guildhall", "false").lower() == "true",
			"source": path.as_posix(), "origin": "base-map",
		})
	return {"schemaVersion": 1, "houses": houses, "statistics": {"houses": len(houses), "guildhalls": sum(bool(house["guildhall"]) for house in houses)}}
