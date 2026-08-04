#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import io
import json
import re
import sys
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError as exc:
    raise SystemExit('PyYAML is required') from exc

ROOT = Path('docs/agents/evidence/OTERYN-20260804-external-truth-source-enrichment')
SCOPE = ROOT / 'canonical-scope.json'
DOSSIERS = ROOT / 'dossiers'
MATRICES = [
    ROOT / 'expected-behavior-matrix.md',
    ROOT / 'reproduction-matrix.md',
    ROOT / 'decision-matrix.md',
]
REQUIRED_HEADINGS = [
    '## Identity',
    '## Source claim',
    '## Expected behavior',
    '## Five-repository static comparison',
    '## Deterministic runtime plan',
    '## Runtime execution',
    '## Conclusions',
    '## Drift and unresolved questions',
]
ENUMS = {
    'truth_status': {'PROVEN', 'PARTIALLY_PROVEN', 'CONTRADICTED', 'UNKNOWN'},
    'static_conclusion': {'TARGET_AFFECTED', 'TARGET_NOT_AFFECTED', 'TARGET_PATH_ABSENT', 'STATIC_INCONCLUSIVE'},
    'runtime_conclusion': {'REPRODUCED', 'NOT_REPRODUCED', 'NOT_APPLICABLE', 'NOT_RUN_UNSAFE', 'NOT_RUN_INFEASIBLE', 'NOT_RUN_REFERENCE_INSUFFICIENT', 'PENDING'},
    'owner_action': {'OPEN_FIX_PROGRAM', 'OPEN_ARCHITECTURE_DECISION', 'OPEN_PROTOCOL_DECISION', 'OPEN_PERSISTENCE_DECISION', 'NO_ACTION', 'RESEARCH_REQUIRED'},
    'plan_status': {'READY', 'NOT_APPLICABLE', 'BLOCKED_REFERENCE', 'BLOCKED_UNSAFE', 'BLOCKED_INFEASIBLE'},
    'execution_status': {'NOT_RUN', 'PASS', 'FAIL', 'BLOCKED'},
}

errors: list[str] = []
warnings: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def yaml_blocks(text: str, path: Path) -> list[dict]:
    out = []
    for idx, raw in enumerate(re.findall(r'```yaml\n(.*?)\n```', text, flags=re.S), start=1):
        try:
            obj = yaml.safe_load(raw)
        except Exception as exc:
            fail(f'{path}: YAML block {idx} does not parse: {exc}')
            continue
        if not isinstance(obj, dict):
            fail(f'{path}: YAML block {idx} is not a mapping')
            continue
        out.append(obj)
    return out


def key_to_filename(key: str) -> str:
    repo, number = key.split('#', 1)
    return repo.replace('/', '-') + '-' + number + '.md'

scope = json.loads(SCOPE.read_text(encoding='utf-8'))
items = scope.get('items', [])
keys = [x.get('canonical_key') for x in items]
keyset = set(keys)
if len(items) != 60:
    fail(f'canonical scope row count {len(items)} != 60')
if len(keyset) != 60:
    fail(f'canonical scope unique key count {len(keyset)} != 60')
if Counter(x.get('prior_bucket') for x in items) != Counter({'REPRO': 49, 'INSUFFICIENT': 11}):
    fail(f'canonical bucket counts mismatch: {Counter(x.get("prior_bucket") for x in items)}')
if scope.get('counts') != {'total': 60, 'REPRO': 49, 'INSUFFICIENT': 11}:
    fail(f'canonical counts object mismatch: {scope.get("counts")}')

expected_files = {key_to_filename(k) for k in keyset}
actual_files = {p.name for p in DOSSIERS.glob('*.md')}
for missing in sorted(expected_files - actual_files):
    fail(f'missing dossier: {missing}')
for extra in sorted(actual_files - expected_files):
    fail(f'extra dossier: {extra}')

conclusions: list[dict] = []
plans: list[dict] = []
executions: list[dict] = []
identity_by_key: dict[str, dict] = {}

