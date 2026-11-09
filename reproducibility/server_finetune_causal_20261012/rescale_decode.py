"""Resume identical decoder fits in four disjoint partitions on the 16-CPU host."""
from pathlib import Path
import datetime as dt
import json
import os
import subprocess
from bootstrap import ENV, PYTHON

ROOT = Path(__file__).resolve().parent
clean = dict(os.environ)
for key in ['OPENAI_API_KEY', 'OPENROUTER_API_KEY', 'ANTHROPIC_API_KEY', 'MOONSHOT_API_KEY']:
    clean.pop(key, None)
old = ['coma-ftcausal-20261012-decode' + str(i) for i in range(2)]
subprocess.run(['systemctl', '--user', 'stop'] + old, check=True, env=clean)
records = []
for worker in range(4):
    name = 'decode' + str(worker)
    unit = 'coma-ftcausal-20261012-' + name
    args = ['systemd-run', '--user', '--collect', '--unit', unit,
            '--property', 'WorkingDirectory=' + str(ROOT),
            '--property', 'StandardOutput=append:' + str(ROOT / 'logs' / (name + '.log')),
            '--property', 'StandardError=append:' + str(ROOT / 'logs' / (name + '.log'))]
    for key, value in ENV.items():
        args += ['--setenv', key + '=' + value]
    args += [PYTHON, '-s', str(ROOT / 'run_experiments.py'), 'ablation-decode',
             '--worker', str(worker), '--workers', '4']
    subprocess.run(args, check=True, env=clean)
    records.append(dict(unit=unit, worker=worker, workers=4))
(ROOT / 'DECODER_RESCALE.json').write_text(json.dumps(dict(
    time_utc=dt.datetime.now(dt.timezone.utc).isoformat(), units=records,
    completed_chunks_reused=True, experiment_hyperparameters_unchanged=True), indent=2))
print(json.dumps(records))
