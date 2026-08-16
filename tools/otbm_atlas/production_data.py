"""Incremental orchestration for non-detail Atlas production phases."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from tools.otbm_atlas_facts.mechanics import resolve_mechanics

from . import composition as composition_module
from . import creature_sprites as creature_sprites_module
from . import factual_layers as factual_layers_module
from . import houses as houses_module
from . import monster_sprites as monster_sprites_module
from . import npc_sprites as npc_sprites_module
from . import spatial as spatial_module
from . import spawns as spawns_module
from . import tile_inspector as tile_inspector_module
from . import viewer as viewer_module
from .composition import classify_maps
from .environment_animation_resume import enrich_environment_animations_resumable
from .factual_layers import enrich_existing_atlas
from .houses import parse_houses
from .incremental_core import sha256_file
from .monster_sprites import enrich_monster_spawns
from .npc_sprites import enrich_npc_spawns
from .production_phases import ProductionPhaseCache, copy_if_changed, payload_digest, semantics_digest, tree_digest, write_json_if_changed
from .spatial import write_spatial_data
from .spawns import scan_spawns
from .tile_inspector import write_tile_inspector_data
from .viewer import write_viewer


def _load_json(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object in {path}")
    return value


def _optional_sha(path: Path) -> str:
    return sha256_file(path) if path.is_file() else "MISSING"


def _unknown_report(chunks: list[dict[str, object]]) -> dict[str, object]:
    unknown_items: dict[int, dict[str, object]] = {}
    for chunk in chunks:
        missing = chunk.get("missingAppearances", {})
        if not isinstance(missing, Mapping):
            continue
        for server_id, occurrences in missing.items():
            value = unknown_items.setdefault(int(server_id), {"serverId": int(server_id), "occurrences": 0, "chunks": []})
            value["occurrences"] = int(value["occurrences"]) + int(occurrences)
            value["chunks"].append({
                "z": chunk["z"], "chunkX": chunk["chunkX"], "chunkY": chunk["chunkY"], "logicalBounds": chunk["logicalBounds"]
            })
    return {
        "schemaVersion": 1,
        "items": list(unknown_items.values()),
        "statistics": {
            "uniqueServerIds": len(unknown_items),
            "occurrences": sum(int(value["occurrences"]) for value in unknown_items.values()),
        },
    }


def _spatial_result_from_cache(cache: ProductionPhaseCache) -> tuple[dict[str, object], dict[str, object]]:
    result = cache.result("spatial-factual") or {}
    spatial = result.get("spatialData", {})
    factual = result.get("factual", {})
    return (dict(spatial) if isinstance(spatial, Mapping) else {}, dict(factual) if isinstance(factual, Mapping) else {})


def build_incremental_production_data(
    *,
    map_path: Path,
    asset_dir: Path,
    output: Path,
    repository_root: Path,
    canonical: Mapping[str, Path],
    chunk_size: int,
    chunks: list[dict[str, object]],
    render_plan: Mapping[str, object],
    provenance: Mapping[str, object],
    assets_sha: str,
) -> dict[str, object]:
    data_dir = output / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    spool_dir = output / ".spool"
    cache = ProductionPhaseCache(output)

    # Unknown item aggregation depends only on detail reports, not other Atlas domains.
    unknown_fingerprint = payload_digest({
        "schema": 1,
        "chunks": [
            {"chunk": [chunk.get("z"), chunk.get("chunkX"), chunk.get("chunkY")], "missing": chunk.get("missingAppearances", {})}
            for chunk in chunks
        ],
    })
    if cache.current("unknown-items", unknown_fingerprint, ("data/unknown-items.json",)):
        unknown_report = _load_json(data_dir / "unknown-items.json")
    else:
        unknown_report = _unknown_report(chunks)
        write_json_if_changed(data_dir / "unknown-items.json", unknown_report)
        cache.commit("unknown-items", unknown_fingerprint, ("data/unknown-items.json",), {"statistics": unknown_report["statistics"]})

    # Mechanics facts are canonical spool output; byte-identical facts are not rewritten.
    copy_if_changed(spool_dir / "facts.json", data_dir / "mechanics.json")
    mechanics = _load_json(data_dir / "mechanics.json")

    # Spawns + creature sprites form one independent domain. Asset changes rerun only
    # this domain (and downstream spatial publication), never detail rendering.
    spawn_source_digest = tree_digest(canonical["worldRoot"], ("**/*-monster.xml", "**/*-npc.xml"))
    npc_definition_digest = tree_digest(canonical["npcDefinitionRoot"], ("**/*",))
    monster_definition_digest = tree_digest(canonical["monsterDefinitionRoot"], ("**/*",))
    spawn_semantics = semantics_digest((
        Path(spawns_module.__file__), Path(npc_sprites_module.__file__), Path(monster_sprites_module.__file__), Path(creature_sprites_module.__file__),
    ))
    spawn_fingerprint = payload_digest({
        "schema": 1,
        "spawnSources": spawn_source_digest,
        "npcDefinitions": npc_definition_digest,
        "monsterDefinitions": monster_definition_digest,
        "assetsSha256": assets_sha,
        "semantics": spawn_semantics,
    })
    spawn_patterns = ("data/spawns.json", "data/npc-sprites/**/*", "data/monster-sprites/**/*")
    if cache.current("spawns", spawn_fingerprint, spawn_patterns):
        spawns = _load_json(data_dir / "spawns.json")
        spawn_result = cache.result("spawns") or {}
        npc_sprite_statistics = dict(spawn_result.get("npcSprites", {})) if isinstance(spawn_result.get("npcSprites"), Mapping) else {}
        monster_sprite_statistics = dict(spawn_result.get("monsterSprites", {})) if isinstance(spawn_result.get("monsterSprites"), Mapping) else {}
    else:
        spawns = scan_spawns(canonical["worldRoot"])
        npc_sprite_statistics = enrich_npc_spawns(asset_dir, canonical["npcDefinitionRoot"], output, spawns["npcSpawns"], repository_root)
        monster_sprite_statistics = enrich_monster_spawns(asset_dir, canonical["monsterDefinitionRoot"], output, spawns["monsterSpawns"], repository_root)
        spawns["provenance"] = {
            "worldRoot": provenance["worldRoot"],
            "npcDefinitionRoot": provenance["npcDefinitionRoot"],
            "monsterDefinitionRoot": provenance["monsterDefinitionRoot"],
            "appearanceAssetRoot": provenance["appearanceAssetRoot"],
        }
        write_json_if_changed(data_dir / "spawns.json", spawns)
        cache.commit("spawns", spawn_fingerprint, spawn_patterns, {
            "npcSprites": npc_sprite_statistics,
            "monsterSprites": monster_sprite_statistics,
        })

    house_path = map_path.parent / "world-house.xml"
    house_fingerprint = payload_digest({
        "schema": 1,
        "source": _optional_sha(house_path),
        "semantics": semantics_digest((Path(houses_module.__file__),)),
    })
    if cache.current("houses", house_fingerprint, ("data/houses.json",)):
        houses = _load_json(data_dir / "houses.json")
    else:
        houses = parse_houses(house_path)
        write_json_if_changed(data_dir / "houses.json", houses)
        cache.commit("houses", house_fingerprint, ("data/houses.json",), {"statistics": houses.get("statistics", {})})

    composition_fingerprint = payload_digest({
        "schema": 1,
        "world": tree_digest(canonical["worldRoot"], ("**/*.otbm", "**/*.xml")),
        "semantics": semantics_digest((Path(composition_module.__file__),)),
    })
    if not cache.current("composition", composition_fingerprint, ("data/composition.json",)):
        composition = classify_maps(map_path.parent, repository_root)
        write_json_if_changed(data_dir / "composition.json", composition)
        cache.commit("composition", composition_fingerprint, ("data/composition.json",))

    # Base spatial data and factual overlays share browser shards/search. Treat them
    # as one phase so a cache hit skips both, while the writers themselves compare
    # final shard bytes and only replace changed chunks.
    factual_sources = tree_digest(canonical["crystalDataRoot"], (
        "scripts/**/*", "npc/**/*", "monster/**/*", "raids/**/*", "lib/**/*",
    ))
    facts_tool_sources = tree_digest(repository_root / "tools/otbm_atlas_facts", ("**/*.py",))
    supplemental_manifest = repository_root / "docs/maps/otbm-atlas-supplemental-sources-manifest.json"
    spatial_fingerprint = payload_digest({
        "schema": 1,
        "chunkSize": chunk_size,
        "mechanics": sha256_file(data_dir / "mechanics.json"),
        "spawns": sha256_file(data_dir / "spawns.json"),
        "houses": sha256_file(data_dir / "houses.json"),
        "factualSources": factual_sources,
        "factsToolSources": facts_tool_sources,
        "supplementalManifest": _optional_sha(supplemental_manifest),
        "semantics": semantics_digest((Path(spatial_module.__file__), Path(factual_layers_module.__file__))),
    })
    spatial_patterns = (
        "data/chunks/**/*.json", "data/search-index.json", "data/mechanics-resolution.json",
        "data/npc-services.json", "data/raids-events.json", "data/monster-metadata.json", "data/factual-layers.json",
    )
    if cache.current("spatial-factual", spatial_fingerprint, spatial_patterns):
        resolutions = _load_json(data_dir / "mechanics-resolution.json")
        spatial_statistics, factual_summary = _spatial_result_from_cache(cache)
    else:
        resolutions = resolve_mechanics(mechanics, canonical["crystalDataRoot"] / "scripts")
        write_json_if_changed(data_dir / "mechanics-resolution.json", resolutions)
        resolution_by_key = {(entry["kind"], int(entry["value"])): entry for entry in resolutions["resolutions"]}
        action_records = [{**entry, "mechanics": resolution_by_key.get(("ActionID", int(entry["actionId"])), {"status": "UNKNOWN", "candidates": []})} for entry in mechanics["actionIds"]]
        unique_records = [{**entry, "mechanics": resolution_by_key.get(("UniqueID", int(entry["uniqueId"])), {"status": "UNKNOWN", "candidates": []})} for entry in mechanics["uniqueIds"]]
        spatial_statistics = write_spatial_data(output, chunk_size, {
            **{key: mechanics[key] for key in ("teleports", "houseTiles", "houseDoors", "towns", "waypoints")},
            "actionIds": action_records,
            "uniqueIds": unique_records,
            "mechanics": action_records + unique_records,
            "monsterSpawns": spawns["monsterSpawns"],
            "npcSpawns": spawns["npcSpawns"],
            "houses": houses["houses"],
        })
        factual_report = enrich_existing_atlas(output, repository_root)
        if factual_report.get("status") == "RESOLVED":
            resolutions = _load_json(data_dir / "mechanics-resolution.json")
            factual_summary = {
                "status": "RESOLVED",
                "statistics": factual_report.get("statistics", {}),
                "spatial": factual_report.get("spatial", {}),
            }
        else:
            factual_summary = {"status": factual_report.get("status", "UNKNOWN"), "reason": factual_report.get("reason")}
        cache.commit("spatial-factual", spatial_fingerprint, spatial_patterns, {
            "spatialData": spatial_statistics,
            "factual": factual_summary,
        })

    # Tile inspector depends on canonical tile-facts. The phase fingerprint skips it
    # entirely when the OTBM is unchanged. On map changes the writer receives exact
    # changed/deleted factual shard paths and preserves untouched browser shards.
    tile_fingerprint = payload_digest({
        "schema": 1,
        "mapSha256": sha256_file(map_path),
        "chunkSize": chunk_size,
        "semantics": semantics_digest((Path(tile_inspector_module.__file__),)),
    })
    tile_patterns = ("data/tile-inspector/**/*.json",)
    if cache.current("tile-inspector", tile_fingerprint, tile_patterns):
        tile_index = _load_json(data_dir / "tile-inspector/index.json")
        tile_statistics = dict(tile_index.get("statistics", {})) if isinstance(tile_index.get("statistics"), Mapping) else {}
    else:
        spool_report = render_plan.get("spool", {})
        tile_report = spool_report.get("tileFacts", {}) if isinstance(spool_report, Mapping) else {}
        changed = list(tile_report.get("changed", [])) if isinstance(tile_report, Mapping) else []
        deleted = list(tile_report.get("deleted", [])) if isinstance(tile_report, Mapping) else []
        tile_statistics = write_tile_inspector_data(output, changed_sidecars=changed or None, deleted_sidecars=deleted or None)
        cache.commit("tile-inspector", tile_fingerprint, tile_patterns, {"statistics": tile_statistics})

    environment_statistics = enrich_environment_animations_resumable(asset_dir, output)

    viewer_fingerprint = payload_digest({
        "schema": 1,
        "semantics": semantics_digest((
            Path(viewer_module.__file__),
            Path(viewer_module.__file__).with_name("viewer_app.js"),
            Path(viewer_module.__file__).with_name("viewer_runtime.js"),
            Path(viewer_module.__file__).with_name("creature_animation_runtime.js"),
            Path(viewer_module.__file__).with_name("tile_inspector_runtime.js"),
            Path(viewer_module.__file__).with_name("accessibility_runtime.js"),
        )),
    })
    viewer_patterns = ("*.html", "*.js", "*.css")
    if not cache.current("viewer", viewer_fingerprint, viewer_patterns):
        write_viewer(output)
        cache.commit("viewer", viewer_fingerprint, viewer_patterns)

    final_resolution_stats = resolutions.get("statistics", {}) if isinstance(resolutions, Mapping) else {}
    statistics: dict[str, object] = {
        "schemaVersion": 1,
        "chunks": len(chunks),
        "populatedFloors": sorted({int(chunk["z"]) for chunk in chunks}),
        "tiles": sum(int(chunk["tiles"]) for chunk in chunks),
        "groundItems": sum(int(chunk["groundItems"]) for chunk in chunks),
        "childItems": sum(int(chunk["childItems"]) for chunk in chunks),
        "renderOperations": sum(int(chunk["renderOperations"]) for chunk in chunks),
        "actionIdRecords": len(mechanics["actionIds"]),
        "uniqueActionIds": len({entry["actionId"] for entry in mechanics["actionIds"]}),
        "uniqueIdRecords": len(mechanics["uniqueIds"]),
        "uniqueUniqueIds": len({entry["uniqueId"] for entry in mechanics["uniqueIds"]}),
        "teleports": len(mechanics["teleports"]),
        "houseTiles": len(mechanics["houseTiles"]),
        "houseDoors": len(mechanics["houseDoors"]),
        "houses": houses["statistics"]["houses"],
        "towns": len(mechanics["towns"]),
        "waypoints": len(mechanics["waypoints"]),
        **spawns["statistics"],
        "npcSprites": npc_sprite_statistics,
        "monsterSprites": monster_sprite_statistics,
        "mechanicsResolution": final_resolution_stats,
        "unknownItems": unknown_report["statistics"],
        "provenance": dict(provenance),
        "spatialData": spatial_statistics,
        "tileInspector": tile_statistics,
        "environmentAnimations": environment_statistics,
        "incrementalBuild": {
            "dirtyDetailChunks": len(render_plan.get("dirtyDetailChunks", [])),
            "reusedDetailChunks": len(render_plan.get("reusedDetailChunks", [])),
            "deletedDetailChunks": len(render_plan.get("deletedDetailChunks", [])),
            "fullBuildRequired": render_plan.get("fullBuildRequired", False),
            "fullBuildReasons": render_plan.get("fullBuildReasons", []),
            "legacyPublicationAdopted": render_plan.get("legacyPublicationAdopted", False),
            "spool": render_plan.get("spool", {}),
        },
    }
    if factual_summary.get("status") == "RESOLVED":
        factual_stats = factual_summary.get("statistics", {})
        statistics["mechanicsResolution"] = factual_stats.get("mechanicsResolution", final_resolution_stats) if isinstance(factual_stats, Mapping) else final_resolution_stats
        statistics["factualLayers"] = factual_stats
        statistics["factualSpatial"] = factual_summary.get("spatial", {})
    else:
        statistics["factualLayers"] = {"status": factual_summary.get("status", "UNKNOWN"), "reason": factual_summary.get("reason")}

    write_json_if_changed(data_dir / "statistics.json", statistics)
    return statistics
