"""WSL/desktop Atlas builder with parallel overview derivatives."""
from __future__ import annotations

import argparse
from collections.abc import Mapping
from concurrent.futures import ProcessPoolExecutor, as_completed
import hashlib
from io import BytesIO
import json
from pathlib import Path

from . import atlas as core
from .assets import encode_png
from .overview import LOW_OVERVIEW_FACTOR, OVERVIEW_FACTOR, OVERVIEW_VERSION, make_overview


OverviewDerivative = tuple[str, str, str, int, str, int, int]
OverviewCandidate = tuple[str, str, str, str, str, int, str, int, int, dict[str, object] | None]


def _make_overviews(payload: bytes, factors: tuple[int, ...]) -> dict[int, bytes]:
    """Produce multiple canonical overview factors with at most one PNG decode."""
    unique_factors = tuple(dict.fromkeys(factors))
    try:
        from PIL import Image

        with Image.open(BytesIO(payload)) as image:
            rgba_image = image.convert("RGBA")
            results: dict[int, bytes] = {}
            for factor in unique_factors:
                if factor <= 0 or rgba_image.width % factor or rgba_image.height % factor:
                    raise ValueError("PNG dimensions must be divisible by overview factor")
                resized = rgba_image.resize(
                    (rgba_image.width // factor, rgba_image.height // factor),
                    Image.Resampling.NEAREST,
                )
                results[factor] = encode_png(resized.width, resized.height, resized.tobytes())
            return results
    except ImportError:
        return {factor: make_overview(payload, factor) for factor in unique_factors}


def _overview_worker(job: tuple[str, tuple[OverviewDerivative, ...]]) -> list[tuple[str, str, dict[str, object]]]:
    detailed_path_text, derivatives = job
    source_payload = Path(detailed_path_text).read_bytes()
    payloads = _make_overviews(source_payload, tuple(derivative[3] for derivative in derivatives))
    results: list[tuple[str, str, dict[str, object]]] = []
    for prefix, overview_path_text, report_path_text, factor, fingerprint, image_width, image_height in derivatives:
        overview_path = Path(overview_path_text)
        report_path = Path(report_path_text)
        payload = payloads[factor]
        overview_path.parent.mkdir(parents=True, exist_ok=True)
        temporary = overview_path.with_suffix(".png.tmp")
        temporary.write_bytes(payload)
        temporary.replace(overview_path)
        report = {
            "fingerprint": fingerprint,
            "checksum": hashlib.sha256(payload).hexdigest(),
            "imageWidth": image_width // factor,
            "imageHeight": image_height // factor,
        }
        core._write_text_atomic(report_path, json.dumps(report, sort_keys=True) + "\n")
        results.append((prefix, overview_path_text, report))
    return results


def _validate_overview_candidate(candidate: OverviewCandidate) -> tuple[str, str, dict[str, object] | None, bool]:
    """Validate one reusable derivative from one report read and one PNG read."""
    prefix, _directory, _chunk_text, overview_path_text, report_path_text, factor, fingerprint, image_width, image_height, previous_identity = candidate
    overview_path = Path(overview_path_text)
    report_path = Path(report_path_text)
    if not overview_path.is_file() or not report_path.is_file():
        return prefix, overview_path_text, None, False

    try:
        report_payload = report_path.read_bytes()
        report_value = json.loads(report_payload.decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError):
        return prefix, overview_path_text, None, False
    if not isinstance(report_value, dict):
        return prefix, overview_path_text, None, False
    report = {str(key): value for key, value in report_value.items()}
    checksum = report.get("checksum")
    if (
        report.get("fingerprint") != fingerprint
        or not isinstance(checksum, str)
        or report.get("imageWidth") != image_width // factor
        or report.get("imageHeight") != image_height // factor
    ):
        return prefix, overview_path_text, report, False

    try:
        image_payload = overview_path.read_bytes()
    except OSError:
        return prefix, overview_path_text, report, False
    actual_checksum = hashlib.sha256(image_payload).hexdigest()
    if actual_checksum != checksum:
        return prefix, overview_path_text, report, False

    if previous_identity is not None:
        identity_checksum = previous_identity.get("checksum")
        identity_report_checksum = previous_identity.get("reportSha256")
        if identity_checksum != actual_checksum:
            return prefix, overview_path_text, report, False
        if identity_report_checksum != hashlib.sha256(report_payload).hexdigest():
            return prefix, overview_path_text, report, False

    return prefix, overview_path_text, report, True


def _validate_overview_job(job: tuple[OverviewCandidate, ...]) -> list[tuple[str, str, dict[str, object] | None, bool]]:
    return [_validate_overview_candidate(candidate) for candidate in job]


def _apply_overview_result(chunk: dict[str, object], output: Path, prefix: str, overview_path_text: str, report: Mapping[str, object]) -> None:
    overview_path = Path(overview_path_text)
    chunk.update({
        f"{prefix}Path": overview_path.relative_to(output).as_posix(),
        f"{prefix}Checksum": report["checksum"],
        f"{prefix}ImageWidth": report["imageWidth"],
        f"{prefix}ImageHeight": report["imageHeight"],
    })


def _progress(completed: int, total: int, next_mark: int) -> int:
    if completed == total or completed >= next_mark:
        print(f"Overview validation: {completed}/{total}", flush=True)
        while next_mark <= completed:
            next_mark += 256
    return next_mark


def build_overviews(chunks: list[dict[str, object]], output: Path, previous_overviews: dict[str, object] | None, workers: int) -> None:
    """Validate/reuse existing overviews and build only dirty derivatives in parallel."""
    if workers <= 0:
        raise ValueError("workers must be positive")

    validation_jobs: list[tuple[int, tuple[OverviewCandidate, ...]]] = []
    generation_by_index: list[list[OverviewDerivative]] = [[] for _chunk in chunks]
    for index, chunk in enumerate(chunks):
        chunk_text = f"z{chunk['z']}/{chunk['chunkX']}_{chunk['chunkY']}"
        candidates: list[OverviewCandidate] = []
        for prefix, directory, factor in (("overview", "overview", OVERVIEW_FACTOR), ("lowOverview", "overview-low", LOW_OVERVIEW_FACTOR)):
            overview_path = output / directory / f"z{chunk['z']}" / f"{chunk['chunkX']}_{chunk['chunkY']}.png"
            report_path = overview_path.with_suffix(".json")
            fingerprint = hashlib.sha256(f"{OVERVIEW_VERSION}:{factor}:{chunk['checksum']}".encode()).hexdigest()
            identity: dict[str, object] | None = None
            if previous_overviews is not None:
                value = previous_overviews.get(f"{directory}/{chunk_text}")
                identity = dict(value) if isinstance(value, Mapping) else {}
            candidates.append((
                prefix,
                directory,
                chunk_text,
                str(overview_path),
                str(report_path),
                factor,
                fingerprint,
                int(chunk["imageWidth"]),
                int(chunk["imageHeight"]),
                identity,
            ))
        validation_jobs.append((index, tuple(candidates)))

    candidate_count = sum(len(job) for _index, job in validation_jobs)
    if candidate_count == 0:
        return
    worker_count = min(workers, len(validation_jobs))
    print(f"Overview validation: {candidate_count} candidates | workers={worker_count}", flush=True)

    validation_results: list[list[tuple[str, str, dict[str, object] | None, bool]] | None] = [None] * len(chunks)
    completed = 0
    next_mark = 256
    if worker_count == 1:
        for index, job in validation_jobs:
            result = _validate_overview_job(job)
            validation_results[index] = result
            completed += len(result)
            next_mark = _progress(completed, candidate_count, next_mark)
    else:
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            future_to_index = {executor.submit(_validate_overview_job, job): index for index, job in validation_jobs}
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                result = future.result()
                validation_results[index] = result
                completed += len(result)
                next_mark = _progress(completed, candidate_count, next_mark)

    valid_count = 0
    dirty_count = 0
    for index, (_job_index, candidates) in enumerate(validation_jobs):
        results = validation_results[index]
        if results is None:
            raise RuntimeError(f"overview validation produced no result for chunk index {index}")
        for candidate, (prefix, overview_path_text, report, valid) in zip(candidates, results, strict=True):
            _prefix, _directory, _chunk_text, _path, report_path_text, factor, fingerprint, image_width, image_height, _identity = candidate
            if valid:
                if report is None:
                    raise RuntimeError("validated overview has no report")
                _apply_overview_result(chunks[index], output, prefix, overview_path_text, report)
                valid_count += 1
            else:
                generation_by_index[index].append((prefix, overview_path_text, report_path_text, factor, fingerprint, image_width, image_height))
                dirty_count += 1
    print(f"Overview reuse: {valid_count} valid, {dirty_count} dirty", flush=True)

    jobs: list[tuple[int, tuple[str, tuple[OverviewDerivative, ...]]]] = []
    for index, derivatives in enumerate(generation_by_index):
        if derivatives:
            detailed_path = output / str(chunks[index]["path"])
            jobs.append((index, (str(detailed_path), tuple(derivatives))))
    if not jobs:
        return

    derivative_worker_count = min(workers, len(jobs))
    print(f"Overview derivatives: {len(jobs)} dirty chunks | workers={derivative_worker_count}", flush=True)
    if derivative_worker_count == 1:
        for index, job in jobs:
            for prefix, overview_path_text, report in _overview_worker(job):
                _apply_overview_result(chunks[index], output, prefix, overview_path_text, report)
        return

    completed_chunks = 0
    with ProcessPoolExecutor(max_workers=derivative_worker_count) as executor:
        future_to_index = {executor.submit(_overview_worker, job): index for index, job in jobs}
        for future in as_completed(future_to_index):
            index = future_to_index[future]
            for prefix, overview_path_text, report in future.result():
                _apply_overview_result(chunks[index], output, prefix, overview_path_text, report)
            completed_chunks += 1
            if completed_chunks == len(jobs) or completed_chunks % 64 == 0:
                print(f"Overview derivatives: {completed_chunks}/{len(jobs)} chunks", flush=True)


def build_atlas(map_path: Path, asset_dir: Path, output: Path, chunk_size: int = 128, scripts_dir: Path | None = None, repository_root: Path = Path("."), workers: int = 1, allow_full_build: bool = False) -> dict[str, object]:
    """Run the production Atlas build with parallel overview post-processing."""
    if chunk_size <= 0:
        raise ValueError("chunk size must be positive")
    if workers <= 0:
        raise ValueError("workers must be positive")
    canonical = core.canonical_source_paths(repository_root)
    core._require_canonical_source(map_path, canonical["map"], "map")
    core._require_canonical_source(asset_dir, canonical["appearanceAssetRoot"], "appearance assets")
    if scripts_dir is not None:
        core._require_canonical_source(scripts_dir, canonical["crystalDataRoot"], "CrystalServer data root")

    map_sha, assets_sha = core._sha256(map_path), core._tree_sha256(asset_dir)
    expected = {"mapSha256": map_sha, "assetsSha256": assets_sha, "chunkSize": chunk_size, "atlasVersion": core.ATLAS_VERSION, "tileFactsVersion": core.TILE_FACTS_VERSION}
    render_plan = core.prepare_production_render_plan(map_path, asset_dir, output, repository_root, chunk_size, expected, {"version": core.SPOOL_VERSION, "tileFactsVersion": core.TILE_FACTS_VERSION}, core.spool_map, allow_full_build=allow_full_build)
    spool_dir = Path(str(render_plan["spoolDir"]))
    dirty_chunks = {str(value) for value in render_plan["dirtyDetailChunks"]}
    fingerprints = {str(key): str(value) for key, value in dict(render_plan["chunkFingerprints"]).items()}
    core.remove_deleted_chunk_outputs(output, [str(value) for value in render_plan["deletedDetailChunks"]])

    renderer = core.AssetRenderer(asset_dir) if workers == 1 else None
    chunks: list[dict[str, object]] = []
    entries: list[tuple[dict[str, object], tuple[str, str, str, str] | None]] = []

    def chunk_order(value: Path) -> tuple[int, int, int]:
        chunk_x, chunk_y = map(int, value.stem.split("_"))
        return int(value.parent.name[1:]), chunk_y, chunk_x

    for path in sorted(spool_dir.glob("z*/*.bin"), key=chunk_order):
        z = int(path.parent.name[1:])
        chunk_x, chunk_y = map(int, path.stem.split("_"))
        chunk_text = f"z{z}/{chunk_x}_{chunk_y}"
        logical_bounds = (chunk_x * chunk_size, chunk_x * chunk_size + chunk_size - 1, chunk_y * chunk_size, chunk_y * chunk_size + chunk_size - 1, z)
        tile_path = output / "tiles" / f"z{z}" / f"{chunk_x}_{chunk_y}.png"
        report_path = tile_path.with_suffix(".json")
        fingerprint = fingerprints[chunk_text]
        cached_report = core._read_report(report_path)
        cache_valid = chunk_text not in dirty_chunks and tile_path.exists() and cached_report is not None
        if cache_valid:
            entries.append(({"z": z, "chunkX": chunk_x, "chunkY": chunk_y, "logicalBounds": list(logical_bounds), "path": tile_path.relative_to(output).as_posix(), **cached_report, "fingerprint": fingerprint}, None))
        else:
            entries.append(({"z": z, "chunkX": chunk_x, "chunkY": chunk_y, "logicalBounds": list(logical_bounds), "path": tile_path.relative_to(output).as_posix()}, (str(path), str(tile_path), str(report_path), fingerprint)))

    if workers == 1:
        assert renderer is not None
        for metadata, job in entries:
            chunks.append({**metadata, **({} if job is None else core._write_rendered_chunk(Path(job[1]), Path(job[2]), Path(job[0]), job[3], renderer))})
    else:
        with ProcessPoolExecutor(max_workers=workers, initializer=core._init_render_worker, initargs=(str(asset_dir),)) as executor:
            futures = [None if job is None else executor.submit(core._render_worker, job) for _metadata, job in entries]
            for (metadata, _job), future in zip(entries, futures):
                chunks.append({**metadata, **({} if future is None else future.result())})

    previous_overviews = render_plan.get("previousOverviewFiles") if isinstance(render_plan.get("previousOverviewFiles"), dict) else None
    build_overviews(chunks, output, previous_overviews, workers)

    provenance = {
        "map": core.CANONICAL_WORLD_ROOT.joinpath("world.otbm").as_posix(),
        "worldRoot": core.CANONICAL_WORLD_ROOT.as_posix(),
        "npcDefinitionRoot": core.CANONICAL_NPC_ROOT.as_posix(),
        "monsterDefinitionRoot": core.CANONICAL_MONSTER_ROOT.as_posix(),
        "appearanceAssetRoot": core.CANONICAL_ASSET_ROOT.as_posix(),
    }
    manifest = {"schemaVersion": core.ATLAS_VERSION, "chunkSize": chunk_size, "tilePixels": 32, "overviewFactor": OVERVIEW_FACTOR, "lowOverviewFactor": LOW_OVERVIEW_FACTOR, "overviewVersion": OVERVIEW_VERSION, "chunks": chunks, "sources": expected, "provenance": provenance}
    output.mkdir(parents=True, exist_ok=True)
    core._write_text_atomic(output / "manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    core.commit_production_render_state(output, render_plan)
    core._write_text_atomic(spool_dir / "source.json", json.dumps(expected, sort_keys=True) + "\n")
    core.build_incremental_production_data(map_path=map_path, asset_dir=asset_dir, output=output, repository_root=repository_root, canonical=canonical, chunk_size=chunk_size, chunks=chunks, render_plan=render_plan, provenance=provenance, assets_sha=assets_sha)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("map", type=Path)
    parser.add_argument("assets", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--chunk-size", type=int, default=128)
    parser.add_argument("--scripts", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--repository", type=Path, default=Path("."))
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--allow-full-build", action="store_true")
    args = parser.parse_args()
    build_atlas(args.map, args.assets, args.output, args.chunk_size, args.scripts, args.repository, args.workers, args.allow_full_build)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
