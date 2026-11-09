"""Reuse read-only archives; write all new outputs in this run directory."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent
OLD = Path('/home/yagr')


def link(destination, source):
    assert source.exists(), source
    if not destination.exists():
        destination.symlink_to(source, target_is_directory=source.is_dir())


def main():
    v10 = OLD / 'coma_revision_v10_20261011'
    v12 = OLD / 'coma_revision_v12_20261011'
    v14 = OLD / 'coma_revision_v14_20261011'
    link(ROOT / 'core_frozen/data', v10 / 'data')
    for item in ('data', 'deps', 'runtime'):
        link(ROOT / 'core_ft' / item, v12 / item)
    for item in ('data', 'representations'):
        link(ROOT / 'core_v14' / item, v14 / item)
    for name in ('data', 'representations'):
        (ROOT / 'retrained_v14' / name).mkdir(exist_ok=True)
    for src in (v14 / 'data').iterdir():
        if src.is_file():
            shutil.copyfile(src, ROOT / 'retrained_v14/data' / src.name)
    (ROOT / 'status').mkdir(exist_ok=True)
    hashes = {}
    for directory in (v10 / 'data', v12 / 'data', v14 / 'data', v14 / 'representations'):
        for p in directory.iterdir():
            if p.is_file():
                hashes[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
    expected = json.loads((ROOT / 'expected_inputs.json').read_text())
    for path, expected_hash in expected.items():
        if hashes.get(path) != expected_hash:
            raise RuntimeError(('input differs from local archive', path))
    (ROOT / 'status/inputs_verified.json').write_text(json.dumps(hashes, indent=2))
    print('Verified', len(expected), 'local/archive hashes; reused', len(hashes), 'files')


if __name__ == '__main__':
    main()