for item in items:
    key = item['canonical_key']
    path = DOSSIERS / key_to_filename(key)
    if not path.exists():
        continue
    text = path.read_text(encoding='utf-8')
    for heading in REQUIRED_HEADINGS:
        if heading not in text:
            fail(f'{path}: missing heading {heading}')
    blocks = yaml_blocks(text, path)
    identities = [b for b in blocks if 'canonical_key' in b]
    if len(identities) != 1:
        fail(f'{path}: expected one identity block, found {len(identities)}')
        continue
    ident = identities[0]
    identity_by_key[key] = ident
    if ident.get('canonical_key') != key:
        fail(f'{path}: canonical_key {ident.get("canonical_key")} != {key}')
    if ident.get('research_status') != 'COMPLETE':
        fail(f'{path}: research_status is not COMPLETE')
    for field in ('predecessor_row', 'source_type', 'prior_bucket', 'prior_truth_status', 'family'):
        if field not in ident:
            fail(f'{path}: missing identity field {field}')
    if ident.get('predecessor_row') != item.get('predecessor_row'):
        fail(f'{path}: predecessor row mismatch')
    if ident.get('source_type') != item.get('item_type'):
        fail(f'{path}: source type mismatch')
    if ident.get('prior_bucket') != item.get('prior_bucket'):
        fail(f'{path}: prior bucket mismatch')
    if 'PLACEHOLDER' in text or '<owner/repo#number>' in text or '<one testable statement>' in text:
        fail(f'{path}: unresolved template placeholder')
    tables = [line for line in text.splitlines() if line.startswith('|')]
    repo_aliases = {
        'opentibiabr/canary': ('opentibiabr/canary', 'upstream Canary'),
        'zimbadev/crystalserver': ('zimbadev/crystalserver', 'CrystalServer'),
        'blakinio/canary': ('blakinio/canary',),
        'blakinio/Otheryn': ('blakinio/Otheryn', 'Otheryn'),
        'blakinio/otclient': ('blakinio/otclient', 'OTClient'),
    }
    for repo_name, aliases in repo_aliases.items():
        if not any(any(alias in line for alias in aliases) for line in tables):
            fail(f'{path}: five-repository table missing {repo_name}')
    cands = [b for b in blocks if 'truth_status' in b]
    if len(cands) != 1:
        fail(f'{path}: expected one conclusions block, found {len(cands)}')
    else:
        c = {'canonical_key': key, **cands[0]}
        conclusions.append(c)
        for field in ('truth_status', 'static_conclusion', 'runtime_conclusion', 'owner_action', 'confidence', 'rationale'):
            if field not in c:
                fail(f'{path}: missing conclusion field {field}')
        for field, allowed in ENUMS.items():
            if field in c and c[field] not in allowed:
                fail(f'{path}: invalid {field}={c[field]}')
    pcands = [b for b in blocks if 'plan_status' in b]
    if len(pcands) != 1:
        fail(f'{path}: expected one runtime plan block, found {len(pcands)}')
    else:
        p = {'canonical_key': key, **pcands[0]}
        plans.append(p)
        if p.get('plan_status') not in ENUMS['plan_status']:
            fail(f'{path}: invalid plan_status={p.get("plan_status")}')
        safety = p.get('safety')
        if not isinstance(safety, dict) or any(safety.get(k) is not False for k in ('production_access', 'persistent_live_state', 'external_side_effects')):
            fail(f'{path}: runtime safety must explicitly be false for all three dimensions')
    ecands = [b for b in blocks if 'execution_status' in b]
    if len(ecands) != 1:
        fail(f'{path}: expected one execution block, found {len(ecands)}')
    else:
        e = {'canonical_key': key, **ecands[0]}
        executions.append(e)
        if e.get('execution_status') not in ENUMS['execution_status']:
            fail(f'{path}: invalid execution_status={e.get("execution_status")}')

if len(conclusions) != 60:
    fail(f'parsed conclusions {len(conclusions)} != 60')
if len(plans) != 60:
    fail(f'parsed plans {len(plans)} != 60')
if len(executions) != 60:
    fail(f'parsed executions {len(executions)} != 60')

