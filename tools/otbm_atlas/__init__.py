"""Deterministic OTBM analysis and atlas tooling."""

from .nodefile import NodeEvent, NodeEventKind, NodeFileError, iter_node_events
from .semantic import Diagnostic, Item, MapHeader, Position, Tile, Town, Waypoint, iter_map_records, walk_items

# Atlas enrichers are composed here so existing atlas.py keeps one stable build entry
# point while generated creature and cyclic-environment data remain separate modules.
from . import npc_sprites as _npc_sprites
from .environment_animation import enrich_environment_animations as _enrich_environment_animations
_original_enrich_npc_spawns = _npc_sprites.enrich_npc_spawns

def _enrich_atlas_sprites(asset_dir, scripts_dir, output, records):
	statistics = _original_enrich_npc_spawns(asset_dir, scripts_dir, output, records)
	statistics["environmentAnimations"] = _enrich_environment_animations(asset_dir, output)
	return statistics

_npc_sprites.enrich_npc_spawns = _enrich_atlas_sprites

__all__ = [
	"Diagnostic", "Item", "MapHeader", "NodeEvent", "NodeEventKind", "NodeFileError",
	"Position", "Tile", "Town", "Waypoint", "iter_map_records", "iter_node_events",
	"walk_items",
]
