from __future__ import annotations

from collections import Counter
import unittest

from tools.otbm_atlas.assets import Appearance, SpriteInfo
from tools.otbm_atlas.render import _blend, _item_patterns, render_tiles
from tools.otbm_atlas.semantic import Item, Position, Tile


def appearance(*, stackable: bool = False, splash: bool = False, fluid_container: bool = False) -> Appearance:
	return Appearance(
		appearance_id=1, name="test", is_ground=False, clip=False, bottom=False, top=False,
		stackable=stackable, splash=splash, fluid_container=fluid_container,
		shift=None, height=None, frames=(),
	)


class RecordingRenderer:
	def __init__(self) -> None:
		self.missing_appearances: Counter[int] = Counter()
		self.missing_sprites: Counter[int] = Counter()
		self.calls: list[int] = []

	def item_sprites(self, item: Item, _x: int, _y: int, _z: int):
		self.calls.append(item.server_id)
		return iter(())


class RenderTests(unittest.TestCase):
	def test_alpha_blend_and_clipping_are_deterministic(self) -> None:
		canvas = bytearray(b"\x00\x00\xff\xff" * 4)
		source = b"\xff\x00\x00\x80" * 4
		_blend(canvas, 2, 2, source, 2, 2, 1, 1)
		self.assertEqual(canvas[12:16], bytes((128, 0, 127, 255)))
		self.assertEqual(canvas[:4], b"\x00\x00\xff\xff")

	def test_stack_count_selects_otclient_pattern_bucket(self) -> None:
		frame = SpriteInfo(4, 2, 1, 1, tuple(range(8)), 1, 0)
		self.assertEqual(_item_patterns(appearance(stackable=True), frame, Item(1, 25), 10, 11, 7), (2, 1, 0))
		self.assertEqual(_item_patterns(appearance(stackable=True), frame, Item(1, 4), 10, 11, 7), (3, 0, 0))

	def test_modern_fluid_subtype_selects_color_pattern(self) -> None:
		frame = SpriteInfo(4, 3, 1, 1, tuple(range(12)), 1, 0)
		self.assertEqual(_item_patterns(appearance(fluid_container=True), frame, Item(1, 2), 0, 0, 7), (3, 1, 0))
		self.assertEqual(_item_patterns(appearance(splash=True), frame, Item(1, 18), 0, 0, 7), (0, 2, 0))

	def test_nested_container_contents_are_not_rendered_on_tile(self) -> None:
		renderer = RecordingRenderer()
		container = Item(100, children=(Item(200),))
		tile = Tile(Position(1, 2, 7), None, 0, None, (container,))
		_png, report = render_tiles(iter((tile,)), renderer, (1, 1, 2, 2, 7))
		self.assertEqual(renderer.calls, [100])
		self.assertEqual(report["childItems"], 2)


if __name__ == "__main__":
	unittest.main()
