from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.otbm_atlas.assets import Appearance, SpriteInfo, SpriteSheet
from tools.otbm_atlas.environment_animation import (
	ANIMATION_ZOOM,
	_candidate_details,
	_geometry,
	_intersects,
	_opaque_composite,
	_phase,
	enrich_environment_animations,
)
from tools.otbm_atlas.semantic import Item


class _FakeRenderer:
	def __init__(self) -> None:
		frame = SpriteInfo(
			pattern_width=1,
			pattern_height=1,
			pattern_depth=1,
			layers=1,
			sprite_ids=(10, 11),
			animation_phases=2,
			default_start_phase=0,
			phase_durations=((100, 100), (100, 100)),
			synchronized=False,
			random_start_phase=False,
			loop_type=0,
			loop_count=0,
		)
		appearance = Appearance(
			appearance_id=100,
			name="extended animated fixture",
			is_ground=False,
			clip=False,
			bottom=False,
			top=False,
			stackable=False,
			splash=False,
			fluid_container=False,
			hangable=False,
			hook_direction=None,
			shift=(3, 5),
			height=2,
			frames=(frame,),
		)
		self.appearances = {100: appearance}
		self.sheets = [SpriteSheet(Path("fixture"), 10, 11, 3)]

	def sprite(self, sprite_id: int):
		value = 80 if sprite_id == 10 else 160
		return 64, 64, bytes((value, value, value, 255)) * 64 * 64


class EnvironmentAnimationTests(unittest.TestCase):
	def test_missing_atlas_is_safe_and_empty(self):
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			self.assertEqual(enrich_environment_animations(root, root), {"instances": 0, "uniqueAnimations": 0, "chunks": 0, "staticFallbacks": 0})

	def test_close_zoom_policy_is_explicit(self):
		self.assertEqual(ANIMATION_ZOOM, 1.5)

	def test_extended_shifted_candidate_keeps_canonical_geometry(self):
		renderer = _FakeRenderer()
		candidate = _candidate_details(renderer, Item(100), 64, 64, 7, False, False)
		self.assertIsNotNone(candidate)
		assert candidate is not None
		self.assertEqual((candidate.width, candidate.height), (64, 64))
		self.assertEqual((candidate.offset_x, candidate.offset_y), (-37, -39))
		self.assertEqual(_geometry(candidate.appearance, 64, 64), (64, 64, -37, -39))
		png = _phase(renderer, candidate.frame, candidate.px, candidate.py, candidate.pz, 1)
		self.assertEqual(png[:8], b"\x89PNG\r\n\x1a\n")
		self.assertEqual((int.from_bytes(png[16:20], "big"), int.from_bytes(png[20:24], "big")), (64, 64))

	def test_composite_requires_full_replacement_coverage(self):
		opaque = bytes((10, 20, 30, 255)) * 4
		transparent = bytes((0, 0, 0, 0)) * 4
		phase = bytes((100, 100, 100, 255)) * 4
		self.assertTrue(_opaque_composite(opaque, transparent, [phase], 2, 2))
		self.assertFalse(_opaque_composite(transparent, transparent, [transparent], 2, 2))

	def test_visual_overlap_is_strict_not_edge_touching(self):
		self.assertTrue(_intersects((0, 0, 64, 64), (32, 32, 96, 96)))
		self.assertFalse(_intersects((0, 0, 32, 32), (32, 0, 64, 32)))


if __name__ == "__main__":
	unittest.main()
