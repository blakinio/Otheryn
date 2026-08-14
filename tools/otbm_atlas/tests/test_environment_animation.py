from __future__ import annotations
import tempfile,unittest
from pathlib import Path
from tools.otbm_atlas.environment_animation import ANIMATION_ZOOM,enrich_environment_animations

class EnvironmentAnimationTests(unittest.TestCase):
	def test_missing_atlas_is_safe_and_empty(self):
		with tempfile.TemporaryDirectory() as directory:
			root=Path(directory)
			self.assertEqual(enrich_environment_animations(root,root),{"instances":0,"uniqueAnimations":0,"chunks":0,"staticFallbacks":0})
	def test_close_zoom_policy_is_explicit(self):
		self.assertEqual(ANIMATION_ZOOM,1.5)

if __name__=="__main__":unittest.main()
