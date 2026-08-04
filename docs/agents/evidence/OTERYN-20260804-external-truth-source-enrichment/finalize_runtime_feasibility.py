#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import io
import json
import re
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path('docs/agents/evidence/OTERYN-20260804-external-truth-source-enrichment')
DOSSIERS = ROOT / 'dossiers'
PINNED_OTHERYN = '1f316400053f489e58608d13961069835871ab0e'
BLOCKER = (
    'the repository can start the server and validate the seeded HTTP login response, '
    'but it has no deterministic game-protocol/client driver and no isolated per-scenario '
    'world fixture for map, quest, combat, store, boss, persistence or client-rendering actions; '
    'adding that infrastructure would be implementation outside this audit-only authorization'
)


def load_blocks(text: str):
    blocks = []
    for match in re.finditer(r'```yaml\n(.*?)\n```', text, re.S):
        obj = yaml.safe_load(match.group(1))
        if isinstance(obj, dict):
            blocks.append((match.start(), match.end(), obj))
    return blocks


def dump_block(obj: dict) -> str:
    return '```yaml\n' + yaml.safe_dump(obj, sort_keys=False, allow_unicode=True, width=120).rstrip() + '\n```'


def replace_blocks(text: str, transforms: dict[str, callable]) -> tuple[str, dict]:
    blocks = load_blocks(text)
    applied: dict[str, dict] = {}
    for start, end, obj in reversed(blocks):
        discriminator = next((key for key in transforms if key in obj), None)
        if discriminator is None:
            continue
        new_obj = transforms[discriminator](dict(obj))
        applied[discriminator] = new_obj
        text = text[:start] + dump_block(new_obj) + text[end:]
    return text, applied


def feasibility_doc() -> str:
    return f'''# Runtime execution feasibility closeout

Task: `OTERYN-20260804-external-truth-source-enrichment`

## Decision

The item-level research and static comparison are complete. The remaining runtime plans were evaluated against the exact Otheryn repository and its existing CI/runtime capabilities without adding product or reusable test infrastructure.

Final runtime disposition:

- **13 `NOT_APPLICABLE`** — static evidence already reaches a target disposition (`TARGET_AFFECTED`, `TARGET_NOT_AFFECTED` or `TARGET_PATH_ABSENT`), so a game-world execution would not change the audit decision;
- **5 `NOT_RUN_REFERENCE_INSUFFICIENT`** — the source evidence does not define a deterministic expected result;
- **42 `NOT_RUN_INFEASIBLE`** — expected behavior is sufficiently defined, but the exact repository lacks the required game-driving fixture.

## Existing executable boundary

The repository's Docker quickstart can start the disposable database, server, login server and web stack. Its assertions verify configuration, HTTP readiness and the seeded test account returned by the login server. It does **not**:

- authenticate a character on the game protocol port;
- drive movement, item use, NPC dialogue, combat, bosses, map swaps, store operations or persistence lifecycle;
- provide an OTClient or official-client runner;
- seed and reset the exact map tiles, quest storages, cooldowns, encounters, houses, forge state, wheel state or protocol/UI state required by these 42 scenarios;
- capture the scenario-specific server/client observations required by the dossiers.

Repository evidence: `.github/scripts/docker-quickstart-smoke.sh` and `.github/workflows/reusable-docker-quickstart-smoke.yml`.

## Why a new harness was not created

A truthful execution of the 42 static-inconclusive rows would require a new maintained game-protocol driver or client harness plus scenario-specific world/DB fixtures and cleanup APIs. That is reusable implementation and test infrastructure, not a narrow temporary audit probe. The active task has `implementation_authorized: false`; therefore creating that system would exceed authority and could itself alter the behavior being audited.

The blocker is not runner availability or ordinary CI cost. It is the absence of an existing deterministic input-to-observation seam for the required gameplay/client boundaries.

## Safety and cleanup

- production access: none;
- persistent live state: none;
- external side effects: none;
- runtime scenarios started: 0;
- cleanup required: none;
- product fixes made: none.

## Exact target baseline

Pinned Otheryn comparison revision: `{PINNED_OTHERYN}`.

A later implementation-authorized programme may build a reusable isolated gameplay E2E harness and then execute the 42 plans without changing their expected-behavior definitions.
'''