for matrix in MATRICES:
    text = matrix.read_text(encoding='utf-8')
    row_keys = []
    for line in text.splitlines():
        if not line.startswith('|'):
            continue
        row_keys.extend(re.findall(r'(?:opentibiabr/canary|zimbadev/crystalserver)#\d+', line))
    counts = Counter(row_keys)
    if set(row_keys) != keyset:
        missing = sorted(keyset - set(row_keys))
        extra = sorted(set(row_keys) - keyset)
        fail(f'{matrix}: key set mismatch missing={missing} extra={extra}')
    dups = sorted(k for k, v in counts.items() if v != 1)
    if dups:
        fail(f'{matrix}: duplicate/non-single rows {dups}')
    if len(row_keys) != 60:
        fail(f'{matrix}: row count {len(row_keys)} != 60')


def registry_records_json(path: Path) -> list[dict]:
    data = json.loads(gzip.decompress(path.read_bytes()).decode('utf-8'))
    if isinstance(data, list):
        return data
    for name in ('records', 'items', 'sources'):
        if isinstance(data, dict) and isinstance(data.get(name), list):
            return data[name]
    raise ValueError('no record list found')


def registry_key(row: dict) -> str | None:
    for name in ('canonical_key', 'item_key', 'key'):
        if row.get(name):
            return str(row[name])
    return None

try:
    json_rows = registry_records_json(ROOT / 'source-registry.json.gz')
    json_keys = [registry_key(x) for x in json_rows]
    if len(json_rows) != 60 or set(json_keys) != keyset or len(set(json_keys)) != 60:
        fail(f'JSON registry mismatch rows={len(json_rows)} unique={len(set(json_keys))}')
except Exception as exc:
    fail(f'JSON registry invalid: {exc}')

try:
    csv_text = gzip.decompress((ROOT / 'source-registry.csv.gz').read_bytes()).decode('utf-8')
    csv_rows = list(csv.DictReader(io.StringIO(csv_text)))
    csv_keys = [registry_key(x) for x in csv_rows]
    if len(csv_rows) != 60 or set(csv_keys) != keyset or len(set(csv_keys)) != 60:
        fail(f'CSV registry mismatch rows={len(csv_rows)} unique={len(set(csv_keys))}')
except Exception as exc:
    fail(f'CSV registry invalid: {exc}')

truth = Counter(c.get('truth_status') for c in conclusions)
static = Counter(c.get('static_conclusion') for c in conclusions)
runtime = Counter(c.get('runtime_conclusion') for c in conclusions)
actions = Counter(c.get('owner_action') for c in conclusions)
plan_counts = Counter(p.get('plan_status') for p in plans)
execution_counts = Counter(e.get('execution_status') for e in executions)

report = {
    'status': 'PASS' if not errors else 'FAIL',
    'scope': {'rows': len(items), 'unique_keys': len(keyset), 'buckets': dict(Counter(x.get('prior_bucket') for x in items))},
    'dossiers': {'expected': len(expected_files), 'actual': len(actual_files), 'parsed_conclusions': len(conclusions)},
    'matrices': {p.name: 60 for p in MATRICES},
    'truth_status': dict(sorted(truth.items())),
    'static_conclusion': dict(sorted(static.items())),
    'runtime_conclusion': dict(sorted(runtime.items())),
    'owner_action': dict(sorted(actions.items())),
    'plan_status': dict(sorted(plan_counts.items())),
    'execution_status': dict(sorted(execution_counts.items())),
    'errors': errors,
    'warnings': warnings,
}
Path('validation.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
lines = [
    f"STATUS: {report['status']}",
    f"SCOPE: {len(items)} rows / {len(keyset)} unique / {dict(Counter(x.get('prior_bucket') for x in items))}",
    f"DOSSIERS: {len(actual_files)}/60",
    f"TRUTH: {dict(sorted(truth.items()))}",
    f"STATIC: {dict(sorted(static.items()))}",
    f"RUNTIME: {dict(sorted(runtime.items()))}",
    f"PLANS: {dict(sorted(plan_counts.items()))}",
    f"EXECUTIONS: {dict(sorted(execution_counts.items()))}",
    f"OWNER_ACTIONS: {dict(sorted(actions.items()))}",
]
if errors:
    lines.append('ERRORS:')
    lines.extend(f'- {e}' for e in errors)
else:
    lines.append('ERRORS: none')
Path('validation.txt').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
sys.exit(1 if errors else 0)
