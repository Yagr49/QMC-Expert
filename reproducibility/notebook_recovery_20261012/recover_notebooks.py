"""Recover dated research notebooks without executing them or retaining API keys."""
import csv
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote, urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
HISTORY = Path('/Users/egorilin/Library/Application Support/Code/User/History')
TZ = ZoneInfo('Europe/Moscow')
SECRET = re.compile(r'sk-[A-Za-z0-9_-]{12,}|ghp_[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{12,}')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def sanitize(value, counter):
    if isinstance(value, str):
        cleaned, n = SECRET.subn('[REDACTED_API_KEY]', value)
        counter[0] += n
        return cleaned
    if isinstance(value, list):
        return [sanitize(x, counter) for x in value]
    if isinstance(value, dict):
        return {k: sanitize(v, counter) for k, v in value.items()}
    return value


def recover(source, dest, original_resource, date, date_kind):
    raw = source.read_bytes()
    notebook = json.loads(raw)
    counter = [0]
    clean = sanitize(notebook, counter)
    if counter[0]:
        data = (json.dumps(clean, ensure_ascii=False, indent=1) + '\n').encode()
    else:
        data = raw
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    outputs = []
    for i, cell in enumerate(clean.get('cells', [])):
        for output in cell.get('outputs', []):
            t = output.get('text', '')
            t = ''.join(t) if isinstance(t, list) else t
            v = output.get('data', {}).get('text/plain', '')
            t += ''.join(v) if isinstance(v, list) else str(v)
            if re.search(r'RMSE|R²|\bR2\b|CKA|\bATE\b', t):
                outputs.append({'cell_index_zero_based': i, 'text': t})
    return {
        'original_resource': original_resource,
        'source': str(source),
        'recovered_file': str(dest.relative_to(ROOT)),
        'date_moscow': date.isoformat(timespec='seconds'),
        'date_kind': date_kind,
        'source_sha256': sha(raw),
        'recovered_sha256': sha(data),
        'api_key_occurrences_redacted': counter[0],
        'cells': len(clean.get('cells', [])),
        'cells_with_outputs': sum(bool(c.get('outputs')) for c in clean.get('cells', [])),
        'metric_outputs': outputs,
    }


def main():
    rows, latest = [], {}
    for entries in sorted(HISTORY.glob('*/entries.json')):
        meta = json.loads(entries.read_text())
        resource = meta.get('resource', '')
        path = unquote(urlparse(resource).path)
        if '/Desktop/COMA/' not in path or not path.endswith('.ipynb'):
            continue
        for entry in meta.get('entries', []):
            date = datetime.fromtimestamp(entry['timestamp'] / 1000, TZ)
            source = entries.parent / entry['id']
            if date.year != 2026 or date.month not in (4, 5) or not source.exists():
                continue
            name = Path(path).name
            stamp = date.strftime('%Y-%m-%d_%H-%M-%S')
            dest = ROOT / 'history' / Path(name).stem / (stamp + '_' + entry['id'])
            row = recover(source, dest, path, date, 'VS Code save timestamp')
            rows.append(row)
            if name not in latest or date > latest[name][0]:
                latest[name] = (date, source, path)

    primary = []
    for name, (date, source, path) in sorted(latest.items()):
        dest = ROOT / 'notebooks' / (date.strftime('%Y-%m-%d') + '_' + name)
        row = recover(source, dest, path, date, 'VS Code save timestamp')
        primary.append(row)

    additional = [
        Path('/Users/egorilin/Desktop/COMA/descriptor_multitask_cell6_style.ipynb'),
        Path('/Users/egorilin/Desktop/COMA/create_embeddings_for_test_by_multiregression.ipynb'),
        Path('/Users/egorilin/Downloads/emb_decomposition.ipynb'),
        Path('/Users/egorilin/Desktop/Veresh_paper/shap_causal_analysis.ipynb'),
        Path('/Users/egorilin/Desktop/Veresh_paper/shap_causal_analysis-2.ipynb'),
    ]
    for source in additional:
        date = datetime.fromtimestamp(source.stat().st_mtime, TZ)
        dest = ROOT / 'additional' / (date.strftime('%Y-%m-%d') + '_' + source.name)
        primary.append(recover(source, dest, str(source), date, 'filesystem modification timestamp'))

    manifest = {'recovered_on_moscow_date': '2026-10-12',
                'note': 'Files were recovered without execution. VS Code dates are save dates, not execution dates. API keys are redacted where present. Later July support notebooks are separately labelled.',
                'history_snapshots': rows, 'selected_notebooks': primary}
    (ROOT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    with (ROOT / 'inventory.csv').open('w', newline='') as f:
        fields = ['date_moscow', 'date_kind', 'original_resource', 'source', 'recovered_file',
                  'cells', 'cells_with_outputs', 'source_sha256', 'recovered_sha256', 'api_key_occurrences_redacted']
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows + primary)
    (ROOT / 'metric_outputs.json').write_text(json.dumps(
        [{'notebook': r['recovered_file'], 'date_moscow': r['date_moscow'], 'outputs': r['metric_outputs']}
         for r in primary], ensure_ascii=False, indent=2) + '\n')
    validation = {'history_snapshots': len(rows), 'selected_notebooks': len(primary),
                  'valid_notebook_json': True, 'unredacted_detected_api_keys': 0}
    for row in rows + primary:
        p = ROOT / row['recovered_file']
        raw = p.read_bytes()
        obj = json.loads(raw)
        assert obj.get('nbformat') == 4
        assert sha(raw) == row['recovered_sha256']
        assert not SECRET.search(raw.decode())
    (ROOT / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
    print(json.dumps(validation))
    for row in primary:
        print(row['date_moscow'], row['recovered_file'], 'output_cells=' + str(row['cells_with_outputs']))


if __name__ == '__main__':
    main()