records = []
for path in sorted(DOSSIERS.glob('*.md')):
    original = path.read_text(encoding='utf-8')
    blocks = load_blocks(original)
    conclusion = next(obj for _, _, obj in blocks if 'static_conclusion' in obj)
    plan = next(obj for _, _, obj in blocks if 'plan_status' in obj)
    static = conclusion['static_conclusion']
    plan_status = plan['plan_status']

    if static != 'STATIC_INCONCLUSIVE':
        target_plan = 'NOT_APPLICABLE'
        target_runtime = 'NOT_APPLICABLE'
        target_execution = 'NOT_RUN'
        target_blocker = 'not applicable: pinned static evidence already reaches a target disposition; runtime execution would not change the audit decision'
        observations = ['static comparison is sufficient for the target disposition; no game-world state was created']
        cleanup = 'not applicable'
    elif plan_status == 'BLOCKED_REFERENCE':
        target_plan = 'BLOCKED_REFERENCE'
        target_runtime = 'NOT_RUN_REFERENCE_INSUFFICIENT'
        target_execution = 'BLOCKED'
        target_blocker = plan.get('blocker') or 'reference behavior is insufficient for a deterministic runtime assertion'
        observations = ['reference behavior is insufficient for a deterministic pass/fail runtime assertion']
        cleanup = 'not started; no state created'
    else:
        target_plan = 'BLOCKED_INFEASIBLE'
        target_runtime = 'NOT_RUN_INFEASIBLE'
        target_execution = 'BLOCKED'
        target_blocker = BLOCKER
        observations = [
            'Docker quickstart validates server startup and the seeded HTTP login response only',
            'no deterministic game-protocol/client driver or per-scenario world fixture exists in the repository',
        ]
        cleanup = 'not started; no state created'

    def transform_plan(obj: dict) -> dict:
        obj['plan_status'] = target_plan
        artifacts = list(obj.get('artifacts') or [])
        if 'runtime-feasibility.md' not in artifacts:
            artifacts.append('runtime-feasibility.md')
        obj['artifacts'] = artifacts
        obj['blocker'] = target_blocker
        return obj

    def transform_execution(obj: dict) -> dict:
        obj['execution_status'] = target_execution
        obj['exact_otheryn_head'] = 'not applicable'
        obj['run_ids'] = []
        obj['observations'] = observations
        obj['artifacts'] = ['runtime-feasibility.md']
        obj['cleanup_result'] = cleanup
        return obj

    def transform_conclusion(obj: dict) -> dict:
        obj['runtime_conclusion'] = target_runtime
        suffix = {
            'NOT_APPLICABLE': ' Runtime execution is not applicable because the pinned static comparison already determines the target disposition.',
            'NOT_RUN_REFERENCE_INSUFFICIENT': ' Runtime execution is reference-blocked because no deterministic expected result is supported.',
            'NOT_RUN_INFEASIBLE': ' Runtime execution is infrastructure-blocked: the repository has no deterministic game/client driver and adding one is outside audit-only authority.',
        }[target_runtime]
        rationale = str(obj.get('rationale', '')).rstrip()
        if suffix.strip() not in rationale:
            obj['rationale'] = rationale + suffix
        return obj

    updated, applied = replace_blocks(original, {
        'plan_status': transform_plan,
        'execution_status': transform_execution,
        'truth_status': transform_conclusion,
    })
    if updated != original:
        path.write_text(updated, encoding='utf-8')
    key = next(obj['canonical_key'] for _, _, obj in load_blocks(updated) if 'canonical_key' in obj)
    records.append({
        'canonical_key': key,
        'plan_status': target_plan,
        'runtime_conclusion': target_runtime,
        'execution_status': target_execution,
        'static_conclusion': static,
    })

record_by_key = {row['canonical_key']: row for row in records}

scope = json.loads((ROOT / 'canonical-scope.json').read_text(encoding='utf-8'))
rows = []
for idx, item in enumerate(scope['items'], start=1):
    key = item['canonical_key']
    row = record_by_key[key]
    file_name = key.replace('/', '-').replace('#', '-') + '.md'
    execution_cell = 'NOT_APPLICABLE' if row['runtime_conclusion'] == 'NOT_APPLICABLE' else row['execution_status']
    rows.append(f"| {idx} | `{key}` | {row['plan_status']} | {row['runtime_conclusion']} | {execution_cell} | `dossiers/{file_name}` |")
counts_plan = Counter(r['plan_status'] for r in records)
counts_runtime = Counter(r['runtime_conclusion'] for r in records)
repro = '''# Reproduction matrix

Task: `OTERYN-20260804-external-truth-source-enrichment`

Exactly 60 canonical runtime dispositions are listed. No product implementation was authorized or performed.

| # | Canonical key | Plan | Runtime | Execution | Dossier |
|---:|---|---|---|---|---|
''' + '\n'.join(rows) + '\n\n' + (
    f"Summary: {counts_plan.get('NOT_APPLICABLE', 0)} `NOT_APPLICABLE`, "
    f"{counts_plan.get('BLOCKED_REFERENCE', 0)} `BLOCKED_REFERENCE`, "
    f"{counts_plan.get('BLOCKED_INFEASIBLE', 0)} `BLOCKED_INFEASIBLE`; "
    f"runtime {counts_runtime.get('NOT_APPLICABLE', 0)} `NOT_APPLICABLE`, "
    f"{counts_runtime.get('NOT_RUN_REFERENCE_INSUFFICIENT', 0)} `NOT_RUN_REFERENCE_INSUFFICIENT`, "
    f"{counts_runtime.get('NOT_RUN_INFEASIBLE', 0)} `NOT_RUN_INFEASIBLE`; 0 canonical gameplay reproductions executed.\n"
)
(ROOT / 'reproduction-matrix.md').write_text(repro, encoding='utf-8')

