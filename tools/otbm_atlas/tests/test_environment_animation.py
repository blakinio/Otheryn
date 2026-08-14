from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from tools.otbm_atlas.assets import Appearance, SpriteInfo, SpriteSheet
from tools.otbm_atlas.environment_animation import (
	ANIMATION_ZOOM,
	_candidate,
	_draw_offset,
	_runtime_replacement_safe,
	enrich_environment_animations,
)
from tools.otbm_atlas.semantic import Item


def _appearance(frame: SpriteInfo, *, shift=None, height=None) -> Appearance:
	return Appearance(
		appearance_id=200,
		name="animated fixture",
		is_ground=False,
		clip=False,
		bottom=False,
		top=False,
		stackable=False,
		splash=False,
		fluid_container=False,
		hangable=False,
		hook_direction=None,
		shift=shift,
		height=height,
		frames=(frame,),
	)


class EnvironmentAnimationTests(unittest.TestCase):
	def test_missing_atlas_is_safe_and_empty(self):
		with tempfile.TemporaryDirectory() as directory:
			root = Path(directory)
			self.assertEqual(
				enrich_environment_animations(root, root),
				{"instances": 0, "uniqueAnimations": 0, "chunks": 0, "staticFallbacks": 0},
			)

	def test_close_zoom_policy_is_explicit(self):
		self.assertEqual(ANIMATION_ZOOM, 1.5)

	def test_candidate_keeps_native_large_geometry_and_displacement(self):
		frame = SpriteInfo(
			pattern_width=1,
			pattern_height=1,
			pattern_depth=1,
			layers=1,
			sprite_ids=(1, 2),
			animation_phases=2,
			default_start_phase=0,
			phase_durations=((100, 100), (120, 120)),
			synchronized=True,
			random_start_phase=False,
			loop_type=0,
			loop_count=0,
		)
		appearance = _appearance(frame, shift=(3, 4), height=2)
		renderer = SimpleNamespace(
			appearances={200: appearance},
			sheets=[SpriteSheet(Path("fixture.lzma"), 1, 2, 2)],  # layout 2 = 64x32
		)
		candidate = _candidate(renderer, Item(200), 100, 100, 7, False, False)
		self.assertIsNotNone(candidate)
		assert candidate is not None
		self.assertEqual(candidate[5:9], (64, 32, -37, -6))
		self.assertEqual(_draw_offset(appearance, 64, 32), (-37, -6))

	def test_replacement_proof_rejects_default_phase_leak(self):
		transparent = bytes((0, 0, 0, 0))
		red = bytes((255, 0, 0, 255))
		blue = bytes((0, 0, 255, 255))
		green = bytes((0, 255, 0, 255))
		self.assertFalse(
			_runtime_replacement_safe(1, 1, transparent, [red, transparent], transparent, 0)
		)
		self.assertTrue(
			_runtime_replacement_safe(1, 1, green, [red, transparent], transparent, 0)
		)
		self.assertTrue(
			_runtime_replacement_safe(1, 1, transparent, [red, blue], transparent, 0)
		)


if __name__ == "__main__":
	unittest.main()
