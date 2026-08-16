from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.semantic import Item, Position, Tile
from tools.otbm_atlas.tile_inspector import tile_record, write_tile_inspector_data


class TileInspectorTests(unittest.TestCase):
    def test_record_resolves_only_unambiguous_canonical_facts(self) -> None:
        tile = Tile(
            Position(32360, 32230, 7),
            None,
            0,
            Item(100),
            (Item(200), Item(201), Item(202)),
        )
        actions = {
            (32360, 32230, 7, 100): {501},
            (32360, 32230, 7, 202): {502},
        }
        uniques = {
            (32360, 32230, 7, 201): {7001},
            (32360, 32230, 7, 202): {7002},
        }
        record, resolved, ambiguous = tile_record(tile, actions, uniques)
        self.assertEqual(
            record,
            {
                "x": 32360,
                "y": 32230,
                "z": 7,
                "ground": {"serverId": 100, "actionId": 501},
                "items": [
                    {"serverId": 200},
                    {"serverId": 201, "uniqueId": 7001},
                    {"serverId": 202, "actionId": 502, "uniqueId": 7002},
                ],
            },
        )
        self.assertEqual(resolved, 4)
        self.assertEqual(ambiguous, 0)

    def test_duplicate_server_id_omits_ambiguous_attribute(self) -> None:
        tile = Tile(Position(100, 200, 7), None, 0, Item(10), (Item(10),))
        record, resolved, ambiguous = tile_record(
            tile,
            {(100, 200, 7, 10): {55}},
            {},
        )
        self.assertEqual(record["ground"], {"serverId": 10})
        self.assertEqual(record["items"], [{"serverId": 10}])
        self.assertEqual(resolved, 0)
        self.assertEqual(ambiguous, 2)

    def test_writer_is_chunk_bounded_deterministic_and_preserves_exact_ground_stack(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spool = root / ".spool"
            sidecar = spool / "tile-facts/z7/1_1.jsonl"
            sidecar.parent.mkdir(parents=True)
            (spool / "spool.json").write_text(
                json.dumps({"version": 1, "chunkSize": 128, "tiles": 2}),
                encoding="utf-8",
            )
            records = [
                {
                    "x": 150,
                    "y": 151,
                    "z": 7,
                    "ground": {"serverId": 100},
                    "items": [{"serverId": 200}],
                },
                {
                    "x": 151,
                    "y": 151,
                    "z": 7,
                    "ground": None,
                    "items": [{"serverId": 201, "actionId": 42}],
                },
            ]
            sidecar.write_text(
                "".join(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n" for record in records),
                encoding="utf-8",
            )

            first = write_tile_inspector_data(root)
            shard = root / "data/tile-inspector/z7/1_1.json"
            before = shard.read_bytes()
            second = write_tile_inspector_data(root)
            self.assertEqual(first, second)
            self.assertEqual(before, shard.read_bytes())
            payload = json.loads(shard.read_text(encoding="utf-8"))
            self.assertEqual(payload["schemaVersion"], 1)
            self.assertEqual(len(payload["records"]), 2)
            self.assertIsNone(payload["records"][1]["ground"])
            self.assertEqual(payload["records"][1]["items"][0]["actionId"], 42)
            self.assertEqual(first["shards"], 1)
            self.assertEqual(first["tiles"], 2)
            self.assertEqual(first["topLevelStackItems"], 2)
            self.assertEqual(first["attributesResolved"], 1)
            self.assertEqual(first["attributesAmbiguousOmitted"], 0)
            index = json.loads((root / "data/tile-inspector/index.json").read_text(encoding="utf-8"))
            self.assertEqual(index["statistics"], first)
            self.assertEqual(index["chunkSize"], 128)
            self.assertIn("raw OTBM server IDs", index["policy"]["identity"])
            self.assertIn("ambiguous attributes are omitted", index["policy"]["attributes"])

    def test_writer_refuses_legacy_spool_without_exact_sidecars(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            spool = root / ".spool"
            spool.mkdir(parents=True)
            (spool / "spool.json").write_text(
                json.dumps({"version": 1, "chunkSize": 128, "tiles": 0}),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "sidecars are missing"):
                write_tile_inspector_data(root)


if __name__ == "__main__":
    unittest.main()