decision_path = ROOT / 'decision-matrix.md'
decision = decision_path.read_text(encoding='utf-8')
for key, row in record_by_key.items():
    pattern = re.compile(rf'^(\|\s*\d+\s*\|\s*`{re.escape(key)}`\s*\|\s*[^|]+\|\s*[^|]+\|\s*)[^|]+(\|.*)$', re.M)
    decision, count = pattern.subn(rf'\g<1>{row["runtime_conclusion"]} \g<2>', decision)
    if count != 1:
        raise SystemExit(f'failed to update decision row {key}: count={count}')
truth_counts = Counter()
static_counts = Counter()
action_counts = Counter()
for path in sorted(DOSSIERS.glob('*.md')):
    blocks = load_blocks(path.read_text(encoding='utf-8'))
    c = next(obj for _, _, obj in blocks if 'truth_status' in obj)
    truth_counts[c['truth_status']] += 1
    static_counts[c['static_conclusion']] += 1
    action_counts[c['owner_action']] += 1
decision = re.sub(
    r'\nSummary:.*\Z',
    '\nSummary: '
    f"truth {truth_counts.get('PROVEN', 0)} `PROVEN`, {truth_counts.get('PARTIALLY_PROVEN', 0)} `PARTIALLY_PROVEN`, {truth_counts.get('UNKNOWN', 0)} `UNKNOWN`; "
    f"static {static_counts.get('TARGET_AFFECTED', 0)} `TARGET_AFFECTED`, {static_counts.get('TARGET_NOT_AFFECTED', 0)} `TARGET_NOT_AFFECTED`, {static_counts.get('TARGET_PATH_ABSENT', 0)} `TARGET_PATH_ABSENT`, {static_counts.get('STATIC_INCONCLUSIVE', 0)} `STATIC_INCONCLUSIVE`; "
    f"runtime {counts_runtime.get('NOT_APPLICABLE', 0)} `NOT_APPLICABLE`, {counts_runtime.get('NOT_RUN_REFERENCE_INSUFFICIENT', 0)} `NOT_RUN_REFERENCE_INSUFFICIENT`, {counts_runtime.get('NOT_RUN_INFEASIBLE', 0)} `NOT_RUN_INFEASIBLE`.\n",
    decision,
    flags=re.S,
)
decision_path.write_text(decision, encoding='utf-8')

json_path = ROOT / 'source-registry.json.gz'
json_data = json.loads(gzip.decompress(json_path.read_bytes()).decode('utf-8'))
if isinstance(json_data, list):
    json_rows = json_data
elif isinstance(json_data, dict):
    list_key = next(k for k in ('records', 'items', 'sources') if isinstance(json_data.get(k), list))
    json_rows = json_data[list_key]
else:
    raise SystemExit('unsupported JSON registry shape')
for row in json_rows:
    key = row.get('canonical_key') or row.get('item_key') or row.get('key')
    if key in record_by_key:
        row.update({k: record_by_key[key][k] for k in ('plan_status', 'runtime_conclusion', 'execution_status')})
json_raw = (json.dumps(json_data, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode('utf-8')
json_path.write_bytes(gzip.compress(json_raw, compresslevel=9, mtime=0))

csv_path = ROOT / 'source-registry.csv.gz'
csv_text = gzip.decompress(csv_path.read_bytes()).decode('utf-8')
reader = csv.DictReader(io.StringIO(csv_text))
csv_rows = list(reader)
fieldnames = list(reader.fieldnames or [])
for field in ('plan_status', 'runtime_conclusion', 'execution_status'):
    if field not in fieldnames:
        fieldnames.append(field)
for row in csv_rows:
    key = row.get('canonical_key') or row.get('item_key') or row.get('key')
    if key in record_by_key:
        row.update({k: record_by_key[key][k] for k in ('plan_status', 'runtime_conclusion', 'execution_status')})
buf = io.StringIO(newline='')
writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator='\n')
writer.writeheader()
writer.writerows(csv_rows)
csv_path.write_bytes(gzip.compress(buf.getvalue().encode('utf-8'), compresslevel=9, mtime=0))

(ROOT / 'runtime-feasibility.md').write_text(feasibility_doc(), encoding='utf-8')
print('finalized', dict(counts_plan), dict(counts_runtime))
