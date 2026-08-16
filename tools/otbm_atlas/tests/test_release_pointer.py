from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.otbm_atlas.release_pointer import promote, rollback


class ReleasePointerTests(unittest.TestCase):
    def make_release(self, root: Path, name: str) -> Path:
        release = root / "releases" / name
        release.mkdir(parents=True)
        (release / "manifest.json").write_text('{}\n', encoding="utf-8")
        (release / "index.html").write_text('<!doctype html>\n', encoding="utf-8")
        return release

    def test_promote_then_rollback_keeps_versioned_releases(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_release(root, "one")
            self.make_release(root, "two")
            first = promote(root, "one")
            second = promote(root, "two")
            self.assertEqual(first["current"], "releases/one")
            self.assertEqual(second["current"], "releases/two")
            self.assertEqual(second["previous"], "releases/one")
            self.assertEqual((root / "current").readlink().as_posix(), "releases/two")
            restored = rollback(root)
            self.assertEqual(restored["current"], "releases/one")
            self.assertEqual((root / "current").readlink().as_posix(), "releases/one")
            self.assertTrue((root / "releases/one/manifest.json").is_file())
            self.assertTrue((root / "releases/two/manifest.json").is_file())

    def test_promotion_refuses_non_symlink_current(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.make_release(root, "one")
            (root / "current").mkdir()
            with self.assertRaisesRegex(ValueError, "current must be a symlink"):
                promote(root, "one")

    def test_release_requires_browser_runtime_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            release = root / "releases/bad"
            release.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "manifest.json and index.html"):
                promote(root, "bad")


if __name__ == "__main__":
    unittest.main()
