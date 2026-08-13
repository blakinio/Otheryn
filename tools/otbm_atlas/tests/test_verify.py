from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.assets import encode_png
from tools.otbm_atlas.verify import verify_atlas


class VerifyTests(unittest.TestCase):
	def test_verifier_checks_png_checksum_dimensions_and_required_data(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory); tile = root / "tiles/z7/1_2.png"; tile.parent.mkdir(parents=True)
			png = encode_png(1, 1, b"\x00\x00\x00\x00"); tile.write_bytes(png)
			overview=root/"overview/z7/1_2.png";overview.parent.mkdir(parents=True);overview.write_bytes(png)
			low=root/"overview-low/z7/1_2.png";low.parent.mkdir(parents=True);low.write_bytes(png)
			chunk = {"path": "tiles/z7/1_2.png", "overviewPath":"overview/z7/1_2.png","overviewChecksum":hashlib.sha256(png).hexdigest(),"overviewImageWidth":1,"overviewImageHeight":1,"lowOverviewPath":"overview-low/z7/1_2.png","lowOverviewChecksum":hashlib.sha256(png).hexdigest(),"lowOverviewImageWidth":1,"lowOverviewImageHeight":1,"z": 7, "checksum": hashlib.sha256(png).hexdigest(), "imageWidth": 1, "imageHeight": 1, "tiles": 1, "groundItems": 0, "childItems": 0, "renderOperations": 0, "missingAppearances": {}, "missingSprites": {}}
			(root / "manifest.json").write_text(json.dumps({"chunks": [chunk]}), encoding="utf-8"); (root / "index.html").write_text("viewer", encoding="utf-8")
			(root / "data").mkdir()
			for name in ("mechanics.json", "mechanics-resolution.json", "spawns.json", "composition.json", "houses.json"): (root / "data" / name).write_text("{}", encoding="utf-8")
			(root/"data/unknown-items.json").write_text(json.dumps({"items":[]}),encoding="utf-8")
			(root/"data/statistics.json").write_text(json.dumps({"chunks":1,"populatedFloors":[7],"tiles":1,"groundItems":0,"childItems":0,"renderOperations":0}),encoding="utf-8")
			self.assertTrue(verify_atlas(root)["ok"])
			tile.write_bytes(png + b"corrupt")
			self.assertIn("checksum mismatch", " ".join(verify_atlas(root)["errors"]))

	def test_verifier_rejects_stale_data_reports(self) -> None:
		with tempfile.TemporaryDirectory() as directory:
			root=Path(directory);(root/"manifest.json").write_text('{"chunks":[]}',encoding="utf-8");(root/"index.html").write_text("viewer",encoding="utf-8");(root/"data").mkdir()
			for name in ("mechanics.json","mechanics-resolution.json","spawns.json","composition.json","houses.json"): (root/"data"/name).write_text("{}",encoding="utf-8")
			(root/"data/unknown-items.json").write_text('{"items":[]}',encoding="utf-8");(root/"data/statistics.json").write_text('{"chunks":99}',encoding="utf-8")
			self.assertIn("disagrees"," ".join(verify_atlas(root)["errors"]))


if __name__ == "__main__": unittest.main()
