"""Build bounded viewport overlay shards and a compact factual search index."""
from __future__ import annotations
from collections import defaultdict
import json
from pathlib import Path

POSITION_KEYS={"towns":"temple","houses":"entry"}
SUPPLEMENTAL_SPAWN_KINDS={"monsterSpawns":"supplementalMonsterSpawns","npcSpawns":"supplementalNpcSpawns"}

def _position(kind: str, record: dict) -> dict | None:
	return record.get(POSITION_KEYS.get(kind,"position"))

def _viewer_kind(kind: str, record: dict) -> str:
	if kind in SUPPLEMENTAL_SPAWN_KINDS and record.get("origin") != "base-map":
		return SUPPLEMENTAL_SPAWN_KINDS[kind]
	return kind

def write_spatial_data(output: Path, chunk_size: int, groups: dict[str,list[dict]]) -> dict[str,int]:
	shards: dict[tuple[int,int,int],dict[str,list[dict]]]=defaultdict(lambda:defaultdict(list)); search=[]; seen=set()
	for kind,records in groups.items():
		for record in records:
			position=_position(kind,record)
			if not position: continue
			viewer_kind=_viewer_kind(kind,record)
			key=(int(position["z"]),int(position["x"])//chunk_size,int(position["y"])//chunk_size)
			value={**record,"kind":viewer_kind};shards[key][viewer_kind].append(value)
			label=record.get("name") or record.get("actionId") or record.get("uniqueId") or record.get("houseId")
			if label is not None:
				skey=(viewer_kind,str(label).casefold())
				if skey not in seen:
					seen.add(skey);search.append({"kind":viewer_kind,"label":str(label),"position":position})
	root=output/"data"/"chunks"
	for (z,x,y),content in shards.items():
		path=root/f"z{z}"/f"{x}_{y}.json";path.parent.mkdir(parents=True,exist_ok=True)
		path.write_text(json.dumps({"schemaVersion":1,**content},separators=(",",":"),sort_keys=True)+"\n",encoding="utf-8")
	(output/"data"/"search-index.json").write_text(json.dumps({"schemaVersion":1,"records":sorted(search,key=lambda v:(v["label"].casefold(),v["kind"]))},separators=(",",":"),sort_keys=True)+"\n",encoding="utf-8")
	return {"shards":len(shards),"searchRecords":len(search)}
