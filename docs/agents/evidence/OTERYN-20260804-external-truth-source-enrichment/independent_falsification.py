#!/usr/bin/env python3
from __future__ import annotations

import csv
import gzip
import io
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path('docs/agents/evidence/OTERYN-20260804-external-truth-source-enrichment')
DOSSIERS = ROOT / 'dossiers'
EXPECTED_TRUTH = Counter({'PROVEN': 31, 'PARTIALLY_PROVEN': 24, 'UNKNOWN': 5})
EXPECTED_STATIC = Counter({'STATIC_INCONCLUSIVE': 47, 'TARGET_AFFECTED': 9, 'TARGET_NOT_AFFECTED': 2, 'TARGET_PATH_ABSENT': 2})
EXPECTED_RUNTIME = Counter({'NOT_RUN_INFEASIBLE': 42, 'NOT_APPLICABLE': 13, 'NOT_RUN_REFERENCE_INSUFFICIENT': 5})
EXPECTED_ACTIONS = Counter({'RESEARCH_REQUIRED': 45, 'OPEN_FIX_PROGRAM': 8, 'OPEN_ARCHITECTURE_DECISION': 3, 'NO_ACTION': 2, 'OPEN_PROTOCOL_DECISION': 2})
EXPECTED_PLANS = Counter({'BLOCKED_INFEASIBLE': 42, 'NOT_APPLICABLE': 13, 'BLOCKED_REFERENCE': 5})
EXPECTED_EXECUTIONS = Counter({'BLOCKED': 47, 'NOT_RUN': 13})
ALLOWED_PREFIXES = (
    'docs/agents/evidence/OTERYN-20260804-external-truth-source-enrichment/',
    'docs/agents/tasks/active/OTERYN-20260804-external-truth-source-enrichment.md',
    '.github/workflows/external-truth-source-evidence.yml',
    '.github/workflows/external-truth-runtime-finalize.yml',
    '.github/workflows/external-truth-independent-audit.yml',
)

findings: list[str] = []


def finding(text: str) -> None:
    findings.append(text)


def blocks(text: str) -> list[dict]:
    out = []
    for raw in re.findall(r'```yaml\n(.*?)\n```', text, re.S):
        try:
            obj = yaml.safe_load(raw)
        except Exception as exc:
            finding(f'YAML parse failure: {exc}')
            continue
        if isinstance(obj, dict):
            out.append(obj)
    return out


scope = json.loads((ROOT / 'canonical-scope.json').read_text(encoding='utf-8'))
items = scope.get('items') or []
keys = [row.get('canonical_key') for row in items]
keyset = set(keys)
if len(items) != 60 or len(keyset) != 60:
    finding(f'canonical scope mismatch rows={len(items)} unique={len(keyset)}')
if Counter(row.get('prior_bucket') for row in items) != Counter({'REPRO': 49, 'INSUFFICIENT': 11}):
    finding('predecessor bucket totals do not equal 49 REPRO + 11 INSUFFICIENT')

truth = Counter()
static = Counter()
runtime = Counter()
actions = Counter()
plans = Counter()
executions = Counter()
dossier_keys = []
for path in sorted(DOSSIERS.glob('*.md')):
    text = path.read_text(encoding='utf-8')
    bs = blocks(text)
    ids = [b for b in bs if 'canonical_key' in b]
    cs = [b for b in bs if 'truth_status' in b]
    ps = [b for b in bs if 'plan_status' in b]
    es = [b for b in bs if 'execution_status' in b]
    if len(ids) != 1 or len(cs) != 1 or len(ps) != 1 or len(es) != 1:
        finding(f'{path.name}: expected one identity/conclusion/plan/execution block, got {len(ids)}/{len(cs)}/{len(ps)}/{len(es)}')
        continue
    key = ids[0]['canonical_key']
    dossier_keys.append(key)
    c, p, e = cs[0], ps[0], es[0]
    truth[c.get('truth_status')] += 1
    static[c.get('static_conclusion')] += 1
    runtime[c.get('runtime_conclusion')] += 1
    actions[c.get('owner_action')] += 1
    plans[p.get('plan_status')] += 1
    executions[e.get('execution_status')] += 1
    if c.get('static_conclusion') != 'STATIC_INCONCLUSIVE' and c.get('runtime_conclusion') != 'NOT_APPLICABLE':
        finding(f'{key}: statically decisive row is not runtime NOT_APPLICABLE')
    if p.get('plan_status') == 'BLOCKED_REFERENCE' and c.get('runtime_conclusion') != 'NOT_RUN_REFERENCE_INSUFFICIENT':
        finding(f'{key}: reference-blocked plan has inconsistent runtime conclusion')
    if p.get('plan_status') == 'BLOCKED_INFEASIBLE' and c.get('runtime_conclusion') != 'NOT_RUN_INFEASIBLE':
        finding(f'{key}: infrastructure-blocked plan has inconsistent runtime conclusion')
    safety = p.get('safety')
    if not isinstance(safety, dict) or any(safety.get(name) is not False for name in ('production_access', 'persistent_live_state', 'external_side_effects')):
        finding(f'{key}: safety boundary is not explicitly all-false')
    if e.get('run_ids') not in ([], None):
        finding(f'{key}: unexpected runtime run IDs recorded despite zero canonical gameplay executions')

if len(dossier_keys) != 60 or set(dossier_keys) != keyset:
    finding(f'dossier identity mismatch rows={len(dossier_keys)} unique={len(set(dossier_keys))}')
