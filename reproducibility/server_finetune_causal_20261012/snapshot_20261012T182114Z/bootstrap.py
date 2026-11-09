"""Verify task payload, then start detached server-owned experiment units."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PYTHON = '/home/yagr/anaconda3/bin/python'
ENV = {
    'PYTHONPATH': '/home/yagr/coma_revision_v12_20261011/deps:/home/yagr/anaconda3/lib/python3.12/site-packages:/home/yagr/.local/lib/python3.12/site-packages',
    'HF_HOME': '/home/yagr/coma_revision_v12_20261011/runtime/hf',
    'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
    'OMP_NUM_THREADS': '2', 'OPENBLAS_NUM_THREADS': '2', 'MKL_NUM_THREADS': '2',
    'TOKENIZERS_PARALLELISM': 'false', 'PYTHONUNBUFFERED': '1',
    'CUBLAS_WORKSPACE_CONFIG': ':4096:8',
}


def main():
    expected = json.loads((ROOT / 'expected_inputs.json').read_text())
    for name, checksum in expected.items():
        path = ROOT / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == checksum, name
    assert subprocess.check_output(['loginctl', 'show-user', 'yagr', '-p', 'Linger'], text=True).strip() == 'Linger=yes'
    (ROOT / 'logs').mkdir(exist_ok=True)
    clean_env = dict(os.environ)
    for key in list(clean_env):
        if key in ['OPENAI_API_KEY', 'OPENROUTER_API_KEY', 'ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY']:
            del clean_env[key]
    smoke_env = dict(clean_env, **ENV)
    print(subprocess.check_output([PYTHON, '-s', '-c',
          'import torch,numpy,pandas,transformers,catboost; print(torch.__version__,numpy.__version__,pandas.__version__,transformers.__version__,catboost.__version__)'],
          env=smoke_env, text=True), flush=True)
    print(subprocess.check_output(['df', '-h', str(ROOT)], text=True), flush=True)
    if '--smoke' in sys.argv:
        subprocess.run([PYTHON, '-s', str(ROOT / 'run_experiments.py'), 'direct', '--smoke'],
                       env=smoke_env, check=True)
        subprocess.run([PYTHON, '-s', str(ROOT / 'run_experiments.py'), 'ablation-vectors', '--smoke'],
                       env=smoke_env, check=True)
        return
    configurations = [('direct0', 'direct', 0, 2), ('direct1', 'direct', 1, 2),
                      ('vectors', 'ablation-vectors', 0, 1),
                      ('decode0', 'ablation-decode', 0, 2), ('decode1', 'ablation-decode', 1, 2)]
    records = []
    for name, action, worker, workers in configurations:
        unit = 'coma-ftcausal-20261012-' + name
        argv = ['systemd-run', '--user', '--collect', '--unit', unit,
                '--property', 'WorkingDirectory=' + str(ROOT),
                '--property', 'StandardOutput=append:' + str(ROOT / 'logs' / (name + '.log')),
                '--property', 'StandardError=append:' + str(ROOT / 'logs' / (name + '.log'))]
        for key, value in ENV.items():
            argv += ['--setenv', key + '=' + value]
        argv += [PYTHON, '-s', str(ROOT / 'run_experiments.py'), action,
                 '--worker', str(worker), '--workers', str(workers)]
        subprocess.run(argv, env=clean_env, check=True)
        records.append(dict(unit=unit, action=action, worker=worker, workers=workers))
    (ROOT / 'LAUNCH.json').write_text(json.dumps(dict(units=records, detached_from_Mac=True,
              direct_fits=363, ablation_fits=1331, expected_inputs_checked=len(expected)), indent=2))
    print(json.dumps(records, indent=2))


if __name__ == '__main__':
    main()