for label, actual, expected in (
    ('truth', truth, EXPECTED_TRUTH),
    ('static', static, EXPECTED_STATIC),
    ('runtime', runtime, EXPECTED_RUNTIME),
    ('owner actions', actions, EXPECTED_ACTIONS),
    ('plans', plans, EXPECTED_PLANS),
    ('executions', executions, EXPECTED_EXECUTIONS),
):
    if actual != expected:
        finding(f'{label} counters mismatch actual={dict(actual)} expected={dict(expected)}')

for matrix_name in ('expected-behavior-matrix.md', 'reproduction-matrix.md', 'decision-matrix.md'):
    text = (ROOT / matrix_name).read_text(encoding='utf-8')
    found = re.findall(r'(?:opentibiabr/canary|zimbadev/crystalserver)#\d+', text)
    counts = Counter(found)
    if set(found) != keyset or len(found) != 60 or any(value != 1 for value in counts.values()):
        finding(f'{matrix_name}: canonical identity equality failed rows={len(found)} unique={len(set(found))}')

for registry_name, kind in (('source-registry.json.gz', 'json'), ('source-registry.csv.gz', 'csv')):
    raw = gzip.decompress((ROOT / registry_name).read_bytes()).decode('utf-8')
    if kind == 'json':
        data = json.loads(raw)
        if isinstance(data, list):
            rows = data
        else:
            rows = next(data[name] for name in ('records', 'items', 'sources') if isinstance(data.get(name), list))
    else:
        rows = list(csv.DictReader(io.StringIO(raw)))
    registry_keys = [row.get('canonical_key') or row.get('item_key') or row.get('key') for row in rows]
    if len(rows) != 60 or set(registry_keys) != keyset or len(set(registry_keys)) != 60:
        finding(f'{registry_name}: key equality failed rows={len(rows)} unique={len(set(registry_keys))}')
    for row in rows:
        key = row.get('canonical_key') or row.get('item_key') or row.get('key')
        if key in keyset and row.get('runtime_conclusion') not in EXPECTED_RUNTIME:
            finding(f'{registry_name}: {key} has invalid or stale runtime conclusion {row.get("runtime_conclusion")}')

changed = subprocess.check_output(['git', 'diff', '--name-only', 'origin/main...HEAD'], text=True).splitlines()
unexpected = [path for path in changed if not path.startswith(ALLOWED_PREFIXES)]
if unexpected:
    finding(f'out-of-scope changed paths: {unexpected}')
if any(path.startswith(('src/', 'data/', 'data-otservbr-global/', 'schema.sql', 'config.lua')) for path in changed):
    finding('product/runtime path changed in an audit-only task')

feasibility = (ROOT / 'runtime-feasibility.md').read_text(encoding='utf-8')
for marker in ('13 `NOT_APPLICABLE`', '5 `NOT_RUN_REFERENCE_INSUFFICIENT`', '42 `NOT_RUN_INFEASIBLE`', 'runtime scenarios started: 0'):
    if marker not in feasibility:
        finding(f'runtime-feasibility.md missing marker: {marker}')

status = 'PASS' if not findings else 'FAIL'
lines = [
    '# Independent falsification — external truth-source enrichment',
    '',
    f'Status: **{status}**',
    '',
    'This review uses a separate parser and invariant set from `validate_evidence.py`. It attempts to falsify canonical identity, item counters, runtime-disposition logic, registry equality, path authority and the zero-runtime-execution claim.',
    '',
    '## Results',
    '',
    f'- canonical scope: {len(items)} rows / {len(keyset)} unique keys / 49 `REPRO` + 11 `INSUFFICIENT`;',
    f'- dossiers: {len(dossier_keys)} rows / {len(set(dossier_keys))} unique keys;',
    f'- truth: {dict(sorted(truth.items()))};',
    f'- static: {dict(sorted(static.items()))};',
    f'- runtime: {dict(sorted(runtime.items()))};',
    f'- owner actions: {dict(sorted(actions.items()))};',
    f'- plans: {dict(sorted(plans.items()))};',
    f'- executions: {dict(sorted(executions.items()))};',
    f'- changed paths reviewed: {len(changed)}; product/runtime paths: 0;',
    '- matrices and both compressed registries: exact 60-key equality checked;',
    '- runtime feasibility claim: checked against item-level conclusion/plan/execution consistency.',
    '',
    '## Material findings',
    '',
]
if findings:
    lines.extend(f'- {item}' for item in findings)
else:
    lines.append('- none; open material findings: **0**.')
lines.extend([
    '',
    '## Non-claims',
    '',
    '- This audit does not claim that any of the 42 gameplay/client scenarios was executed.',
    '- It does not authorize product fixes or a reusable gameplay E2E harness.',
    '- `NOT_RUN_INFEASIBLE` is an exact repository-capability/authority conclusion, not evidence that the reported behavior is absent.',
])
(ROOT / 'independent-audit.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
(ROOT / 'independent-audit.json').write_text(json.dumps({
    'status': status,
    'material_findings_open': len(findings),
    'findings': findings,
    'scope_rows': len(items),
    'unique_keys': len(keyset),
    'truth': dict(sorted(truth.items())),
    'static': dict(sorted(static.items())),
    'runtime': dict(sorted(runtime.items())),
    'owner_actions': dict(sorted(actions.items())),
    'plans': dict(sorted(plans.items())),
    'executions': dict(sorted(executions.items())),
    'changed_paths': changed,
}, indent=2, sort_keys=True) + '\n', encoding='utf-8')
print(status)
if findings:
    print('\n'.join(findings))
sys.exit(1 if findings else 0)
